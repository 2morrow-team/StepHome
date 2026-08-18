import logging
import os
import time
from typing import Any

from openai import OpenAIError

from app.ai.planner import AIPlannerError, _fallback_enabled, _get_client
from app.ai.prompts import build_scenario_prompt
from app.ai.schemas import ScenarioRecommendationOutput


logger = logging.getLogger(__name__)


def _call_scenario_llm(
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    started_at = time.monotonic()
    response = _get_client().responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text_format=ScenarioRecommendationOutput,
        reasoning={"effort": os.getenv("OPENAI_REASONING_EFFORT", "low")},
        max_output_tokens=1536,
    )
    if response.output_parsed is None:
        raise ValueError("LLM이 구조화된 Scenario 추천을 반환하지 않았습니다.")
    logger.info(
        "AI Scenario 추천 생성 완료 model=%s elapsed_ms=%d",
        model,
        round((time.monotonic() - started_at) * 1000),
    )
    return response.output_parsed.model_dump(mode="json")


def _validate_recommendation(
    result: dict[str, Any],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    scenario_ids = [scenario["scenario_id"] for scenario in scenarios]
    expected_id = max(
        scenarios,
        key=lambda scenario: scenario["recommendation_score"],
    )["scenario_id"]

    if result.get("recommended_scenario_id") != expected_id:
        raise ValueError("AI 추천 시나리오가 Backend 추천 점수와 일치하지 않습니다.")
    if not isinstance(result.get("summary"), str) or not result["summary"]:
        raise ValueError("AI Scenario 요약이 누락되었습니다.")

    explanations = result.get("explanations")
    if not isinstance(explanations, list):
        raise ValueError("AI Scenario 설명 구조가 올바르지 않습니다.")
    explanation_ids = [item.get("scenario_id") for item in explanations]
    if len(explanation_ids) != len(set(explanation_ids)):
        raise ValueError("AI Scenario 설명이 중복되었습니다.")
    if set(explanation_ids) != set(scenario_ids):
        raise ValueError("AI Scenario 설명 후보가 누락되거나 추가되었습니다.")
    for explanation in explanations:
        if not explanation.get("reason") or not explanation.get("tradeoff"):
            raise ValueError("AI Scenario 설명의 필수 필드가 누락되었습니다.")
    return result


def _fallback_recommendation(
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    recommended = max(
        scenarios,
        key=lambda scenario: scenario["recommendation_score"],
    )
    tradeoffs = {
        "LOWER_DEPOSIT": "선택 가능한 주택의 지역이나 면적 범위가 줄어들 수 있습니다.",
        "DELAY_MOVE_IN": "독립 시점이 늦어져 현재 주거 상태를 더 오래 유지해야 합니다.",
        "INCREASE_SAVINGS": "매달 사용할 수 있는 생활비와 여유자금이 줄어들 수 있습니다.",
    }
    explanations = []
    for scenario in scenarios:
        diagnosis = scenario["diagnosis"]
        policy_change_count = len(scenario["policy_changes"])
        reason = (
            f"준비도는 {diagnosis['readiness_score']}점, 필요 월 저축액은 "
            f"{diagnosis['required_monthly_saving']:,}원입니다."
        )
        if policy_change_count:
            reason += f" 정책 상태 {policy_change_count}건이 개선됩니다."
        explanations.append(
            {
                "scenario_id": scenario["scenario_id"],
                "reason": reason,
                "tradeoff": tradeoffs[scenario["scenario_id"]],
            }
        )
    return {
        "recommended_scenario_id": recommended["scenario_id"],
        "summary": (
            f"{recommended['title']} 시나리오가 선택한 목표에 가장 적합합니다. "
            "계산된 부담과 정책 변화를 함께 비교해 결정하세요."
        ),
        "explanations": explanations,
    }


def generate_scenario_recommendation(
    scenario_ai_input: dict[str, Any],
) -> dict[str, Any]:
    scenarios = scenario_ai_input["scenarios"]
    system_prompt, user_prompt = build_scenario_prompt(scenario_ai_input)
    try:
        result = _call_scenario_llm(system_prompt, user_prompt)
        return _validate_recommendation(result, scenarios)
    except (OpenAIError, RuntimeError, ValueError) as exc:
        if not _fallback_enabled():
            raise AIPlannerError("AI Scenario 추천 생성에 실패했습니다.") from exc
        logger.warning(
            "AI Scenario 추천 fallback 사용 reason=%s",
            type(exc).__name__,
        )
        fallback = _fallback_recommendation(scenarios)
        try:
            return _validate_recommendation(fallback, scenarios)
        except ValueError as fallback_exc:
            raise AIPlannerError(
                "AI Scenario 추천과 안전 fallback 생성에 실패했습니다."
            ) from fallback_exc
