import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.ai.candidate_generator import generate_candidates
from app.ai.fallback import build_fallback_action_plan
from app.ai.prompts import build_plan_prompt, build_replan_prompt
from app.ai.schemas import ActionPlanOutput
from app.ai.validator import validate_action_plan

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env", override=False)

_client: Optional[OpenAI] = None
logger = logging.getLogger(__name__)


class AIPlannerError(RuntimeError):
    """AI와 fallback 모두 Action Plan을 만들지 못한 경우."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        _client = OpenAI(
            api_key=api_key,
            timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        )
    return _client


def _call_llm(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """LLM API 호출을 담당하는 유일한 함수. 모델 교체 시 이 함수만 수정한다."""
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    started_at = time.monotonic()
    response = _get_client().responses.parse(
        model=model,
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
    logger.info(
        "AI Action Plan 생성 완료 model=%s elapsed_ms=%d",
        model,
        round((time.monotonic() - started_at) * 1000),
    )
    return response.output_parsed.model_dump(mode="json")


def _fallback_enabled() -> bool:
    return os.getenv("AI_FALLBACK_ENABLED", "true").lower() not in {
        "0",
        "false",
        "no",
    }


def _generate_and_validate(
    system_prompt: str,
    user_prompt: str,
    candidates: list,
    replan_input: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    try:
        result = _call_llm(system_prompt, user_prompt)
        return validate_action_plan(
            result,
            candidates=candidates,
            require_all_candidates=True,
        )
    except (OpenAIError, RuntimeError, ValueError) as exc:
        if not _fallback_enabled():
            raise AIPlannerError("AI Action Plan 생성에 실패했습니다.") from exc

        logger.warning(
            "AI Action Plan fallback 사용 reason=%s",
            type(exc).__name__,
        )
        fallback = build_fallback_action_plan(
            candidates,
            replan_input=replan_input,
        )
        try:
            return validate_action_plan(
                fallback,
                candidates=candidates,
                require_all_candidates=True,
            )
        except ValueError as fallback_exc:
            raise AIPlannerError(
                "AI Action Plan과 안전 fallback 생성에 실패했습니다."
            ) from fallback_exc


def generate_action_plan(ai_input: dict[str, Any]) -> dict[str, Any]:
    candidates = generate_candidates(
        diagnosis=ai_input["diagnosis"],
        matched_policies=ai_input["matched_policies"],
        monthly_saving=ai_input.get("user", {}).get("monthly_savings"),
    )
    system_prompt, user_prompt = build_plan_prompt(ai_input, candidates)
    return _generate_and_validate(system_prompt, user_prompt, candidates)


def generate_replan_action_plan(replan_ai_input: dict[str, Any]) -> dict[str, Any]:
    current = replan_ai_input["current"]
    candidates = generate_candidates(
        diagnosis=current["diagnosis"],
        matched_policies=current["matched_policies"],
        monthly_saving=current.get("user", {}).get("monthly_savings"),
    )
    system_prompt, user_prompt = build_replan_prompt(replan_ai_input, candidates)
    return _generate_and_validate(
        system_prompt,
        user_prompt,
        candidates,
        replan_input=replan_ai_input,
    )
