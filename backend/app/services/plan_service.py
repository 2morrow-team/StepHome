# 최초 Plan / Re-planning 전체 흐름을 연결하는 Backend Service

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from app.ai.planner import (
    generate_action_plan,
    generate_replan_action_plan,
)
from app.ai.prompts import (
    build_ai_input,
    build_replan_ai_input,
)
from app.db.database import InMemoryDatabase
from app.diagnosis.calculator import calculate_diagnosis
from app.policy.rule_engine import match_policies


KST = timezone(timedelta(hours=9))

# 현재 Demo Policy는 6개다.
# match_policies()가 first_match_id + offset 방식으로
# match_id를 생성하므로 MVP에서는 충분한 ID 구간을 미리 확보한다.
#
# 추후 실제 DB를 사용하거나 Policy 수가 크게 늘어나면
# match_id 생성 책임을 DB 계층으로 이동하는 것이 좋다.
_MATCH_ID_BUFFER = 20


# =========================================================
# Utility
# =========================================================


def _dump(
    model: Any,
    *,
    exclude_none: bool = False,
) -> dict[str, Any]:
    """
    Pydantic v1 / v2 모두 지원하도록
    모델을 dict로 변환한다.
    """

    if hasattr(model, "model_dump"):
        return model.model_dump(
            exclude_none=exclude_none,
        )

    return model.dict(
        exclude_none=exclude_none,
    )


def _plain(value: Any) -> Any:
    """
    Enum 등이 포함된 Pydantic 결과를
    일반 Python 값으로 변환한다.
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {
            key: _plain(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _plain(item)
            for item in value
        ]

    return value


# Re-plan 시 변경값이 어느 객체에 속하는지 구분한다.

_USER_FIELDS = {
    "age",
    "employment_status",
    "current_region",
    "personal_monthly_income",
    "total_assets",
    "monthly_savings",
    "housing_status",
    "youth_household_monthly_income",
    "youth_household_size",
    "marital_status",
}

_TARGET_FIELDS = {
    "planned_move_in_date",
    "desired_deposit",
    "desired_monthly_rent",
    "desired_housing_type",
    "desired_region",
}

_USER_FACING_TEXT_REPLACEMENTS = (
    ("planned_move_in_date", "입주 예정일"),
    ("desired_monthly_rent", "희망 월세"),
    ("desired_housing_type", "희망 주거 형태"),
    ("desired_deposit", "희망 보증금"),
    ("desired_region", "희망 지역"),
    ("monthly_savings", "월 저축액"),
    ("total_assets", "총자산"),
    ("personal_monthly_income", "월 소득"),
    ("youth_household_monthly_income", "가구 월소득"),
    ("youth_household_size", "가구원 수"),
    ("employment_status", "고용 상태"),
    ("current_region", "현재 거주 지역"),
    ("housing_status", "주거 상태"),
    ("marital_status", "혼인 상태"),
    ("NEED_MORE_INFO", "추가 확인 필요"),
    ("NOT_ELIGIBLE", "현재 대상 아님"),
    ("CONDITIONAL", "조건 조정 필요"),
    ("AVAILABLE", "신청 가능"),
)


def _sanitize_user_facing_text(text: str) -> str:
    for source, label in _USER_FACING_TEXT_REPLACEMENTS:
        text = text.replace(source, label)
    return text


def _sanitize_ai_output(ai_output: dict[str, Any]) -> dict[str, Any]:
    sanitized = deepcopy(ai_output)
    if isinstance(sanitized.get("summary"), str):
        sanitized["summary"] = _sanitize_user_facing_text(sanitized["summary"])

    for action in sanitized.get("actions", []):
        for field in ("title", "description", "reason"):
            if isinstance(action.get(field), str):
                action[field] = _sanitize_user_facing_text(action[field])

    return sanitized


# =========================================================
# Plan Service
# =========================================================


class PlanService:
    def __init__(
        self,
        database: InMemoryDatabase | None = None,
    ):
        self.database = database or InMemoryDatabase()

    # -----------------------------------------------------
    # 최초 Plan
    # -----------------------------------------------------

    def create_plan(
        self,
        request: Any,
    ) -> dict[str, Any]:
        """
        최초 P0 15개 입력을 기반으로:

        User / Target
        → Diagnosis
        → PolicyMatch
        → AI ActionPlan
        → Final Snapshot

        을 생성한다.
        """

        # ---------------------------------------------
        # 1. ID 생성
        # ---------------------------------------------

        user_id = self.database.next_id("user")
        target_id = self.database.next_id("target")
        diagnosis_id = self.database.next_id("diagnosis")
        plan_id = self.database.next_id("plan")

        # ---------------------------------------------
        # 2. User / Target 변환
        # ---------------------------------------------

        user = _plain(
            _dump(request.user)
        )

        user["user_id"] = user_id

        target = _plain(
            _dump(request.target)
        )

        target["target_id"] = target_id
        target["user_id"] = user_id

        # desired_region은 Frontend 입력값을 그대로 사용한다.
        # Backend에서 별도의 기본 지역을 추가하지 않는다.

        # ---------------------------------------------
        # 3. Diagnosis + PolicyMatch 계산
        # ---------------------------------------------

        diagnosis, matches = self._compute(
            user=user,
            target=target,
            diagnosis_id=diagnosis_id,
        )

        # ---------------------------------------------
        # 4. Backend -> AI Input
        # ---------------------------------------------

        ai_input = build_ai_input(
            user=user,
            target=target,
            diagnosis=diagnosis,
            matched_policies=matches,
        )

        # planner 내부에서 candidate 생성 및
        # validate_action_plan까지 수행한다.
        ai_output = generate_action_plan(
            ai_input
        )

        # ---------------------------------------------
        # 5. Final Snapshot
        # ---------------------------------------------

        snapshot = self._build_snapshot(
            user=user,
            target=target,
            diagnosis=diagnosis,
            matches=matches,
            ai_output=ai_output,
            plan_id=plan_id,
        )

        # ---------------------------------------------
        # 6. 저장
        # ---------------------------------------------

        self.database.save_plan(
            {
                "user_id": user_id,
                "target_id": target_id,
                "plan_id": plan_id,
                "user": user,
                "snapshot": snapshot,
            }
        )

        return snapshot

    # -----------------------------------------------------
    # Re-planning
    # -----------------------------------------------------

    def replan(
        self,
        request: Any,
    ) -> dict[str, Any]:
        """
        기존 Plan의 P0 15개 중 변경된 값을 적용하고:

        Diagnosis 재계산
        → Policy 재판정
        → AI Re-planning
        → 새로운 전체 ActionPlan

        을 생성한다.
        """

        # ---------------------------------------------
        # 1. 이전 Plan 조회
        # ---------------------------------------------

        previous_record = self.database.get_plan(
            request.user_id,
            request.target_id,
            request.previous_plan_id,
        )

        if previous_record is None:
            raise LookupError(
                "이전 플랜을 찾을 수 없습니다."
            )

        previous_snapshot = previous_record[
            "snapshot"
        ]

        if (
            previous_snapshot["diagnosis_id"]
            != request.previous_diagnosis_id
        ):
            raise LookupError(
                "이전 진단 ID가 플랜과 일치하지 않습니다."
            )

        # ---------------------------------------------
        # 2. 이전 User / Target 복사
        # ---------------------------------------------

        current_user = deepcopy(
            previous_record["user"]
        )

        current_target = deepcopy(
            previous_snapshot["target"]
        )

        # ---------------------------------------------
        # 3. 변경값 추출
        # ---------------------------------------------

        changes = _plain(
            _dump(
                request.changes,
                exclude_none=True,
            )
        )

        changed_fields: dict[
            str,
            dict[str, Any],
        ] = {}

        # ---------------------------------------------
        # 4. P0 변경값 적용
        # ---------------------------------------------

        for field, new_value in changes.items():

            # User 필드
            if field in _USER_FIELDS:

                old_value = current_user.get(
                    field
                )

                if old_value != new_value:
                    changed_fields[field] = {
                        "before": old_value,
                        "after": new_value,
                    }

                    current_user[field] = (
                        new_value
                    )

            # Target 필드
            elif field in _TARGET_FIELDS:

                old_value = current_target.get(
                    field
                )

                if old_value != new_value:
                    changed_fields[field] = {
                        "before": old_value,
                        "after": new_value,
                    }

                    current_target[field] = (
                        new_value
                    )

            else:
                raise ValueError(
                    "변경할 수 없는 항목입니다."
                )

        # ---------------------------------------------
        # 5. 새로운 Diagnosis / Plan ID
        # ---------------------------------------------

        diagnosis_id = self.database.next_id(
            "diagnosis"
        )

        plan_id = self.database.next_id(
            "plan"
        )

        # ---------------------------------------------
        # 6. 현재 Diagnosis + PolicyMatch 재계산
        # ---------------------------------------------

        current_diagnosis, current_matches = (
            self._compute(
                user=current_user,
                target=current_target,
                diagnosis_id=diagnosis_id,
            )
        )

        # ---------------------------------------------
        # 7. Re-plan AI Input
        # ---------------------------------------------

        previous_diagnosis = (
            previous_snapshot["diagnosis"]
        )

        previous_policies = (
            previous_snapshot[
                "matched_policies"
            ]
        )

        previous_actions = (
            previous_snapshot[
                "action_plan"
            ]["actions"]
        )

        replan_ai_input = build_replan_ai_input(
            changed_fields=changed_fields,
            previous_diagnosis=previous_diagnosis,
            previous_policies=previous_policies,
            previous_actions=previous_actions,
            current_diagnosis=current_diagnosis,
            current_policies=current_matches,
            current_user=current_user,
            current_target=current_target,
        )

        # ---------------------------------------------
        # 8. AI Re-planning
        # ---------------------------------------------

        ai_output = generate_replan_action_plan(
            replan_ai_input
        )

        # ---------------------------------------------
        # 9. 현재 Snapshot 생성
        # ---------------------------------------------

        current_snapshot = self._build_snapshot(
            user=current_user,
            target=current_target,
            diagnosis=current_diagnosis,
            matches=current_matches,
            ai_output=ai_output,
            plan_id=plan_id,
        )

        # ---------------------------------------------
        # 10. 새로운 Plan 저장
        # ---------------------------------------------

        self.database.save_plan(
            {
                "user_id": request.user_id,
                "target_id": request.target_id,
                "plan_id": plan_id,
                "user": current_user,
                "snapshot": current_snapshot,
            }
        )

        # ---------------------------------------------
        # 11. Before / After 반환
        # ---------------------------------------------

        return {
            "user_id": request.user_id,
            "target_id": request.target_id,
            "previous": previous_snapshot,
            "current": current_snapshot,
            "changed_fields": changed_fields,
        }

    # -----------------------------------------------------
    # Diagnosis + PolicyMatch
    # -----------------------------------------------------

    def _compute(
        self,
        user: dict[str, Any],
        target: dict[str, Any],
        diagnosis_id: int,
    ) -> tuple[
        dict[str, Any],
        list[dict[str, Any]],
    ]:
        """
        Diagnosis 계산과 Policy Rule Matching까지만 수행한다.

        AI 호출은 수행하지 않는다.
        """

        # ---------------------------------------------
        # Diagnosis
        # ---------------------------------------------

        diagnosis = calculate_diagnosis(
            user,
            target,
        )

        diagnosis.update(
            {
                "diagnosis_id": diagnosis_id,
                "user_id": user["user_id"],
                "target_id": target["target_id"],
            }
        )

        # ---------------------------------------------
        # PolicyMatch ID 확보
        # ---------------------------------------------

        match_ids = self.database.reserve_ids(
            "match",
            _MATCH_ID_BUFFER,
        )

        first_match_id = match_ids[0]

        # ---------------------------------------------
        # Rule Engine
        # ---------------------------------------------

        matches = match_policies(
            user=user,
            target=target,
            diagnosis_id=diagnosis_id,
            first_match_id=first_match_id,
        )

        return diagnosis, matches

    # -----------------------------------------------------
    # Snapshot
    # -----------------------------------------------------

    def _build_snapshot(
        self,
        user: dict[str, Any],
        target: dict[str, Any],
        diagnosis: dict[str, Any],
        matches: list[dict[str, Any]],
        ai_output: dict[str, Any],
        plan_id: int,
    ) -> dict[str, Any]:
        """
        AI가 생성한 Action에 Backend 생성 필드를 추가하고
        최종 PlanSnapshot을 만든다.
        """

        now = datetime.now(KST)
        ai_output = _sanitize_ai_output(
            ai_output
        )

        actions: list[dict[str, Any]] = []

        for action in ai_output["actions"]:

            action_record = {
                **action,

                "action_id": self.database.next_id(
                    "action"
                ),

                "plan_id": plan_id,

                "user_id": user["user_id"],

                "diagnosis_id": diagnosis[
                    "diagnosis_id"
                ],

                "status": "TODO",

                "created_at": now,
            }

            actions.append(
                action_record
            )

        return {
            "user_id": user["user_id"],

            "target_id": target[
                "target_id"
            ],

            "diagnosis_id": diagnosis[
                "diagnosis_id"
            ],

            "plan_id": plan_id,

            "target": target,

            "diagnosis": diagnosis,

            "matched_policies": matches,

            "action_plan": {
                "summary": ai_output[
                    "summary"
                ],
                "actions": actions,
            },
        }


plan_service = PlanService()
