from dataclasses import dataclass, field
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CandidateBasis:
    SAVING_MAINTAIN = "SAVING_MAINTAIN"
    SAVING_ADJUST = "SAVING_ADJUST"
    POLICY_APPLY = "POLICY_APPLY"
    POLICY_MONITOR = "POLICY_MONITOR"
    CONDITION_ADJUST = "CONDITION_ADJUST"
    INFORMATION_NOTICE = "INFORMATION_NOTICE"
    CONTRACT_CHECK = "CONTRACT_CHECK"


@dataclass
class ActionCandidate:
    action_type: str
    basis: str
    policy_id: Optional[int] = None
    context: dict = field(default_factory=dict)


class ActionOutput(BaseModel):
    """LLM이 생성해야 하는 개별 Action의 구조화 출력 스키마."""

    model_config = ConfigDict(extra="forbid")

    phase: int = Field(ge=1, le=4, description="실행 단계 1=즉시·2=단기·3=중기·4=입주직전")
    priority: int = Field(ge=1, description="1부터 시작하는 실행 우선순위")
    action_type: Literal["SAVING", "POLICY", "HOUSING", "CONTRACT"]
    timing: Literal["NOW", "PREPARE", "SEARCH_HOUSE", "BEFORE_CONTRACT"]
    title: str = Field(min_length=1, max_length=15)
    description: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    policy_id: Optional[int]
    due_date: Optional[date]


class ActionPlanOutput(BaseModel):
    """OpenAI Structured Outputs에 전달하는 최종 응답 스키마."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, description="사용자 상황을 요약한 1~2문장")
    actions: list[ActionOutput]


class ScenarioExplanationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: Literal["LOWER_DEPOSIT", "DELAY_MOVE_IN", "INCREASE_SAVINGS"]
    reason: str = Field(min_length=1)
    tradeoff: str = Field(min_length=1)


class ScenarioRecommendationOutput(BaseModel):
    """AI가 계산을 바꾸지 않고 시나리오 비교 설명만 생성하는 스키마."""

    model_config = ConfigDict(extra="forbid")

    recommended_scenario_id: Literal[
        "LOWER_DEPOSIT",
        "DELAY_MOVE_IN",
        "INCREASE_SAVINGS",
    ]
    summary: str = Field(min_length=1)
    explanations: list[ScenarioExplanationOutput] = Field(min_length=1)
