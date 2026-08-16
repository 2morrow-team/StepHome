from typing import Any, Optional

from app.ai.schemas import ActionCandidate, CandidateBasis
from app.schemas.schemas import EligibilityStatus


def generate_candidates(
    diagnosis: dict[str, Any],
    matched_policies: list[dict[str, Any]],
    monthly_saving: Optional[int] = None,
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
                basis=CandidateBasis.POLICY_APPLY,
                policy_id=policy.get("policy_id"),
                context={
                    "title": policy.get("title"),
                    "application_end": policy.get("application_end"),
                    "application_period_type": policy.get("application_period_type"),
                    "support_amount_text": policy.get("support_amount_text"),
                },
            ))
        elif status == EligibilityStatus.CONDITIONAL.value:
            candidates.append(ActionCandidate(
                action_type="HOUSING",
                basis=CandidateBasis.CONDITION_ADJUST,
                policy_id=policy.get("policy_id"),
                context={
                    "title": policy.get("title"),
                    "failed_conditions": policy.get("failed_conditions", []),
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
