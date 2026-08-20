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

_STATUS_LABELS = {
    "AVAILABLE": "신청 가능",
    "CONDITIONAL": "조건 조정 필요",
    "NEED_MORE_INFO": "추가 확인 필요",
    "NOT_ELIGIBLE": "현재 대상 아님",
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


_BASIS_PHASE: dict[str, int] = {
    CandidateBasis.SAVING_MAINTAIN: 1,
    CandidateBasis.SAVING_ADJUST: 1,
    CandidateBasis.POLICY_APPLY: 1,
    CandidateBasis.POLICY_MONITOR: 3,
    CandidateBasis.CONDITION_ADJUST: 2,
    CandidateBasis.INFORMATION_NOTICE: 2,
    CandidateBasis.CONTRACT_CHECK: 4,
}
_REQUIRED_PHASES = {1, 2, 3, 4}


def _candidate_for_phase(candidates: list[ActionCandidate], phase: int) -> ActionCandidate:
    preferred_action_types = {
        1: ("SAVING", "POLICY"),
        2: ("POLICY", "HOUSING", "SAVING"),
        3: ("HOUSING", "POLICY", "SAVING"),
        4: ("CONTRACT", "HOUSING", "SAVING"),
    }
    for action_type in preferred_action_types[phase]:
        for candidate in candidates:
            if candidate.action_type == action_type:
                return candidate
    return candidates[0]


def _phase_fill_action(
    candidate: ActionCandidate,
    phase: int,
    priority: int,
) -> dict[str, Any]:
    policy_title = candidate.context.get("title") or "정책"
    common = {
        "phase": phase,
        "priority": priority,
        "action_type": candidate.action_type,
        "policy_id": candidate.policy_id,
        "due_date": None,
    }
    if phase == 1:
        return {
            **common,
            "timing": "NOW",
            "title": "즉시 실행 점검",
            "description": "이번 주 안에 월 저축액, 신청 가능한 정책, 현재 부족 조건을 한 번에 확인하세요.",
            "reason": "독립 준비 초반에는 바로 실행할 항목을 먼저 정리해야 합니다.",
        }
    if phase == 2:
        return {
            **common,
            "timing": "PREPARE",
            "title": "서류 조건 정리",
            "description": f"{policy_title} 관련 필요서류와 미충족 조건을 정리하고 보완 일정을 잡으세요.",
            "reason": "단기 준비 단계에서는 신청 가능성을 높이기 위한 조건 확인이 필요합니다.",
        }
    if phase == 3:
        return {
            **common,
            "timing": "SEARCH_HOUSE",
            "title": "주거 후보 탐색",
            "description": "희망 지역의 보증금·월세 범위에 맞는 매물을 비교하고 정책 공고 변동을 함께 확인하세요.",
            "reason": "입주 수개월 전에는 실제 주거 선택지와 정책 일정을 함께 좁혀야 합니다.",
        }
    return {
        **common,
        "timing": "BEFORE_CONTRACT",
        "title": "입주 전 최종점검",
        "description": "계약 전 등기부등본, 선순위 권리, 보증보험 가입 가능 여부와 이사 일정을 최종 확인하세요.",
        "reason": "입주 직전에는 계약 안전과 이사 실행 준비가 가장 중요합니다.",
    }


def _candidate_action(candidate: ActionCandidate, priority: int) -> dict[str, Any]:
    context = candidate.context
    policy_title = context.get("title") or "해당 정책"
    common = {
        "phase": _BASIS_PHASE.get(candidate.basis, 1),
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
        label = _FIELD_LABELS.get(field, "변경 조건")
        change_texts.append(
            f"{label}: {_won(values.get('before'))}에서 {_won(values.get('after'))}(으)로 변경"
        )

    def _status_str(v: Any) -> str:
        value = v.value if hasattr(v, "value") else str(v)
        return _STATUS_LABELS.get(value, value)

    def _status_key(v: Any) -> str:
        return v.value if hasattr(v, "value") else str(v)

    previous_policies = {
        policy.get("policy_id"): policy.get("eligibility_status")
        for policy in replan_input.get("previous", {}).get("matched_policies", [])
    }
    transitions = []
    for policy in replan_input.get("current", {}).get("matched_policies", []):
        policy_id = policy.get("policy_id")
        before = previous_policies.get(policy_id)
        after = policy.get("eligibility_status")
        if before and _status_key(before) != _status_key(after):
            transitions.append(f"{policy.get('title', '정책')} {_status_str(before)}→{_status_str(after)}")

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
    used_phases = {action["phase"] for action in actions}
    for phase in sorted(_REQUIRED_PHASES - used_phases):
        candidate = _candidate_for_phase(candidates, phase)
        actions.append(_phase_fill_action(candidate, phase, len(actions) + 1))
    actions.sort(key=lambda action: (action["phase"], action["priority"]))
    for priority, action in enumerate(actions, start=1):
        action["priority"] = priority
    summary = (
        _replan_summary(replan_input)
        if replan_input is not None
        else "진단과 정책 판정 결과를 바탕으로 저축, 정책 확인, 계약 안전 순서의 실행 계획을 구성했습니다."
    )
    return {"summary": summary, "actions": actions}
