import json
from typing import Any, Optional

from app.ai.schemas import ActionCandidate


_USER_CONTEXT_FIELDS = (
    "age",
    "current_region",
    "employment_status",
    "marital_status",
    "youth_household_monthly_income",
    "youth_household_size",
    "personal_monthly_income",
    "total_assets",
    "monthly_savings",
    "housing_status",
)
_TARGET_CONTEXT_FIELDS = (
    "planned_move_in_date",
    "desired_region",
    "desired_deposit",
    "desired_monthly_rent",
    "desired_housing_type",
)
_DIAGNOSIS_CONTEXT_FIELDS = (
    "readiness_score",
    "fund_score",
    "saving_score",
    "required_initial_fund",
    "initial_fund_gap",
    "required_monthly_saving",
    "estimated_months",
)
_POLICY_CONTEXT_FIELDS = (
    "policy_id",
    "title",
    "policy_category",
    "policy_region",
    "policy_provider",
    "eligibility_status",
    "matched_conditions",
    "failed_conditions",
    "missing_conditions",
    "condition_details",
    "rank",
    "support_amount",
    "support_amount_unit",
    "support_amount_text",
    "eligibility_text",
    "description",
    "application_start",
    "application_end",
    "application_period_type",
    "source_url",
    "checked_at",
)


_SYSTEM_PROMPT = """당신은 대한민국 청년의 첫 독립 준비를 돕는 Action Plan 생성 전문가입니다.
Backend에서 계산한 Diagnosis 결과와 Rule Engine이 판정한 Policy 결과를 그대로 활용합니다.
반드시 JSON만 응답하고, 설명이나 마크다운 코드블록은 포함하지 마세요."""

_OUTPUT_FORMAT = """\
아래 JSON 형식으로만 응답:
{
  "summary": "사용자 상황 전체를 1~2문장으로 요약",
  "actions": [
    {
      "priority": 1,
      "action_type": "SAVING",
      "timing": "NOW",
      "title": "행동 제목 (15자 이내)",
      "description": "구체적인 행동 방법",
      "reason": "추천 이유",
      "policy_id": null,
      "due_date": null
    }
  ]
}"""

_ACTION_RULES = """\
Action 생성 규칙:
- Diagnosis 재계산이나 Policy 자격 재판정 금지
- eligibility_status별 처리:
  - AVAILABLE: 정책 신청/활용 Action 생성
  - CONDITIONAL: 사용자가 변경 가능한 미충족 조건 해결 Action 생성
    - missing_conditions도 있으면 추가 확인이 필요하다고 함께 안내하고, 조건 변경만으로 신청 가능하다고 단정하지 않음
  - NEED_MORE_INFO: 부족 정보 확인 안내 Action 생성, 신청 추천하지 않음
  - NOT_ELIGIBLE: 해당 정책 관련 Action 생성하지 않음
- 허용된 action_type: SAVING, POLICY, HOUSING, CONTRACT
- 허용된 timing: NOW, PREPARE, SEARCH_HOUSE, BEFORE_CONTRACT
- application_period_type이 FIXED인 정책의 due_date는 application_end와 동일
- application_period_type이 FIXED가 아닌 정책의 due_date는 null
- priority는 1부터 순서대로"""


def _format_candidates(candidates: list[ActionCandidate]) -> str:
    lines = []
    for c in candidates:
        line = f"- [{c.action_type}] {c.basis}"
        if c.policy_id is not None:
            line += f" (policy_id={c.policy_id})"
        if c.context.get("title"):
            line += f": {c.context['title']}"
        lines.append(line)
    return "\n".join(lines)


def _select_fields(data: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: data[field] for field in fields if field in data}


def build_plan_prompt(
    ai_input: dict[str, Any],
    candidates: list[ActionCandidate],
) -> tuple[str, str]:
    user = f"""다음은 독립을 준비 중인 청년의 현재 상황입니다.

{json.dumps(ai_input, ensure_ascii=False, indent=2, default=str)}

생성 예상 Action 후보:
{_format_candidates(candidates)}

{_ACTION_RULES}

{_OUTPUT_FORMAT}"""
    return _SYSTEM_PROMPT, user


def build_replan_prompt(
    replan_ai_input: dict[str, Any],
    candidates: list[ActionCandidate],
) -> tuple[str, str]:
    user = f"""다음은 독립 조건을 변경한 사용자의 재계획 정보입니다.

{json.dumps(replan_ai_input, ensure_ascii=False, indent=2, default=str)}

현재 조건 기준 생성 예상 Action 후보:
{_format_candidates(candidates)}

{_ACTION_RULES}
추가 규칙:
- 변경 전/후 차이를 summary에 반영
- 정책 상태 변화(예: CONDITIONAL→AVAILABLE)가 있다면 summary와 Action에 반영
- 이전 Action Plan을 참고해 변경된 상황에 맞게 우선순위 재조정

{_OUTPUT_FORMAT}"""
    return _SYSTEM_PROMPT, user


def build_ai_input(
    user: dict[str, Any],
    target: dict[str, Any],
    diagnosis: dict[str, Any],
    matched_policies: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "user_id": user["user_id"],
        "target_id": target["target_id"],
        "diagnosis_id": diagnosis["diagnosis_id"],
        "user": _select_fields(user, _USER_CONTEXT_FIELDS),
        "target": _select_fields(target, _TARGET_CONTEXT_FIELDS),
        "diagnosis": _select_fields(diagnosis, _DIAGNOSIS_CONTEXT_FIELDS),
        "matched_policies": [
            _select_fields(policy, _POLICY_CONTEXT_FIELDS)
            for policy in matched_policies
        ],
    }


def build_replan_ai_input(
    changed_fields: dict[str, Any],
    previous_diagnosis: dict[str, Any],
    previous_policies: list[dict[str, Any]],
    previous_actions: list[dict[str, Any]],
    current_diagnosis: dict[str, Any],
    current_policies: list[dict[str, Any]],
    current_user: Optional[dict[str, Any]] = None,
    current_target: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    action_context_fields = (
        "priority",
        "action_type",
        "timing",
        "title",
        "description",
        "reason",
        "policy_id",
        "due_date",
    )
    return {
        "changed_fields": changed_fields,
        "previous": {
            "diagnosis": _select_fields(previous_diagnosis, _DIAGNOSIS_CONTEXT_FIELDS),
            "matched_policies": [
                _select_fields(policy, _POLICY_CONTEXT_FIELDS)
                for policy in previous_policies
            ],
            "actions": [
                {f: a[f] for f in action_context_fields if f in a}
                for a in previous_actions
            ],
        },
        "current": {
            "user": _select_fields(current_user or {}, _USER_CONTEXT_FIELDS),
            "target": _select_fields(current_target or {}, _TARGET_CONTEXT_FIELDS),
            "diagnosis": _select_fields(current_diagnosis, _DIAGNOSIS_CONTEXT_FIELDS),
            "matched_policies": [
                _select_fields(policy, _POLICY_CONTEXT_FIELDS)
                for policy in current_policies
            ],
        },
    }
