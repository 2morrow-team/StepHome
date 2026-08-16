import json
from typing import Any

from app.ai.schemas import ActionCandidate


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
  - NEED_MORE_INFO: 부족 정보 확인 안내 Action 생성, 신청 추천하지 않음
  - NOT_ELIGIBLE: 해당 정책 관련 Action 생성하지 않음
- 허용된 action_type: SAVING, POLICY, HOUSING, CONTRACT
- 허용된 timing: NOW, PREPARE, SEARCH_HOUSE, BEFORE_CONTRACT
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
    user_context_fields = (
        "age",
        "region",
        "employment_status",
        "household_monthly_income",
        "personal_monthly_income",
        "current_savings",
        "monthly_saving",
        "housing_status",
    )
    target_context_fields = (
        "target_date",
        "target_region",
        "deposit_budget",
        "monthly_rent_budget",
        "housing_type",
    )
    diagnosis_context_fields = (
        "readiness_score",
        "fund_score",
        "saving_score",
        "required_initial_fund",
        "initial_fund_gap",
        "required_monthly_saving",
        "estimated_months",
    )
    policy_context_fields = (
        "policy_id",
        "title",
        "eligibility_status",
        "matched_conditions",
        "failed_conditions",
        "missing_conditions",
        "rank",
        "support_amount",
        "support_amount_text",
        "eligibility_text",
        "description",
        "application_start",
        "application_end",
        "application_period_type",
        "source_url",
        "checked_at",
    )
    return {
        "user_id": user["user_id"],
        "target_id": target["target_id"],
        "diagnosis_id": diagnosis["diagnosis_id"],
        "user": {f: user[f] for f in user_context_fields if f in user},
        "target": {f: target[f] for f in target_context_fields if f in target},
        "diagnosis": {f: diagnosis[f] for f in diagnosis_context_fields if f in diagnosis},
        "matched_policies": [
            {f: policy[f] for f in policy_context_fields if f in policy}
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
) -> dict[str, Any]:
    diagnosis_context_fields = (
        "readiness_score",
        "fund_score",
        "saving_score",
        "required_initial_fund",
        "initial_fund_gap",
        "required_monthly_saving",
        "estimated_months",
    )
    policy_context_fields = (
        "policy_id",
        "title",
        "eligibility_status",
        "matched_conditions",
        "failed_conditions",
        "missing_conditions",
        "rank",
        "support_amount",
        "support_amount_text",
        "application_period_type",
    )
    action_context_fields = (
        "priority",
        "action_type",
        "timing",
        "title",
        "description",
        "reason",
        "policy_id",
    )
    return {
        "changed_fields": changed_fields,
        "previous": {
            "diagnosis": {f: previous_diagnosis[f] for f in diagnosis_context_fields if f in previous_diagnosis},
            "matched_policies": [
                {f: p[f] for f in policy_context_fields if f in p}
                for p in previous_policies
            ],
            "actions": [
                {f: a[f] for f in action_context_fields if f in a}
                for a in previous_actions
            ],
        },
        "current": {
            "diagnosis": {f: current_diagnosis[f] for f in diagnosis_context_fields if f in current_diagnosis},
            "matched_policies": [
                {f: p[f] for f in policy_context_fields if f in p}
                for p in current_policies
            ],
        },
    }
