import json
import pytest
from app.ai.candidate_generator import generate_candidates
from app.ai.prompts import (
    build_plan_prompt,
    build_replan_prompt,
    build_ai_input,
    build_replan_ai_input,
)
from tests.ai.fixtures import (
    AI_INPUT,
    DIAGNOSIS,
    POLICY_AVAILABLE,
    POLICY_CONDITIONAL,
    VALID_ACTION_PLAN,
)


def _make_candidates():
    return generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE, POLICY_CONDITIONAL], monthly_saving=500000)


class TestBuildPlanPrompt:
    def test_returns_two_strings(self):
        candidates = _make_candidates()
        system, user = build_plan_prompt(AI_INPUT, candidates)
        assert isinstance(system, str)
        assert isinstance(user, str)

    def test_system_prompt_not_empty(self):
        candidates = _make_candidates()
        system, _ = build_plan_prompt(AI_INPUT, candidates)
        assert len(system) > 0

    def test_user_prompt_contains_json(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert "diagnosis" in user or "user" in user

    def test_user_prompt_contains_candidates(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert "SAVING" in user

    def test_user_prompt_contains_action_rules(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert "action_type" in user

    def test_conditional_with_missing_info_prevents_eligibility_overstatement(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert "missing_conditions" in user

    def test_user_prompt_contains_output_format(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert "summary" in user
        assert "actions" in user

    def test_policy_id_in_candidate_line(self):
        candidates = _make_candidates()
        _, user = build_plan_prompt(AI_INPUT, candidates)
        assert f"policy_id={POLICY_AVAILABLE['policy_id']}" in user


class TestBuildReplanPrompt:
    def _make_replan_input(self):
        changed_fields = {"deposit_budget": 8000000}
        current_diagnosis = dict(DIAGNOSIS, required_monthly_saving=600000)
        return build_replan_ai_input(
            changed_fields=changed_fields,
            previous_diagnosis=DIAGNOSIS,
            previous_policies=[POLICY_AVAILABLE],
            previous_actions=VALID_ACTION_PLAN["actions"],
            current_diagnosis=current_diagnosis,
            current_policies=[POLICY_AVAILABLE, POLICY_CONDITIONAL],
        )

    def test_returns_two_strings(self):
        replan_input = self._make_replan_input()
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE, POLICY_CONDITIONAL])
        system, user = build_replan_prompt(replan_input, candidates)
        assert isinstance(system, str)
        assert isinstance(user, str)

    def test_user_prompt_contains_changed_fields(self):
        replan_input = self._make_replan_input()
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        _, user = build_replan_prompt(replan_input, candidates)
        assert "changed_fields" in user or "deposit_budget" in user

    def test_user_prompt_contains_previous_and_current(self):
        replan_input = self._make_replan_input()
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        _, user = build_replan_prompt(replan_input, candidates)
        assert "previous" in user
        assert "current" in user

    def test_replan_extra_rules_present(self):
        replan_input = self._make_replan_input()
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        _, user = build_replan_prompt(replan_input, candidates)
        assert "summary" in user


class TestBuildAiInput:
    def _make_user(self):
        return {
            "user_id": 1,
            "age": 25,
            "current_region": "SEOUL",
            "employment_status": "EMPLOYED",
            "marital_status": "UNMARRIED",
            "youth_household_monthly_income": 2500000,
            "youth_household_size": 1,
            "personal_monthly_income": 2500000,
            "total_assets": 30000000,
            "monthly_savings": 500000,
            "housing_status": "NO_HOME",
            "some_internal_field": "should_be_excluded",
        }

    def _make_target(self):
        return {
            "target_id": 1,
            "planned_move_in_date": "2027-03-01",
            "desired_region": "SEOUL",
            "desired_deposit": 90000000,
            "desired_monthly_rent": 500000,
            "desired_housing_type": "MONTHLY_RENT",
        }

    def test_returns_dict(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [POLICY_AVAILABLE])
        assert isinstance(result, dict)

    def test_internal_fields_excluded(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [])
        assert "some_internal_field" not in result["user"]

    def test_user_context_fields_present(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [])
        for field in ("age", "current_region", "employment_status", "marital_status",
                      "youth_household_monthly_income", "youth_household_size",
                      "personal_monthly_income", "total_assets", "monthly_savings",
                      "housing_status"):
            assert field in result["user"]

    def test_target_context_fields_present(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [])
        for field in ("planned_move_in_date", "desired_region", "desired_deposit",
                      "desired_monthly_rent", "desired_housing_type"):
            assert field in result["target"]

    def test_no_emergency_fund_fields_in_diagnosis(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [])
        for field in ("emergency_score", "target_emergency_fund", "emergency_fund_gap"):
            assert field not in result["diagnosis"]

    def test_policy_context_includes_application_period_type(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [POLICY_AVAILABLE])
        assert "application_period_type" in result["matched_policies"][0]

    def test_policy_context_includes_policy_metadata(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [POLICY_AVAILABLE])
        policy = result["matched_policies"][0]

        for field in ("policy_category", "policy_region", "policy_provider", "support_amount_unit"):
            assert policy[field] == POLICY_AVAILABLE[field]

    def test_policy_context_includes_condition_details(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [POLICY_CONDITIONAL])

        assert result["matched_policies"][0]["condition_details"] == POLICY_CONDITIONAL["condition_details"]

    def test_matched_policies_list_length(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [POLICY_AVAILABLE, POLICY_CONDITIONAL])
        assert len(result["matched_policies"]) == 2

    def test_ids_carried_over(self):
        result = build_ai_input(self._make_user(), self._make_target(), DIAGNOSIS, [])
        assert result["user_id"] == 1
        assert result["target_id"] == 1
        assert result["diagnosis_id"] == DIAGNOSIS["diagnosis_id"]


class TestBuildReplanAiInput:
    def test_returns_changed_fields(self):
        changed = {"deposit_budget": 8000000}
        result = build_replan_ai_input(changed, DIAGNOSIS, [POLICY_AVAILABLE], [], DIAGNOSIS, [POLICY_AVAILABLE])
        assert result["changed_fields"] == changed

    def test_has_previous_and_current_keys(self):
        result = build_replan_ai_input({}, DIAGNOSIS, [], [], DIAGNOSIS, [])
        assert "previous" in result
        assert "current" in result

    def test_previous_actions_filtered(self):
        actions = VALID_ACTION_PLAN["actions"]
        result = build_replan_ai_input({}, DIAGNOSIS, [], actions, DIAGNOSIS, [])
        for action in result["previous"]["actions"]:
            assert "status" not in action
            assert "action_id" not in action

    def test_previous_policies_filtered(self):
        result = build_replan_ai_input({}, DIAGNOSIS, [POLICY_AVAILABLE], [], DIAGNOSIS, [])
        policy = result["previous"]["matched_policies"][0]
        assert "policy_id" in policy
        assert "eligibility_status" in policy
        assert policy["condition_details"] == POLICY_AVAILABLE["condition_details"]

    def test_current_user_and_target_are_included(self):
        user = TestBuildAiInput()._make_user()
        target = TestBuildAiInput()._make_target()
        result = build_replan_ai_input(
            {}, DIAGNOSIS, [], [], DIAGNOSIS, [],
            current_user=user, current_target=target,
        )
        assert result["current"]["user"]["monthly_savings"] == 500000
        assert result["current"]["target"]["desired_deposit"] == 90000000
