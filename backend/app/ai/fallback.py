from typing import Any, Optional

from app.ai.schemas import ActionCandidate, CandidateBasis


_FIELD_LABELS = {
    "desired_deposit": "희망 보증금",
    "desired_monthly_rent": "희망 월세",
    "planned_move_in_date": "입주 예정일",
    "desired_region": "희망 지역",
    "desired_housing_type": "희망 주거 형태",
    "monthly_savings": "월 저축액",
    "total_assets": "총자산",
}


def _won(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:,.0f}원"
    return str(value)


def _schedule(candidate: ActionCandidate) -> Optional[Any]:
    if candidate.context.get("is_application_closed"):
        return None
    if candidate.context.get("application_period_type") == "FIXED":
        return candidate.context.get("application_end")
    return None


def _first_condition_message(candidate: ActionCandidate) -> str:
    for detail in candidate.context.get("condition_details", []):
        if detail.get("message"):
            return str(detail["message"])
    conditions = (
        candidate.context.get("failed_conditions")
        or candidate.context.get("missing_conditions")
        or []
    )
    return ", ".join(str(condition) for condition in conditions)


def _candidate_action(candidate: ActionCandidate, priority: int) -> dict[str, Any]:
    context = candidate.context
    policy_title = context.get("title") or "해당 정책"
    common = {
        "priority": priority,
        "action_type": candidate.action_type,
        "policy_id": candidate.policy_id,
        "due_date": _schedule(candidate),
    }

    if candidate.basis == CandidateBasis.SAVING_ADJUST:
        current = _won(context.get("monthly_saving"))
        required = _won(context.get("required_monthly_saving"))
        return {
            **common,
            "timing": "NOW",
            "title": "월 저축액 조정",
            "description": (
                f"현재 월 {current}과 필요 월 {required}의 차이를 확인하고, "
                "저축액·희망 보증금·입주 일정을 함께 조정하세요."
            ),
            "reason": "현재 저축 속도로는 목표 시점까지 필요한 초기자금 마련이 어렵습니다.",
        }

    if candidate.basis == CandidateBasis.SAVING_MAINTAIN:
        return {
            **common,
            "timing": "NOW",
            "title": "월 저축계획 유지",
            "description": "현재 월 저축 계획을 유지하고 매달 목표 대비 진행률을 확인하세요.",
            "reason": "진단 결과에 맞는 저축 흐름을 꾸준히 유지하는 것이 중요합니다.",
        }

    if candidate.basis == CandidateBasis.POLICY_APPLY:
        support = context.get("support_amount_text") or "지원 내용"
        return {
            **common,
            "timing": "NOW",
            "title": "정책 신청 준비",
            "description": f"{policy_title}의 신청서류를 확인하세요. 지원 내용은 {support}입니다.",
            "reason": "현재 입력 조건으로 신청 가능한 정책입니다.",
        }

    if candidate.basis == CandidateBasis.POLICY_MONITOR:
        return {
            **common,
            "timing": "PREPARE",
            "title": "다음 모집 확인",
            "description": (
                f"{policy_title}의 현재 신청기간은 종료되었습니다. "
                "공식 사이트에서 다음 모집공고와 변경 조건을 확인하세요."
            ),
            "reason": "자격 조건은 맞지만 종료된 접수에 현재 신청하도록 안내할 수 없습니다.",
        }

    if candidate.basis == CandidateBasis.CONDITION_ADJUST:
        detail = _first_condition_message(candidate) or "미충족 조건을 확인하세요."
        has_missing = bool(context.get("missing_conditions"))
        missing_note = " 추가 확인이 필요한 조건도 함께 점검하세요." if has_missing else ""
        return {
            **common,
            "timing": "NOW",
            "title": "주거조건 조정" if candidate.action_type == "HOUSING" else "정책조건 확인",
            "description": f"{policy_title}: {detail}{missing_note}",
            "reason": "변경 가능한 조건을 조정하면 정책 활용 가능성을 높일 수 있습니다.",
        }

    if candidate.basis == CandidateBasis.INFORMATION_NOTICE:
        detail = _first_condition_message(candidate) or "추가 확인 항목을 점검하세요."
        return {
            **common,
            "timing": "PREPARE",
            "title": "추가정보 확인",
            "description": f"{policy_title}: {detail}",
            "reason": "현재 정보만으로는 신청 가능 여부를 확정할 수 없습니다.",
        }

    return {
        **common,
        "timing": "BEFORE_CONTRACT",
        "title": "계약 안전 확인",
        "description": "계약 전 등기부등본, 선순위 권리, 보증보험 가입 가능 여부를 확인하세요.",
        "reason": "첫 독립 계약에서 보증금 손실 위험을 줄이기 위한 필수 절차입니다.",
    }


def _replan_summary(replan_input: dict[str, Any]) -> str:
    changes = replan_input.get("changed_fields", {})
    change_texts = []
    for field, values in changes.items():
        label = _FIELD_LABELS.get(field, field)
        change_texts.append(
            f"{label}을(를) {_won(values.get('before'))}에서 {_won(values.get('after'))}(으)로 변경"
        )

    previous_policies = {
        policy.get("policy_id"): policy.get("eligibility_status")
        for policy in replan_input.get("previous", {}).get("matched_policies", [])
    }
    transitions = []
    for policy in replan_input.get("current", {}).get("matched_policies", []):
        policy_id = policy.get("policy_id")
        before = previous_policies.get(policy_id)
        after = policy.get("eligibility_status")
        if before and before != after:
            transitions.append(f"{policy.get('title', '정책')} {before}→{after}")

    summary = "; ".join(change_texts) or "변경된 조건"
    if transitions:
        summary += ". 정책 상태 변화: " + ", ".join(transitions)
    return summary + ". 새 진단 결과에 맞춰 실행 순서를 다시 구성했습니다."


def build_fallback_action_plan(
    candidates: list[ActionCandidate],
    replan_input: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """외부 AI 호출이 불가능할 때 후보 규칙만으로 안전한 최소 플랜을 만든다."""
    actions = [
        _candidate_action(candidate, priority)
        for priority, candidate in enumerate(candidates, start=1)
    ]
    summary = (
        _replan_summary(replan_input)
        if replan_input is not None
        else "진단과 정책 판정 결과를 바탕으로 저축, 정책 확인, 계약 안전 순서의 실행 계획을 구성했습니다."
    )
    return {"summary": summary, "actions": actions}
