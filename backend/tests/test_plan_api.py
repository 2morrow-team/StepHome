from fastapi.testclient import TestClient

from app.ai import planner
from app.main import app


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
