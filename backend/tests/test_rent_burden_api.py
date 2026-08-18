from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rent_burden_calculator_returns_expected_result():
    response = client.post(
        "/api/v1/calculators/rent-burden",
        json={
            "personal_monthly_income": 2_500_000,
            "desired_monthly_rent": 600_000,
            "monthly_management_fee": 100_000,
            "monthly_living_expense": 700_000,
            "target_monthly_savings": 500_000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["rent_burden_ratio"] == 24.0

    assert (
        result["monthly_housing_cost"]
        == 700_000
    )

    assert (
        result["estimated_monthly_balance"]
        == 600_000
    )


def test_rent_burden_calculator_allows_negative_balance():
    response = client.post(
        "/api/v1/calculators/rent-burden",
        json={
            "personal_monthly_income": 2_000_000,
            "desired_monthly_rent": 900_000,
            "monthly_management_fee": 200_000,
            "monthly_living_expense": 700_000,
            "target_monthly_savings": 500_000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert (
        result["estimated_monthly_balance"]
        == -300_000
    )


def test_rent_burden_calculator_rejects_zero_income():
    response = client.post(
        "/api/v1/calculators/rent-burden",
        json={
            "personal_monthly_income": 0,
            "desired_monthly_rent": 600_000,
            "monthly_management_fee": 100_000,
            "monthly_living_expense": 700_000,
            "target_monthly_savings": 500_000,
        },
    )

    assert response.status_code == 422

    assert (
        response.json()["error"]["code"]
        == "INVALID_INPUT"
    )


def test_rent_burden_calculator_rejects_unknown_field():
    response = client.post(
        "/api/v1/calculators/rent-burden",
        json={
            "personal_monthly_income": 2_500_000,
            "desired_monthly_rent": 600_000,
            "monthly_management_fee": 100_000,
            "monthly_living_expense": 700_000,
            "target_monthly_savings": 500_000,
            "unknown_field": 123,
        },
    )

    assert response.status_code == 422

    assert (
        response.json()["error"]["code"]
        == "INVALID_INPUT"
    )
