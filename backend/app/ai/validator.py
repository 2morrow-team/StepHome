from typing import Optional

from app.schemas.schemas import ActionType, Timing

_BACKEND_FIELDS = {"plan_id", "action_id", "status", "created_at"}


def validate_action_plan(
    action_plan: dict,
    valid_policy_ids: Optional[set[int]] = None,
) -> dict:
    actions = action_plan.get("actions", [])
    if not isinstance(action_plan.get("summary"), str) or not isinstance(actions, list):
        raise ValueError("AI ActionPlan 구조가 올바르지 않습니다.")

    for action in actions:
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

    return action_plan
