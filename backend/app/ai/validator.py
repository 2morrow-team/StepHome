from typing import Optional

from app.ai.schemas import ActionCandidate
from app.schemas.schemas import ActionType, Timing

_BACKEND_FIELDS = {
    "plan_id",
    "action_id",
    "user_id",
    "diagnosis_id",
    "status",
    "created_at",
}


def validate_action_plan(
    action_plan: dict,
    valid_policy_ids: Optional[set[int]] = None,
    candidates: Optional[list[ActionCandidate]] = None,
) -> dict:
    if not isinstance(action_plan, dict):
        raise ValueError("AI ActionPlan 구조가 올바르지 않습니다.")

    actions = action_plan.get("actions", [])
    if not action_plan.get("summary") or not isinstance(action_plan["summary"], str) or not isinstance(actions, list):
        raise ValueError("AI ActionPlan 구조가 올바르지 않습니다.")

    allowed_candidates = None
    candidate_by_key = {}
    if candidates is not None:
        allowed_candidates = {(candidate.action_type, candidate.policy_id) for candidate in candidates}
        candidate_by_key = {
            (candidate.action_type, candidate.policy_id): candidate
            for candidate in candidates
        }

    used_candidates: set[tuple[str, Optional[int]]] = set()
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("AI Action 구조가 올바르지 않습니다.")

        unexpected = _BACKEND_FIELDS & action.keys()
        if unexpected:
            raise ValueError(f"AI 출력에 Backend 생성 필드가 포함되어 있습니다: {unexpected}")

        if action.get("action_type") not in {item.value for item in ActionType}:
            raise ValueError(f"허용되지 않은 action_type입니다: {action.get('action_type')}")

        if action.get("timing") not in {item.value for item in Timing}:
            raise ValueError(f"허용되지 않은 timing입니다: {action.get('timing')}")

        if not action.get("title") or not action.get("description") or not action.get("reason"):
            raise ValueError("Action 필수 설명이 누락되었습니다.")

        if not isinstance(action.get("priority"), int) or action["priority"] < 1:
            raise ValueError("priority는 1 이상의 정수여야 합니다.")

        # Hallucination 방지: 실제 매칭된 정책 ID만 허용
        policy_id = action.get("policy_id")
        if valid_policy_ids is not None and policy_id is not None:
            if policy_id not in valid_policy_ids:
                raise ValueError(f"존재하지 않는 policy_id가 포함되어 있습니다: {policy_id}")

        if allowed_candidates is not None:
            candidate_key = (action["action_type"], policy_id)
            if candidate_key not in allowed_candidates:
                raise ValueError(
                    "허용되지 않은 Action 후보입니다: "
                    f"action_type={action['action_type']}, policy_id={policy_id}"
                )
            if candidate_key in used_candidates:
                raise ValueError(
                    "동일한 Action 후보가 중복 생성되었습니다: "
                    f"action_type={action['action_type']}, policy_id={policy_id}"
                )
            used_candidates.add(candidate_key)

            candidate = candidate_by_key[candidate_key]
            period_type = candidate.context.get("application_period_type")
            if period_type != "FIXED" and action.get("due_date") is not None:
                raise ValueError("FIXED 신청기간이 아닌 정책의 due_date는 null이어야 합니다.")

    priorities = [action["priority"] for action in actions]
    if priorities != list(range(1, len(actions) + 1)):
        raise ValueError("priority는 1부터 중복 없이 순서대로 지정해야 합니다.")

    return action_plan
