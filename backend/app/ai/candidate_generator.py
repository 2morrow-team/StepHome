from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from app.ai.schemas import ActionCandidate, CandidateBasis
from app.schemas.schemas import EligibilityStatus


_HOUSING_CONDITIONS = {
    "DEPOSIT_LIMIT",
    "HOUSING_TYPE",
    "MONTHLY_RENT_LIMIT",
    # 현재 Rule Engine의 축약 조건명과 최종 Contract 조건명을 함께 지원한다.
    "REGION",
    "TARGET_REGION",
    "DESIRED_REGION",
    "DESIRED_DEPOSIT",
    "DESIRED_MONTHLY_RENT",
    "DESIRED_HOUSING_TYPE",
}
KST = timezone(timedelta(hours=9))


def _conditional_action_type(policy: dict[str, Any]) -> str:
    """사용자가 바꿀 조건의 성격에 따라 조건부 Action 유형을 정한다."""
    failed_conditions = set(policy.get("failed_conditions", []))
    if failed_conditions & _HOUSING_CONDITIONS:
        return "HOUSING"
    return "POLICY"


def _is_application_closed(
    policy: dict[str, Any],
    today: Optional[date] = None,
) -> bool:
    period_type = policy.get("application_period_type")
    if hasattr(period_type, "value"):
        period_type = period_type.value
    if period_type != "FIXED" or not policy.get("application_end"):
        return False

    application_end = policy["application_end"]
    if isinstance(application_end, str):
        application_end = date.fromisoformat(application_end)
    return application_end < (today or datetime.now(KST).date())


def _policy_schedule_context(
    policy: dict[str, Any],
    today: Optional[date] = None,
) -> dict[str, Any]:
    """모든 정책 후보에 동일한 신청기간 정보를 전달한다."""
    return {
        "application_end": policy.get("application_end"),
        "application_period_type": policy.get("application_period_type"),
        "is_application_closed": _is_application_closed(policy, today=today),
    }


def generate_candidates(
    diagnosis: dict[str, Any],
    matched_policies: list[dict[str, Any]],
    monthly_saving: Optional[int] = None,
    today: Optional[date] = None,
) -> list[ActionCandidate]:
    """
    판정된 Diagnosis + PolicyMatch 결과를 받아
    AI가 생성해도 되는 Action 후보를 결정한다.

    서우님의 Rule Engine: "사용자가 이 정책 자격이 되는가?"
    이 함수:           "판정된 결과로 어떤 Action을 AI에게 허용할 것인가?"
    """
    candidates: list[ActionCandidate] = []

    # Saving candidate
    required_monthly_saving = diagnosis.get("required_monthly_saving", 0)
    if monthly_saving is not None and required_monthly_saving > 0:
        basis = (
            CandidateBasis.SAVING_MAINTAIN
            if monthly_saving >= required_monthly_saving
            else CandidateBasis.SAVING_ADJUST
        )
    else:
        basis = CandidateBasis.SAVING_MAINTAIN

    candidates.append(ActionCandidate(
        action_type="SAVING",
        basis=basis,
        context={
            "required_monthly_saving": required_monthly_saving,
            "monthly_saving": monthly_saving,
            "estimated_months": diagnosis.get("estimated_months"),
        },
    ))

    # Policy candidates — eligibility_status별 Action 허용 결정
    for policy in matched_policies:
        status = policy.get("eligibility_status")
        if hasattr(status, "value"):
            status = status.value

        if status == EligibilityStatus.AVAILABLE.value:
            candidates.append(ActionCandidate(
                action_type="POLICY",
                basis=(
                    CandidateBasis.POLICY_MONITOR
                    if _is_application_closed(policy, today=today)
                    else CandidateBasis.POLICY_APPLY
                ),
                policy_id=policy.get("policy_id"),
                context={
                    "title": policy.get("title"),
                    "support_amount_text": policy.get("support_amount_text"),
                    "condition_details": policy.get("condition_details", []),
                    **_policy_schedule_context(policy, today=today),
                },
            ))
        elif status == EligibilityStatus.CONDITIONAL.value:
            candidates.append(ActionCandidate(
                action_type=_conditional_action_type(policy),
                basis=CandidateBasis.CONDITION_ADJUST,
                policy_id=policy.get("policy_id"),
                context={
                    "title": policy.get("title"),
                    "failed_conditions": policy.get("failed_conditions", []),
                    "missing_conditions": policy.get("missing_conditions", []),
                    "condition_details": policy.get("condition_details", []),
                    **_policy_schedule_context(policy, today=today),
                },
            ))
        elif status == EligibilityStatus.NEED_MORE_INFO.value:
            candidates.append(ActionCandidate(
                action_type="POLICY",
                basis=CandidateBasis.INFORMATION_NOTICE,
                policy_id=policy.get("policy_id"),
                context={
                    "title": policy.get("title"),
                    "missing_conditions": policy.get("missing_conditions", []),
                    "condition_details": policy.get("condition_details", []),
                    **_policy_schedule_context(policy, today=today),
                },
            ))
        # NOT_ELIGIBLE: candidate 생성하지 않음

    # Contract candidate — 첫 독립 시 항상 포함
    candidates.append(ActionCandidate(
        action_type="CONTRACT",
        basis=CandidateBasis.CONTRACT_CHECK,
        context={"note": "첫 독립 계약 전 안전 확인"},
    ))

    return candidates
