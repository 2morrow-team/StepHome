from datetime import date

from app.policy.rule_engine import match_policies
from app.schemas.schemas import EligibilityStatus, PolicyMatchResponse


def _make_user():
    return {
        "user_id": 1,
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
    }


def _make_target():
    return {
        "target_id": 1,
        "user_id": 1,
        "planned_move_in_date": date(2027, 3, 1),
        "desired_monthly_rent": 500_000,
        "desired_deposit": 90_000_000,
        "desired_housing_type": "MONTHLY_RENT",
        "desired_region": "SEOUL",
    }


def test_current_policy_data_matches_without_key_error():
    matches = match_policies(_make_user(), _make_target(), diagnosis_id=1, first_match_id=1)

    assert matches
    assert all(match["application_period_type"] for match in matches)
    assert all(match["eligibility_status"] in EligibilityStatus for match in matches)


def test_policy_matches_fit_response_schema():
    matches = match_policies(_make_user(), _make_target(), diagnosis_id=1, first_match_id=1)

    for match in matches:
        PolicyMatchResponse(**match)
