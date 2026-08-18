from types import SimpleNamespace

import pytest

from app.ai import scenario_planner
from app.ai.schemas import ScenarioRecommendationOutput


SCENARIOS = [
    {
        "scenario_id": "LOWER_DEPOSIT",
        "title": "희망 보증금 낮추기",
        "changes": {"desired_deposit": 70_000_000},
        "diagnosis": {
            "readiness_score": 33,
            "required_monthly_saving": 5_700_000,
        },
        "policy_changes": [],
        "recommendation_score": 70,
    },
    {
        "scenario_id": "DELAY_MOVE_IN",
        "title": "입주 예정일 미루기",
        "changes": {"planned_move_in_date": "2027-09-01"},
        "diagnosis": {
            "readiness_score": 27,
            "required_monthly_saving": 4_600_000,
        },
        "policy_changes": [],
        "recommendation_score": 80,
    },
]


def _ai_input() -> dict:
    return {
        "priority": "LOW_MONTHLY_BURDEN",
        "recommended_scenario_id": "DELAY_MOVE_IN",
        "baseline": {"diagnosis": {}, "policies": []},
        "scenarios": SCENARIOS,
    }


def test_call_scenario_llm_uses_structured_output_schema(monkeypatch):
    captured = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                output_parsed=ScenarioRecommendationOutput.model_validate(
                    {
                        "recommended_scenario_id": "DELAY_MOVE_IN",
                        "summary": "입주 연기가 월 부담을 가장 많이 낮춥니다.",
                        "explanations": [
                            {
                                "scenario_id": "LOWER_DEPOSIT",
                                "reason": "필요 자금이 줄어듭니다.",
                                "tradeoff": "선택 가능한 주택이 줄 수 있습니다.",
                            },
                            {
                                "scenario_id": "DELAY_MOVE_IN",
                                "reason": "필요 월 저축액이 가장 낮습니다.",
                                "tradeoff": "독립 시점이 늦어집니다.",
                            },
                        ],
                    }
                )
            )

    fake_client = SimpleNamespace(responses=FakeResponses())
    monkeypatch.setattr(scenario_planner, "_get_client", lambda: fake_client)

    result = scenario_planner._call_scenario_llm("system", "user")

    assert captured["model"] == "gpt-5.6-terra"
    assert captured["text_format"] is ScenarioRecommendationOutput
    assert captured["reasoning"] == {"effort": "low"}
    assert result["recommended_scenario_id"] == "DELAY_MOVE_IN"


def test_invalid_ai_recommendation_is_replaced_by_safe_fallback(monkeypatch):
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(
        scenario_planner,
        "_call_scenario_llm",
        lambda *_args: {
            "recommended_scenario_id": "LOWER_DEPOSIT",
            "summary": "잘못된 추천",
            "explanations": [],
        },
    )

    result = scenario_planner.generate_scenario_recommendation(_ai_input())

    assert result["recommended_scenario_id"] == "DELAY_MOVE_IN"
    assert {item["scenario_id"] for item in result["explanations"]} == {
        "LOWER_DEPOSIT",
        "DELAY_MOVE_IN",
    }


def test_invalid_ai_recommendation_fails_when_fallback_is_disabled(monkeypatch):
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    monkeypatch.setattr(
        scenario_planner,
        "_call_scenario_llm",
        lambda *_args: {
            "recommended_scenario_id": "LOWER_DEPOSIT",
            "summary": "잘못된 추천",
            "explanations": [],
        },
    )

    with pytest.raises(scenario_planner.AIPlannerError):
        scenario_planner.generate_scenario_recommendation(_ai_input())
