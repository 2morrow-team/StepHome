# AI 프롬프트 정의
from typing import Any


def build_ai_input(
    user: dict[str, Any],
    target: dict[str, Any],
    diagnosis: dict[str, Any],
    matched_policies: list[dict[str, Any]],
) -> dict[str, Any]:
    user_context_fields = (
        "age",
        "region",
        "employment_status",
        "monthly_income",
        "current_housing_cost",
        "current_housing_type",
        "monthly_living_expense",
        "monthly_fixed_expense",
        "monthly_saving",
        "current_savings",
        "current_emergency_fund",
        "debt",
    )
    target_context_fields = (
        "target_date",
        "monthly_rent_budget",
        "deposit_budget",
        "housing_type",
        "target_region",
        "housing_preference",
    )
    diagnosis_context_fields = (
        "readiness_score",
        "fund_score",
        "saving_score",
        "emergency_score",
        "required_initial_fund",
        "initial_fund_gap",
        "target_emergency_fund",
        "emergency_fund_gap",
        "required_monthly_saving",
        "estimated_months",
    )
    policy_context_fields = (
        "policy_id",
        "title",
        "eligibility_status",
        "matched_conditions",
        "failed_conditions",
        "missing_conditions",
        "rank",
        "support_amount",
        "support_amount_text",
        "eligibility_text",
        "description",
        "application_start",
        "application_end",
        "region",
        "provider",
        "category",
        "source_url",
        "checked_at",
    )
    return {
        "user_id": user["user_id"],
        "target_id": target["target_id"],
        "diagnosis_id": diagnosis["diagnosis_id"],
        "user": {field: user[field] for field in user_context_fields if field in user},
        "target": {field: target[field] for field in target_context_fields if field in target},
        "diagnosis": {field: diagnosis[field] for field in diagnosis_context_fields},
        "matched_policies": [
            {field: policy[field] for field in policy_context_fields}
            for policy in matched_policies
        ],
    }
