import json
import os
from typing import Any

import anthropic

from app.ai.candidate_generator import generate_candidates
from app.ai.prompts import build_plan_prompt, build_replan_prompt
from app.ai.validator import validate_action_plan

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("AI_API_KEY"))
    return _client


def _call_llm(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """LLM API 호출을 담당하는 유일한 함수. 모델 교체 시 이 함수만 수정한다."""
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return json.loads(message.content[0].text)


def generate_action_plan(ai_input: dict[str, Any]) -> dict[str, Any]:
    candidates = generate_candidates(
        diagnosis=ai_input["diagnosis"],
        matched_policies=ai_input["matched_policies"],
        monthly_saving=ai_input.get("user", {}).get("monthly_saving"),
    )
    system_prompt, user_prompt = build_plan_prompt(ai_input, candidates)
    result = _call_llm(system_prompt, user_prompt)
    valid_policy_ids = {p["policy_id"] for p in ai_input["matched_policies"]}
    return validate_action_plan(result, valid_policy_ids=valid_policy_ids)


def generate_replan_action_plan(replan_ai_input: dict[str, Any]) -> dict[str, Any]:
    current = replan_ai_input["current"]
    candidates = generate_candidates(
        diagnosis=current["diagnosis"],
        matched_policies=current["matched_policies"],
    )
    system_prompt, user_prompt = build_replan_prompt(replan_ai_input, candidates)
    result = _call_llm(system_prompt, user_prompt)
    valid_policy_ids = {p["policy_id"] for p in current["matched_policies"]}
    return validate_action_plan(result, valid_policy_ids=valid_policy_ids)
