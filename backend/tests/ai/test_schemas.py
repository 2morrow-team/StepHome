import pytest
from pydantic import ValidationError

from app.ai.schemas import ActionPlanOutput
from tests.ai.fixtures import VALID_ACTION_PLAN


def test_valid_action_plan_matches_structured_output_schema():
    output = ActionPlanOutput.model_validate(VALID_ACTION_PLAN)

    assert output.summary == VALID_ACTION_PLAN["summary"]
    assert len(output.actions) == len(VALID_ACTION_PLAN["actions"])


def test_structured_output_rejects_unknown_action_type():
    invalid = {
        "summary": "잘못된 Action 유형을 포함한 계획입니다.",
        "actions": [
            {
                "priority": 1,
                "action_type": "UNKNOWN",
                "timing": "NOW",
                "title": "잘못된 행동",
                "description": "허용되지 않은 행동입니다.",
                "reason": "테스트용입니다.",
                "policy_id": None,
                "due_date": None,
            }
        ],
    }

    with pytest.raises(ValidationError):
        ActionPlanOutput.model_validate(invalid)


def test_structured_output_rejects_extra_backend_field():
    invalid = {
        "summary": "백엔드 필드를 포함한 계획입니다.",
        "actions": [
            {
                "priority": 1,
                "action_type": "SAVING",
                "timing": "NOW",
                "title": "월 저축 유지",
                "description": "현재 저축 계획을 유지합니다.",
                "reason": "목표 달성을 위해 필요합니다.",
                "policy_id": None,
                "due_date": None,
                "action_id": 1,
            }
        ],
    }

    with pytest.raises(ValidationError):
        ActionPlanOutput.model_validate(invalid)
