import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.ai.candidate_generator import generate_candidates
from app.ai.prompts import build_plan_prompt, build_replan_prompt
from app.ai.schemas import ActionPlanOutput
from app.ai.validator import validate_action_plan

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env", override=False)

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        _client = OpenAI(api_key=api_key)
    return _client


def _call_llm(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """LLM API 호출을 담당하는 유일한 함수. 모델 교체 시 이 함수만 수정한다."""
    response = _get_client().responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-terra"),
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text_format=ActionPlanOutput,
        reasoning={"effort": os.getenv("OPENAI_REASONING_EFFORT", "low")},
        max_output_tokens=2048,
    )
    if response.output_parsed is None:
        raise ValueError("LLM이 구조화된 ActionPlan을 반환하지 않았습니다.")
    return response.output_parsed.model_dump(mode="json")


def generate_action_plan(ai_input: dict[str, Any]) -> dict[str, Any]:
    candidates = generate_candidates(
        diagnosis=ai_input["diagnosis"],
        matched_policies=ai_input["matched_policies"],
        monthly_saving=ai_input.get("user", {}).get("monthly_savings"),
    )
    system_prompt, user_prompt = build_plan_prompt(ai_input, candidates)
    result = _call_llm(system_prompt, user_prompt)
    return validate_action_plan(result, candidates=candidates)


def generate_replan_action_plan(replan_ai_input: dict[str, Any]) -> dict[str, Any]:
    current = replan_ai_input["current"]
    candidates = generate_candidates(
        diagnosis=current["diagnosis"],
        matched_policies=current["matched_policies"],
        monthly_saving=current.get("user", {}).get("monthly_savings"),
    )
    system_prompt, user_prompt = build_replan_prompt(replan_ai_input, candidates)
    result = _call_llm(system_prompt, user_prompt)
    return validate_action_plan(result, candidates=candidates)
