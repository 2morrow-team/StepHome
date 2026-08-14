# 플랜 전체 흐름을 연결하는 서비스
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from app.ai.planner import generate_action_plan
from app.ai.prompts import build_ai_input
from app.ai.validator import validate_action_plan
from app.db.database import InMemoryDatabase
from app.diagnosis.calculator import calculate_diagnosis
from app.policy.rule_engine import match_policies


KST = timezone(timedelta(hours=9))
DEFAULT_TARGET_REGION = "서울"


def _dump(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


class PlanService:
    def __init__(self, database: InMemoryDatabase | None = None):
        self.database = database or InMemoryDatabase()

    def create_plan(self, request: Any) -> dict[str, Any]:
        user_id = self.database.next_id("user")
        target_id = self.database.next_id("target")
        diagnosis_id = self.database.next_id("diagnosis")
        plan_id = self.database.next_id("plan")

        user = _plain(_dump(request.user))
        user["user_id"] = user_id
        target = _plain(_dump(request.target))
        target["target_id"] = target_id
        target["user_id"] = user_id
        target["target_region"] = DEFAULT_TARGET_REGION

        snapshot = self._create_snapshot(
            user=user,
            target=target,
            diagnosis_id=diagnosis_id,
            plan_id=plan_id,
        )
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

    def replan(self, request: Any) -> dict[str, Any]:
        previous_record = self.database.get_plan(
            request.user_id,
            request.target_id,
            request.previous_plan_id,
        )
        if previous_record is None:
            raise LookupError("이전 플랜을 찾을 수 없습니다.")
        if previous_record["snapshot"]["diagnosis_id"] != request.previous_diagnosis_id:
            raise LookupError("이전 진단 ID가 플랜과 일치하지 않습니다.")

        previous_snapshot = previous_record["snapshot"]
        target = deepcopy(previous_snapshot["target"])
        changes = _plain(_dump(request.changes))
        if changes.get("deposit_budget") is not None:
            target["deposit_budget"] = changes["deposit_budget"]

        diagnosis_id = self.database.next_id("diagnosis")
        plan_id = self.database.next_id("plan")
        current_snapshot = self._create_snapshot(
            user=deepcopy(previous_record["user"]),
            target=target,
            diagnosis_id=diagnosis_id,
            plan_id=plan_id,
        )
        self.database.save_plan(
            {
                "user_id": request.user_id,
                "target_id": request.target_id,
                "plan_id": plan_id,
                "user": previous_record["user"],
                "snapshot": current_snapshot,
            }
        )

        changed_fields: dict[str, dict[str, int]] = {}
        if changes.get("deposit_budget") is not None:
            changed_fields["deposit_budget"] = {
                "before": previous_snapshot["target"]["deposit_budget"],
                "after": target["deposit_budget"],
            }
        return {
            "user_id": request.user_id,
            "target_id": request.target_id,
            "previous": previous_snapshot,
            "current": current_snapshot,
            "changed_fields": changed_fields,
        }

    def _create_snapshot(
        self,
        user: dict[str, Any],
        target: dict[str, Any],
        diagnosis_id: int,
        plan_id: int,
    ) -> dict[str, Any]:
        diagnosis = calculate_diagnosis(user, target)
        diagnosis.update(
            {
                "diagnosis_id": diagnosis_id,
                "user_id": user["user_id"],
                "target_id": target["target_id"],
            }
        )
        first_match_id = self.database.reserve_ids("match", 2)[0]
        matches = match_policies(
            user=user,
            target=target,
            diagnosis_id=diagnosis_id,
            first_match_id=first_match_id,
        )
        ai_input = build_ai_input(user, target, diagnosis, matches)
        ai_output = validate_action_plan(generate_action_plan(ai_input))
        now = datetime.now(KST)
        actions = []
        for action in ai_output["actions"]:
            action_record = {
                **action,
                "action_id": self.database.next_id("action"),
                "plan_id": plan_id,
                "user_id": user["user_id"],
                "diagnosis_id": diagnosis_id,
                "status": "TODO",
                "created_at": now,
            }
            actions.append(action_record)

        return {
            "user_id": user["user_id"],
            "target_id": target["target_id"],
            "diagnosis_id": diagnosis_id,
            "plan_id": plan_id,
            "target": target,
            "diagnosis": diagnosis,
            "matched_policies": matches,
            "action_plan": {
                "summary": ai_output["summary"],
                "actions": actions,
            },
        }


plan_service = PlanService()
