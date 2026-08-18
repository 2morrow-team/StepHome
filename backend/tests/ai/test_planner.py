from types import SimpleNamespace

import pytest

from app.ai import planner
from app.ai.schemas import ActionPlanOutput
from tests.ai.fixtures import DIAGNOSIS


def test_plan_uses_actual_monthly_saving_field(monkeypatch):
    captured = {}

    def fake_call_llm(system_prompt, user_prompt):
        captured["user_prompt"] = user_prompt
        return {
            "summary": "현재 저축액을 조정하고 계약 전 안전사항을 확인하세요.",
            "actions": [
                {
                    "priority": 1,
                    "action_type": "SAVING",
                    "timing": "NOW",
                    "title": "월 저축액 조정",
                    "description": "월 저축액을 필요한 수준으로 조정합니다.",
                    "reason": "현재 저축액이 목표 달성에 필요한 금액보다 적습니다.",
                    "policy_id": None,
                    "due_date": None,
                },
                {
                    "priority": 2,
                    "action_type": "CONTRACT",
                    "timing": "BEFORE_CONTRACT",
                    "title": "계약 안전 확인",
                    "description": "계약 전 등기부등본과 보증보험 가입 여부를 확인합니다.",
                    "reason": "계약 위험을 줄이기 위해 필요합니다.",
                    "policy_id": None,
                    "due_date": None,
                },
            ],
        }

    monkeypatch.setattr(planner, "_call_llm", fake_call_llm)
    ai_input = {
        "user": {"monthly_savings": 300_000},
        "target": {},
        "diagnosis": DIAGNOSIS,
        "matched_policies": [],
    }

    result = planner.generate_action_plan(ai_input)

    assert "SAVING_ADJUST" in captured["user_prompt"]
    assert result["actions"][0]["action_type"] == "SAVING"


def test_call_llm_uses_structured_output_schema(monkeypatch):
    captured = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                output_parsed=ActionPlanOutput.model_validate(
                    {
                        "summary": "현재 저축 계획을 유지하세요.",
                        "actions": [
                            {
                                "priority": 1,
                                "action_type": "SAVING",
                                "timing": "NOW",
                                "title": "월 저축계획 유지",
                                "description": "현재 저축 계획을 유지합니다.",
                                "reason": "목표 저축액을 충족하고 있습니다.",
                                "policy_id": None,
                                "due_date": None,
                            }
                        ],
                    }
                )
            )

    fake_client = SimpleNamespace(responses=FakeResponses())
    monkeypatch.setattr(planner, "_get_client", lambda: fake_client)

    result = planner._call_llm("system", "user")

    assert captured["model"] == "gpt-5.6-terra"
    assert captured["text_format"] is ActionPlanOutput
    assert captured["reasoning"] == {"effort": "low"}
    assert result["actions"][0]["due_date"] is None


def test_call_llm_rejects_missing_parsed_output(monkeypatch):
    class FakeResponses:
        def parse(self, **kwargs):
            return SimpleNamespace(output_parsed=None)

    fake_client = SimpleNamespace(responses=FakeResponses())
    monkeypatch.setattr(planner, "_get_client", lambda: fake_client)

    with pytest.raises(ValueError, match="구조화된 ActionPlan"):
        planner._call_llm("system", "user")


def test_get_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(planner, "_client", None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        planner._get_client()
