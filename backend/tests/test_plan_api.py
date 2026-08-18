from fastapi.testclient import TestClient

from app.ai import planner
from app.main import app
from app.services.plan_service import _sanitize_ai_output


def _plan_payload() -> dict:
    return {
        "user": {
            "age": 25,
            "current_region": "SEOUL",
            "employment_status": "EMPLOYED",
            "marital_status": "UNMARRIED",
            "youth_household_monthly_income": 2_500_000,
            "youth_household_size": 1,
            "personal_monthly_income": 2_500_000,
            "total_assets": 30_000_000,
            "monthly_savings": 500_000,
            "housing_status": "NO_HOME",
        },
        "target": {
            "planned_move_in_date": "2027-03-01",
            "desired_region": "SEOUL",
            "desired_deposit": 90_000_000,
            "desired_monthly_rent": 500_000,
            "desired_housing_type": "MONTHLY_RENT",
        },
    }


def test_plan_to_replan_flow_works_with_safe_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(planner, "_client", None)
    client = TestClient(app)

    plan_response = client.post("/api/v1/plan", json=_plan_payload())

    assert plan_response.status_code == 200
    plan = plan_response.json()
    assert plan["action_plan"]["actions"]
    before_policy = next(
        policy for policy in plan["matched_policies"] if policy["policy_id"] == 6
    )
    assert before_policy["eligibility_status"] == "CONDITIONAL"

    replan_response = client.post(
        "/api/v1/replan",
        json={
            "user_id": plan["user_id"],
            "target_id": plan["target_id"],
            "previous_diagnosis_id": plan["diagnosis_id"],
            "previous_plan_id": plan["plan_id"],
            "changes": {
                "desired_deposit": 70_000_000,
                "monthly_savings": 1_000_000,
            },
        },
    )

    assert replan_response.status_code == 200
    replanned = replan_response.json()
    assert set(replanned["changed_fields"]) == {
        "desired_deposit",
        "monthly_savings",
    }
    assert replanned["current"]["target"]["desired_deposit"] == 70_000_000
    assert (
        replanned["current"]["diagnosis"]["saving_score"]
        > replanned["previous"]["diagnosis"]["saving_score"]
    )
    after_policy = next(
        policy
        for policy in replanned["current"]["matched_policies"]
        if policy["policy_id"] == 6
    )
    assert after_policy["eligibility_status"] == "AVAILABLE"
    user_facing_text = " ".join(
        [
            replanned["current"]["action_plan"]["summary"],
            *[
                action["description"] + " " + action["reason"]
                for action in replanned["current"]["action_plan"]["actions"]
            ],
        ]
    )
    assert "CONDITIONAL" not in user_facing_text
    assert "AVAILABLE" not in user_facing_text
    assert "desired_deposit" not in user_facing_text
    assert "조건 조정 필요→신청 가능" in user_facing_text
    assert replanned["current"]["action_plan"]["actions"]


def test_ai_failure_uses_stable_503_contract(monkeypatch):
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    monkeypatch.setattr(
        planner,
        "_call_llm",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("API unavailable")),
    )
    client = TestClient(app)

    response = client.post("/api/v1/plan", json=_plan_payload())

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AI_TEMPORARILY_UNAVAILABLE"


def test_ai_output_text_replaces_internal_codes_with_user_labels():
    result = _sanitize_ai_output(
        {
            "summary": "desired_deposit 변경 후 CONDITIONAL > AVAILABLE",
            "actions": [
                {
                    "title": "planned_move_in_date 확인",
                    "description": "NEED_MORE_INFO 상태를 확인합니다.",
                    "reason": "NOT_ELIGIBLE에서 CONDITIONAL로 변경되었습니다.",
                }
            ],
        }
    )

    user_facing_text = " ".join(
        [
            result["summary"],
            result["actions"][0]["title"],
            result["actions"][0]["description"],
            result["actions"][0]["reason"],
        ]
    )

    assert "desired_deposit" not in user_facing_text
    assert "planned_move_in_date" not in user_facing_text
    assert "CONDITIONAL" not in user_facing_text
    assert "AVAILABLE" not in user_facing_text
    assert "NEED_MORE_INFO" not in user_facing_text
    assert "NOT_ELIGIBLE" not in user_facing_text
    assert "희망 보증금" in user_facing_text
    assert "입주 예정일" in user_facing_text
    assert "조건 조정 필요 > 신청 가능" in user_facing_text


def test_past_move_in_date_uses_user_friendly_error_message(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    client = TestClient(app)
    payload = _plan_payload()
    payload["target"]["planned_move_in_date"] = "2020-01-01"

    response = client.post("/api/v1/plan", json=payload)

    assert response.status_code == 422
    message = response.json()["error"]["message"]
    assert message == "입주 예정일은 오늘보다 이후 날짜로 선택해주세요."
    assert "planned_move_in_date" not in message


def test_validation_error_uses_user_friendly_field_label():
    client = TestClient(app)
    payload = _plan_payload()
    payload["target"]["desired_deposit"] = -1

    response = client.post("/api/v1/plan", json=payload)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["message"] == "희망 보증금은 0 이상으로 입력해주세요."
    assert error["details"] == [
        {
            "field": "희망 보증금",
            "reason": "희망 보증금은 0 이상으로 입력해주세요.",
        }
    ]
