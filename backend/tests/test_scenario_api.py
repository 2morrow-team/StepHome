from fastapi.testclient import TestClient

from app.ai import planner
from app.main import app


def _create_plan(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/plan",
        json={
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
        },
    )
    assert response.status_code == 200
    return response.json()


def _scenario_request(plan: dict, priority: str) -> dict:
    return {
        "user_id": plan["user_id"],
        "target_id": plan["target_id"],
        "previous_diagnosis_id": plan["diagnosis_id"],
        "previous_plan_id": plan["plan_id"],
        "priority": priority,
        "constraints": {
            "minimum_desired_deposit": 70_000_000,
            "max_additional_monthly_savings": 500_000,
            "max_move_delay_months": 6,
        },
    }


def test_policy_priority_recommends_policy_improving_scenario(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(planner, "_client", None)
    client = TestClient(app)
    plan = _create_plan(client)

    response = client.post(
        "/api/v1/scenarios",
        json=_scenario_request(plan, "POLICY_BENEFIT"),
    )

    assert response.status_code == 200
    result = response.json()
    assert result["recommended_scenario_id"] == "LOWER_DEPOSIT"
    assert len(result["scenarios"]) == 3
    assert result["recommended_scenario_id"] == max(
        result["scenarios"],
        key=lambda scenario: scenario["recommendation_score"],
    )["scenario_id"]

    lower_deposit = next(
        scenario
        for scenario in result["scenarios"]
        if scenario["scenario_id"] == "LOWER_DEPOSIT"
    )
    assert lower_deposit["changes"] == {"desired_deposit": 70_000_000}
    assert lower_deposit["diagnosis"]["required_monthly_saving"] < (
        plan["diagnosis"]["required_monthly_saving"]
    )
    policy_change = next(
        change
        for change in lower_deposit["policy_changes"]
        if change["policy_id"] == 6
    )
    assert policy_change["before_status"] == "CONDITIONAL"
    assert policy_change["after_status"] == "AVAILABLE"

    replan_response = client.post(
        "/api/v1/replan",
        json={
            "user_id": plan["user_id"],
            "target_id": plan["target_id"],
            "previous_diagnosis_id": plan["diagnosis_id"],
            "previous_plan_id": plan["plan_id"],
            "changes": lower_deposit["changes"],
        },
    )
    assert replan_response.status_code == 200
    replanned_policy = next(
        policy
        for policy in replan_response.json()["current"]["matched_policies"]
        if policy["policy_id"] == 6
    )
    assert replanned_policy["eligibility_status"] == "AVAILABLE"


def test_goal_priority_changes_recommended_scenario(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setattr(planner, "_client", None)
    client = TestClient(app)
    plan = _create_plan(client)
    expected_by_priority = {
        "FAST_MOVE": "INCREASE_SAVINGS",
        "LOW_MONTHLY_BURDEN": "DELAY_MOVE_IN",
        "POLICY_BENEFIT": "LOWER_DEPOSIT",
    }

    for priority, expected_scenario_id in expected_by_priority.items():
        response = client.post(
            "/api/v1/scenarios",
            json=_scenario_request(plan, priority),
        )

        assert response.status_code == 200
        assert response.json()["recommended_scenario_id"] == expected_scenario_id


def test_scenario_request_rejects_unknown_fields():
    client = TestClient(app)
    response = client.post(
        "/api/v1/scenarios",
        json={
            "user_id": 1,
            "target_id": 1,
            "previous_diagnosis_id": 1,
            "previous_plan_id": 1,
            "priority": "POLICY_BENEFIT",
            "constraints": {"deposit_budget": 70_000_000},
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INPUT"


def test_scenario_request_rejects_when_no_change_can_be_generated(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    client = TestClient(app)
    plan = _create_plan(client)
    request = _scenario_request(plan, "LOW_MONTHLY_BURDEN")
    request["constraints"] = {
        "minimum_desired_deposit": 90_000_000,
        "max_additional_monthly_savings": 0,
        "max_move_delay_months": 0,
    }

    response = client.post("/api/v1/scenarios", json=request)

    assert response.status_code == 422
    assert "생성 가능한 시나리오" in response.json()["error"]["message"]
