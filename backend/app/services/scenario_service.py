import calendar
from copy import deepcopy
from datetime import date
from enum import Enum
from typing import Any, Optional

from app.ai.scenario_planner import generate_scenario_recommendation
from app.db.database import InMemoryDatabase
from app.diagnosis.calculator import calculate_diagnosis
from app.policy.rule_engine import match_policies
from app.services.plan_service import plan_service


_DIAGNOSIS_FIELDS = (
    "readiness_score",
    "fund_score",
    "saving_score",
    "required_initial_fund",
    "initial_fund_gap",
    "required_monthly_saving",
    "estimated_months",
)
_STATUS_SCORE = {
    "NOT_ELIGIBLE": 0,
    "NEED_MORE_INFO": 1,
    "CONDITIONAL": 2,
    "AVAILABLE": 3,
}
_SCENARIO_TITLES = {
    "LOWER_DEPOSIT": "희망 보증금 낮추기",
    "DELAY_MOVE_IN": "입주 예정일 미루기",
    "INCREASE_SAVINGS": "월 저축액 늘리기",
}
_GOAL_WEIGHTS = {
    "FAST_MOVE": {
        "readiness": 0.20,
        "monthly_burden": 0.05,
        "estimated_time": 0.65,
        "policy": 0.10,
    },
    "LOW_MONTHLY_BURDEN": {
        "readiness": 0.10,
        "monthly_burden": 0.75,
        "estimated_time": 0.05,
        "policy": 0.10,
    },
    "POLICY_BENEFIT": {
        "readiness": 0.20,
        "monthly_burden": 0.10,
        "estimated_time": 0.10,
        "policy": 0.60,
    },
}


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _positive_reduction(before: Optional[float], after: Optional[float]) -> float:
    if before is None:
        return 1.0 if after is not None else 0.0
    if before <= 0 or after is None:
        return 0.0
    return min(max((before - after) / before, 0.0), 1.0)


def _policy_status_changes(
    previous_policies: list[dict[str, Any]],
    current_policies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous_by_id = {
        policy["policy_id"]: policy
        for policy in previous_policies
    }
    changes = []
    for policy in current_policies:
        previous = previous_by_id.get(policy["policy_id"])
        if previous is None:
            continue
        before = _plain(previous["eligibility_status"])
        after = _plain(policy["eligibility_status"])
        if before != after:
            changes.append(
                {
                    "policy_id": policy["policy_id"],
                    "title": policy["title"],
                    "before_status": before,
                    "after_status": after,
                }
            )
    return changes


def _policy_improvement(policy_changes: list[dict[str, Any]]) -> float:
    improvement = sum(
        max(
            _STATUS_SCORE[change["after_status"]]
            - _STATUS_SCORE[change["before_status"]],
            0,
        )
        for change in policy_changes
    )
    return min(improvement / 3, 1.0)


def _recommendation_score(
    goal_priority: str,
    baseline: dict[str, Any],
    current: dict[str, Any],
    policy_changes: list[dict[str, Any]],
) -> int:
    metrics = {
        "readiness": min(
            max(
                (current["readiness_score"] - baseline["readiness_score"]) / 100,
                0.0,
            ),
            1.0,
        ),
        "monthly_burden": _positive_reduction(
            baseline["required_monthly_saving"],
            current["required_monthly_saving"],
        ),
        "estimated_time": _positive_reduction(
            baseline["estimated_months"],
            current["estimated_months"],
        ),
        "policy": _policy_improvement(policy_changes),
    }
    utility = sum(
        metrics[name] * weight
        for name, weight in _GOAL_WEIGHTS[goal_priority].items()
    )
    return min(round(50 + utility * 50), 100)


class ScenarioService:
    def __init__(self, database: Optional[InMemoryDatabase] = None):
        self.database = database or plan_service.database

    def compare(self, request: Any) -> dict[str, Any]:
        previous_record = self.database.get_plan(
            request.user_id,
            request.target_id,
            request.previous_plan_id,
        )
        if previous_record is None:
            raise LookupError("이전 플랜을 찾을 수 없습니다.")

        previous_snapshot = previous_record["snapshot"]
        if previous_snapshot["diagnosis_id"] != request.previous_diagnosis_id:
            raise LookupError("이전 진단 ID가 플랜과 일치하지 않습니다.")

        user = deepcopy(previous_record["user"])
        target = deepcopy(previous_snapshot["target"])
        baseline_diagnosis = {
            field: previous_snapshot["diagnosis"][field]
            for field in _DIAGNOSIS_FIELDS
        }
        previous_policies = previous_snapshot["matched_policies"]
        constraints = _plain(request.constraints.model_dump())
        goal_priority = _plain(request.priority)

        scenario_changes = self._build_scenario_changes(
            user=user,
            target=target,
            constraints=constraints,
        )
        if not scenario_changes:
            raise ValueError("현재 제약조건으로 생성 가능한 시나리오가 없습니다.")

        scenarios = [
            self._evaluate_scenario(
                scenario_id=scenario_id,
                changes=changes,
                user=user,
                target=target,
                baseline_diagnosis=baseline_diagnosis,
                previous_policies=previous_policies,
                previous_diagnosis_id=request.previous_diagnosis_id,
                goal_priority=goal_priority,
            )
            for scenario_id, changes in scenario_changes
        ]
        recommended_scenario_id = max(
            scenarios,
            key=lambda scenario: scenario["recommendation_score"],
        )["scenario_id"]
        ai_input = {
            "priority": goal_priority,
            "recommended_scenario_id": recommended_scenario_id,
            "baseline": {
                "diagnosis": baseline_diagnosis,
                "policies": [
                    {
                        "policy_id": policy["policy_id"],
                        "title": policy["title"],
                        "eligibility_status": _plain(policy["eligibility_status"]),
                    }
                    for policy in previous_policies
                ],
            },
            "scenarios": scenarios,
        }
        ai_output = generate_scenario_recommendation(ai_input)
        explanation_by_id = {
            item["scenario_id"]: item
            for item in ai_output["explanations"]
        }
        return {
            "recommended_scenario_id": ai_output["recommended_scenario_id"],
            "summary": ai_output["summary"],
            "scenarios": [
                {
                    **scenario,
                    "ai_reason": explanation_by_id[scenario["scenario_id"]]["reason"],
                    "tradeoff": explanation_by_id[scenario["scenario_id"]]["tradeoff"],
                }
                for scenario in scenarios
            ],
        }

    def _build_scenario_changes(
        self,
        user: dict[str, Any],
        target: dict[str, Any],
        constraints: dict[str, Any],
    ) -> list[tuple[str, dict[str, Any]]]:
        scenarios = []
        current_deposit = target["desired_deposit"]
        minimum_deposit = constraints["minimum_desired_deposit"]
        lower_deposit = max(current_deposit - 20_000_000, 0)
        if minimum_deposit is not None:
            lower_deposit = max(lower_deposit, minimum_deposit)
        if lower_deposit < current_deposit:
            scenarios.append(
                ("LOWER_DEPOSIT", {"desired_deposit": lower_deposit})
            )

        delay_months = constraints["max_move_delay_months"]
        if delay_months > 0:
            move_in_date = target["planned_move_in_date"]
            if isinstance(move_in_date, str):
                move_in_date = date.fromisoformat(move_in_date)
            scenarios.append(
                (
                    "DELAY_MOVE_IN",
                    {
                        "planned_move_in_date": _add_months(
                            move_in_date,
                            delay_months,
                        )
                    },
                )
            )

        additional_savings = min(
            constraints["max_additional_monthly_savings"],
            max(
                user["personal_monthly_income"] - user["monthly_savings"],
                0,
            ),
        )
        if additional_savings > 0:
            scenarios.append(
                (
                    "INCREASE_SAVINGS",
                    {
                        "monthly_savings": (
                            user["monthly_savings"] + additional_savings
                        )
                    },
                )
            )
        return scenarios

    def _evaluate_scenario(
        self,
        scenario_id: str,
        changes: dict[str, Any],
        user: dict[str, Any],
        target: dict[str, Any],
        baseline_diagnosis: dict[str, Any],
        previous_policies: list[dict[str, Any]],
        previous_diagnosis_id: int,
        goal_priority: str,
    ) -> dict[str, Any]:
        current_user = deepcopy(user)
        current_target = deepcopy(target)
        for field, value in changes.items():
            if field in current_user:
                current_user[field] = value
            else:
                current_target[field] = value

        diagnosis = calculate_diagnosis(current_user, current_target)
        diagnosis_view = {
            field: diagnosis[field]
            for field in _DIAGNOSIS_FIELDS
        }
        policies = match_policies(
            user=current_user,
            target=current_target,
            diagnosis_id=previous_diagnosis_id,
            first_match_id=1,
        )
        policy_changes = _policy_status_changes(previous_policies, policies)
        score = _recommendation_score(
            goal_priority,
            baseline_diagnosis,
            diagnosis_view,
            policy_changes,
        )
        return {
            "scenario_id": scenario_id,
            "title": _SCENARIO_TITLES[scenario_id],
            "changes": changes,
            "diagnosis": diagnosis_view,
            "policy_changes": policy_changes,
            "recommendation_score": score,
        }


scenario_service = ScenarioService()
