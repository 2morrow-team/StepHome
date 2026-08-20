import copy
from datetime import date
import pytest
from app.ai.candidate_generator import generate_candidates
from app.ai.validator import validate_action_plan
from tests.ai.fixtures import (
    DIAGNOSIS,
    POLICY_AVAILABLE,
    POLICY_CONDITIONAL,
    POLICY_NEED_MORE_INFO,
    POLICY_NOT_ELIGIBLE,
    VALID_ACTION_PLAN,
)


class TestValidStructure:
    def test_valid_plan_passes(self):
        result = validate_action_plan(copy.deepcopy(VALID_ACTION_PLAN))
        assert result == VALID_ACTION_PLAN

    def test_valid_plan_with_policy_id_set(self):
        result = validate_action_plan(
            copy.deepcopy(VALID_ACTION_PLAN),
            valid_policy_ids={1, 2},
        )
        assert result is not None

    def test_returns_same_structure(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        result = validate_action_plan(plan)
        assert "summary" in result
        assert "actions" in result


class TestStructureValidation:
    def test_missing_summary_raises(self):
        plan = {"actions": []}
        with pytest.raises(ValueError, match="구조"):
            validate_action_plan(plan)

    def test_non_list_actions_raises(self):
        plan = {"summary": "test", "actions": "not a list"}
        with pytest.raises(ValueError, match="구조"):
            validate_action_plan(plan)

    def test_empty_actions_raise(self):
        with pytest.raises(ValueError, match="최소 1개"):
            validate_action_plan({"summary": "요약", "actions": []})


class TestBackendFieldRejection:
    @pytest.mark.parametrize("field", ["plan_id", "action_id", "status", "created_at"])
    def test_backend_field_rejected(self, field):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0][field] = "any_value"
        with pytest.raises(ValueError, match="Backend"):
            validate_action_plan(plan)


class TestActionTypeValidation:
    @pytest.mark.parametrize("action_type", ["SAVING", "POLICY", "HOUSING", "CONTRACT"])
    def test_valid_action_types_pass(self, action_type):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["action_type"] = action_type
        validate_action_plan(plan)  # should not raise

    def test_invalid_action_type_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["action_type"] = "INVALID_TYPE"
        with pytest.raises(ValueError, match="action_type"):
            validate_action_plan(plan)


class TestTimingValidation:
    @pytest.mark.parametrize("timing", ["NOW", "PREPARE", "SEARCH_HOUSE", "BEFORE_CONTRACT"])
    def test_valid_timings_pass(self, timing):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["timing"] = timing
        validate_action_plan(plan)  # should not raise

    def test_invalid_timing_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["timing"] = "TOMORROW"
        with pytest.raises(ValueError, match="timing"):
            validate_action_plan(plan)


class TestRequiredFields:
    @pytest.mark.parametrize("field", ["title", "description", "reason"])
    def test_missing_required_field_raises(self, field):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        del plan["actions"][0][field]
        with pytest.raises(ValueError, match="누락"):
            validate_action_plan(plan)

    @pytest.mark.parametrize("field", ["title", "description", "reason"])
    def test_empty_required_field_raises(self, field):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0][field] = ""
        with pytest.raises(ValueError, match="누락"):
            validate_action_plan(plan)


class TestPriorityValidation:
    def test_priority_zero_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["priority"] = 0
        with pytest.raises(ValueError, match="priority"):
            validate_action_plan(plan)

    def test_negative_priority_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["priority"] = -1
        with pytest.raises(ValueError, match="priority"):
            validate_action_plan(plan)

    def test_string_priority_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["priority"] = "1"
        with pytest.raises(ValueError, match="priority"):
            validate_action_plan(plan)

    def test_valid_priority_one_passes(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["priority"] = 1
        validate_action_plan(plan)  # should not raise

    def test_duplicate_priority_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][1]["priority"] = 1
        with pytest.raises(ValueError, match="순서대로"):
            validate_action_plan(plan)


class TestPhaseValidation:
    @pytest.mark.parametrize("phase", [1, 2, 3, 4])
    def test_valid_phase_passes(self, phase):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][phase - 1]["phase"] = phase
        validate_action_plan(plan)  # should not raise

    def test_phase_zero_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["phase"] = 0
        with pytest.raises(ValueError, match="phase"):
            validate_action_plan(plan)

    def test_phase_five_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["phase"] = 5
        with pytest.raises(ValueError, match="phase"):
            validate_action_plan(plan)

    def test_string_phase_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["phase"] = "1"
        with pytest.raises(ValueError, match="phase"):
            validate_action_plan(plan)

    def test_missing_phase_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        del plan["actions"][0]["phase"]
        with pytest.raises(ValueError, match="phase"):
            validate_action_plan(plan)

    def test_missing_phase_coverage_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][2]["phase"] = 2
        with pytest.raises(ValueError, match="Phase 1~4"):
            validate_action_plan(plan)


class TestHallucinationPrevention:
    def test_unknown_policy_id_raises(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][1]["policy_id"] = 999
        with pytest.raises(ValueError, match="policy_id"):
            validate_action_plan(plan, valid_policy_ids={1, 2})

    def test_known_policy_id_passes(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        validate_action_plan(plan, valid_policy_ids={1, 2})  # policy_id=1 exists in fixture

    def test_null_policy_id_always_passes(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][0]["policy_id"] = None
        validate_action_plan(plan, valid_policy_ids={1, 2})  # should not raise

    def test_no_valid_policy_ids_skips_check(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][1]["policy_id"] = 999
        validate_action_plan(plan, valid_policy_ids=None)  # should not raise

    def test_not_eligible_policy_candidate_is_rejected(self):
        plan = copy.deepcopy(VALID_ACTION_PLAN)
        plan["actions"][1]["policy_id"] = POLICY_NOT_ELIGIBLE["policy_id"]
        candidates = generate_candidates(
            DIAGNOSIS,
            [POLICY_AVAILABLE, POLICY_NOT_ELIGIBLE],
            monthly_saving=500000,
        )
        with pytest.raises(ValueError, match="허용되지 않은 Action 후보"):
            validate_action_plan(plan, candidates=candidates)

    def test_allowed_candidates_pass(self):
        candidates = generate_candidates(
            DIAGNOSIS,
            [POLICY_AVAILABLE],
            monthly_saving=500000,
            today=date(2026, 4, 1),
        )
        validate_action_plan(copy.deepcopy(VALID_ACTION_PLAN), candidates=candidates)

    def test_all_candidates_are_required_when_enabled(self):
        candidates = generate_candidates(DIAGNOSIS, [], monthly_saving=500000)
        saving = copy.deepcopy(VALID_ACTION_PLAN["actions"][0])
        plan = {
            "summary": "저축 계획을 조정하세요.",
            "actions": [
                {**copy.deepcopy(saving), "phase": 1, "priority": 1},
                {**copy.deepcopy(saving), "phase": 2, "priority": 2},
                {**copy.deepcopy(saving), "phase": 3, "priority": 3},
                {**copy.deepcopy(saving), "phase": 4, "priority": 4},
            ],
        }

        with pytest.raises(ValueError, match="생성되지 않은"):
            validate_action_plan(
                plan,
                candidates=candidates,
                require_all_candidates=True,
            )
