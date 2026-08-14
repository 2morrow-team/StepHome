# AI 플래너 모듈
from typing import Any

from app.schemas.schemas import ActionType, EligibilityStatus, Timing


def generate_action_plan(ai_input: dict[str, Any]) -> dict[str, Any]:
    diagnosis = ai_input["diagnosis"]
    policies = ai_input["matched_policies"]
    actions: list[dict[str, Any]] = []

    actions.append(
        {
            "priority": 1,
            "action_type": ActionType.SAVING.value,
            "timing": Timing.NOW.value,
            "title": "월 저축계획 유지",
            "description": f"현재 월 {ai_input['user']['monthly_saving']}원의 저축 가능액을 유지합니다.",
            "reason": f"목표일까지 필요한 월 저축액은 {diagnosis['required_monthly_saving']}원입니다.",
            "policy_id": None,
            "due_date": None,
        }
    )

    for policy in policies:
        status = getattr(policy["eligibility_status"], "value", policy["eligibility_status"])
        if status == EligibilityStatus.AVAILABLE.value:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "action_type": ActionType.POLICY.value,
                    "timing": Timing.NOW.value,
                    "title": f"{policy['title']} 신청 준비",
                    "description": "신청기간과 필요서류를 확인하고 정책 신청을 준비합니다.",
                    "reason": "현재 이용 가능한 정책으로 주거비 부담을 줄일 수 있습니다.",
                    "policy_id": policy["policy_id"],
                    "due_date": policy["application_end"],
                }
            )
        elif status == EligibilityStatus.CONDITIONAL.value:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "action_type": ActionType.HOUSING.value,
                    "timing": Timing.SEARCH_HOUSE.value,
                    "title": "보증금 조건 조정 검토",
                    "description": "조건부 정책의 보증금 기준과 목표 보증금을 함께 검토합니다.",
                    "reason": "보증금 조건을 조정하면 정책 이용 가능성이 달라질 수 있습니다.",
                    "policy_id": policy["policy_id"],
                    "due_date": None,
                }
            )

    actions.append(
        {
            "priority": len(actions) + 1,
            "action_type": ActionType.CONTRACT.value,
            "timing": Timing.BEFORE_CONTRACT.value,
            "title": "계약 전 안전사항 확인",
            "description": "등기부등본, 주변 시세, 보증보험 가입 가능 여부를 확인합니다.",
            "reason": "첫 독립 과정의 계약 위험을 줄이기 위해 필요합니다.",
            "policy_id": None,
            "due_date": None,
        }
    )

    return {
        "summary": "현재 준비도와 이용 가능한 정책을 바탕으로 독립 준비 Action Plan을 생성했습니다.",
        "actions": actions,
    }
