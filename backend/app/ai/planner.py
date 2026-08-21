import logging
import os
import time
from datetime import date, timedelta
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


def _calc_phase_deadlines(move_in_date: date, today: Optional[date] = None) -> dict[int, str]:
    today = today or date.today()
    total_days = (move_in_date - today).days
    if total_days <= 0:
        # 입주 예정일이 과거이면 오늘부터 90일 기준으로 phase 분배
        total_days = 90
        move_in_date = today + timedelta(days=90)
    return {
        1: str(today + timedelta(days=total_days // 4)),
        2: str(today + timedelta(days=total_days // 2)),
        3: str(today + timedelta(days=total_days * 3 // 4)),
        4: str(move_in_date),
    }


def _extract_move_in_date(ai_input: dict[str, Any]) -> Optional[date]:
    raw = ai_input.get("target", {}).get("planned_move_in_date")
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    try:
        return date.fromisoformat(str(raw))
    except ValueError:
        return None


def _inject_phase_due_dates(plan: dict[str, Any], phase_deadlines: dict[int, str]) -> dict[str, Any]:
    for action in plan.get("actions", []):
        phase = action.get("phase")
        if isinstance(phase, int) and phase in phase_deadlines:
            action["due_date"] = phase_deadlines[phase]
    return plan


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
    max_attempts = int(os.getenv("AI_MAX_ATTEMPTS", "2"))
    last_exc: Exception = RuntimeError("AI 호출 시도 없음")

    for attempt in range(1, max_attempts + 1):
        try:
            result = _call_llm(system_prompt, user_prompt)
            return validate_action_plan(
                result,
                candidates=candidates,
                require_all_candidates=True,
            )
        except ValueError as exc:
            last_exc = exc
            logger.warning(
                "AI Action Plan 검증 실패 attempt=%d/%d reason=%s",
                attempt,
                max_attempts,
                exc,
            )
        except (OpenAIError, RuntimeError) as exc:
            last_exc = exc
            logger.warning(
                "AI Action Plan 호출 실패 attempt=%d/%d reason=%s",
                attempt,
                max_attempts,
                type(exc).__name__,
            )
            break  # OpenAI 클라이언트가 이미 내부 재시도를 처리하므로 즉시 중단

    if not _fallback_enabled():
        raise AIPlannerError("AI Action Plan 생성에 실패했습니다.") from last_exc

    logger.warning("AI Action Plan fallback 사용 reason=%s", type(last_exc).__name__)
    fallback = build_fallback_action_plan(candidates, replan_input=replan_input)
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
    move_in_date = _extract_move_in_date(ai_input)
    phase_deadlines = _calc_phase_deadlines(move_in_date) if move_in_date else None
    system_prompt, user_prompt = build_plan_prompt(ai_input, candidates, phase_deadlines)
    plan = _generate_and_validate(system_prompt, user_prompt, candidates)
    if phase_deadlines:
        plan = _inject_phase_due_dates(plan, phase_deadlines)
    return plan


def generate_replan_action_plan(replan_ai_input: dict[str, Any]) -> dict[str, Any]:
    current = replan_ai_input["current"]
    candidates = generate_candidates(
        diagnosis=current["diagnosis"],
        matched_policies=current["matched_policies"],
        monthly_saving=current.get("user", {}).get("monthly_savings"),
    )
    move_in_date = _extract_move_in_date({"target": current.get("target", {})})
    phase_deadlines = _calc_phase_deadlines(move_in_date) if move_in_date else None
    system_prompt, user_prompt = build_replan_prompt(replan_ai_input, candidates, phase_deadlines)
    plan = _generate_and_validate(
        system_prompt,
        user_prompt,
        candidates,
        replan_input=replan_ai_input,
    )
    if phase_deadlines:
        plan = _inject_phase_due_dates(plan, phase_deadlines)
    return plan
