import copy

import pytest
from app.ai.candidate_generator import generate_candidates
from app.ai.schemas import CandidateBasis
from tests.ai.fixtures import (
    DIAGNOSIS,
    POLICY_AVAILABLE,
    POLICY_CONDITIONAL,
    POLICY_NEED_MORE_INFO,
    POLICY_NOT_ELIGIBLE,
)


class TestSavingCandidate:
    def test_saving_maintain_when_sufficient(self):
        candidates = generate_candidates(DIAGNOSIS, [], monthly_saving=9000000)
        saving = next(c for c in candidates if c.action_type == "SAVING")
        assert saving.basis == CandidateBasis.SAVING_MAINTAIN

    def test_saving_adjust_when_insufficient(self):
        candidates = generate_candidates(DIAGNOSIS, [], monthly_saving=300000)
        saving = next(c for c in candidates if c.action_type == "SAVING")
        assert saving.basis == CandidateBasis.SAVING_ADJUST

    def test_saving_maintain_when_monthly_saving_unknown(self):
        candidates = generate_candidates(DIAGNOSIS, [], monthly_saving=None)
        saving = next(c for c in candidates if c.action_type == "SAVING")
        assert saving.basis == CandidateBasis.SAVING_MAINTAIN

    def test_saving_context_contains_required_monthly_saving(self):
        candidates = generate_candidates(DIAGNOSIS, [], monthly_saving=500000)
        saving = next(c for c in candidates if c.action_type == "SAVING")
        assert saving.context["required_monthly_saving"] == DIAGNOSIS["required_monthly_saving"]


class TestPolicyCandidates:
    def test_available_policy_generates_policy_apply(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        policy_candidates = [c for c in candidates if c.action_type == "POLICY"]
        assert any(c.basis == CandidateBasis.POLICY_APPLY for c in policy_candidates)

    def test_conditional_policy_generates_condition_adjust(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_CONDITIONAL])
        housing_candidates = [c for c in candidates if c.action_type == "HOUSING"]
        assert any(c.basis == CandidateBasis.CONDITION_ADJUST for c in housing_candidates)

    def test_non_housing_conditional_policy_generates_policy_action(self):
        policy = copy.deepcopy(POLICY_CONDITIONAL)
        policy["failed_conditions"] = ["INCOME"]
        policy["condition_details"] = [
            {
                "condition": "INCOME",
                "result": "FAILED",
                "current_value": 5000000,
                "required_max": 3000000,
                "message": "소득 기준을 초과합니다.",
            }
        ]

        candidates = generate_candidates(DIAGNOSIS, [policy])
        candidate = next(c for c in candidates if c.policy_id == policy["policy_id"])

        assert candidate.action_type == "POLICY"
        assert candidate.basis == CandidateBasis.CONDITION_ADJUST

    def test_condition_details_are_kept_in_candidate_context(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_CONDITIONAL])
        candidate = next(c for c in candidates if c.policy_id == POLICY_CONDITIONAL["policy_id"])

        assert candidate.context["condition_details"] == POLICY_CONDITIONAL["condition_details"]

    def test_conditional_candidate_keeps_missing_conditions(self):
        policy = copy.deepcopy(POLICY_CONDITIONAL)
        policy["missing_conditions"] = ["ASSET_REQUIREMENT"]

        candidates = generate_candidates(DIAGNOSIS, [policy])
        candidate = next(c for c in candidates if c.policy_id == policy["policy_id"])

        assert candidate.context["missing_conditions"] == ["ASSET_REQUIREMENT"]

    @pytest.mark.parametrize(
        "policy_fixture",
        [POLICY_AVAILABLE, POLICY_CONDITIONAL, POLICY_NEED_MORE_INFO],
    )
    def test_policy_candidate_keeps_application_period(self, policy_fixture):
        candidates = generate_candidates(DIAGNOSIS, [policy_fixture])
        candidate = next(c for c in candidates if c.policy_id == policy_fixture["policy_id"])

        assert candidate.context["application_period_type"] == policy_fixture["application_period_type"]
        assert candidate.context["application_end"] == policy_fixture["application_end"]

    def test_target_region_condition_generates_housing_action(self):
        policy = copy.deepcopy(POLICY_CONDITIONAL)
        policy["failed_conditions"] = ["TARGET_REGION"]

        candidates = generate_candidates(DIAGNOSIS, [policy])
        candidate = next(c for c in candidates if c.policy_id == policy["policy_id"])

        assert candidate.action_type == "HOUSING"

    def test_current_region_condition_does_not_generate_housing_action(self):
        policy = copy.deepcopy(POLICY_CONDITIONAL)
        policy["failed_conditions"] = ["CURRENT_REGION"]

        candidates = generate_candidates(DIAGNOSIS, [policy])
        candidate = next(c for c in candidates if c.policy_id == policy["policy_id"])

        assert candidate.action_type == "POLICY"

    def test_need_more_info_generates_information_notice(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_NEED_MORE_INFO])
        policy_candidates = [c for c in candidates if c.action_type == "POLICY"]
        assert any(c.basis == CandidateBasis.INFORMATION_NOTICE for c in policy_candidates)

    def test_not_eligible_generates_no_candidate(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_NOT_ELIGIBLE])
        policy_ids = [c.policy_id for c in candidates]
        assert POLICY_NOT_ELIGIBLE["policy_id"] not in policy_ids

    def test_policy_id_attached_to_candidate(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        policy_candidates = [c for c in candidates if c.policy_id == POLICY_AVAILABLE["policy_id"]]
        assert len(policy_candidates) == 1


class TestContractCandidate:
    def test_contract_always_present(self):
        candidates = generate_candidates(DIAGNOSIS, [])
        assert any(c.action_type == "CONTRACT" for c in candidates)

    def test_contract_basis_is_contract_check(self):
        candidates = generate_candidates(DIAGNOSIS, [])
        contract = next(c for c in candidates if c.action_type == "CONTRACT")
        assert contract.basis == CandidateBasis.CONTRACT_CHECK


class TestCandidateOrder:
    def test_saving_comes_first(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        assert candidates[0].action_type == "SAVING"

    def test_contract_comes_last(self):
        candidates = generate_candidates(DIAGNOSIS, [POLICY_AVAILABLE])
        assert candidates[-1].action_type == "CONTRACT"

    def test_all_policies_generate_candidates(self):
        policies = [POLICY_AVAILABLE, POLICY_CONDITIONAL, POLICY_NEED_MORE_INFO, POLICY_NOT_ELIGIBLE]
        candidates = generate_candidates(DIAGNOSIS, policies)
        # SAVING(1) + AVAILABLE(1) + CONDITIONAL(1) + NEED_MORE_INFO(1) + CONTRACT(1) = 5
        # NOT_ELIGIBLE는 제외
        assert len(candidates) == 5
