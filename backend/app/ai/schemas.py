from dataclasses import dataclass, field
from typing import Optional


class CandidateBasis:
    SAVING_MAINTAIN = "SAVING_MAINTAIN"
    SAVING_ADJUST = "SAVING_ADJUST"
    POLICY_APPLY = "POLICY_APPLY"
    CONDITION_ADJUST = "CONDITION_ADJUST"
    INFORMATION_NOTICE = "INFORMATION_NOTICE"
    CONTRACT_CHECK = "CONTRACT_CHECK"


@dataclass
class ActionCandidate:
    action_type: str
    basis: str
    policy_id: Optional[int] = None
    context: dict = field(default_factory=dict)
