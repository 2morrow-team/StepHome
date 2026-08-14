# AI 계획 검증 모듈
from app.schemas.schemas import ActionType, Timing


def validate_action_plan(action_plan: dict) -> dict:
    actions = action_plan.get("actions", [])
    if not isinstance(action_plan.get("summary"), str) or not isinstance(actions, list):
        raise ValueError("AI ActionPlan 구조가 올바르지 않습니다.")
    for action in actions:
        if action.get("action_type") not in {item.value for item in ActionType}:
            raise ValueError("허용되지 않은 action_type입니다.")
        if action.get("timing") not in {item.value for item in Timing}:
            raise ValueError("허용되지 않은 timing입니다.")
        if not action.get("title") or not action.get("description") or not action.get("reason"):
            raise ValueError("Action 필수 설명이 누락되었습니다.")
    return action_plan
