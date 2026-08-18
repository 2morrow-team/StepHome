# API 요청/응답에서 사용하는 공통 Pydantic Schema
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# Enum
# =========================================================


class EmploymentStatus(str, Enum):
    JOB_SEEKER = "JOB_SEEKER"
    EMPLOYED = "EMPLOYED"
    STUDENT = "STUDENT"
    OTHER = "OTHER"


class HousingType(str, Enum):
    MONTHLY_RENT = "MONTHLY_RENT"
    JEONSE = "JEONSE"


class HousingStatus(str, Enum):
    NO_HOME = "NO_HOME"
    HAS_HOME = "HAS_HOME"


class MaritalStatus(str, Enum):
    UNMARRIED = "UNMARRIED"
    MARRIED = "MARRIED"


class Region(str, Enum):
    NATIONAL = "NATIONAL"
    SEOUL = "SEOUL"
    BUSAN = "BUSAN"
    DAEGU = "DAEGU"
    INCHEON = "INCHEON"
    GWANGJU = "GWANGJU"
    DAEJEON = "DAEJEON"
    ULSAN = "ULSAN"
    SEJONG = "SEJONG"
    GYEONGGI = "GYEONGGI"
    GANGWON = "GANGWON"
    CHUNGBUK = "CHUNGBUK"
    CHUNGNAM = "CHUNGNAM"
    JEONBUK = "JEONBUK"
    JEONNAM = "JEONNAM"
    GYEONGBUK = "GYEONGBUK"
    GYEONGNAM = "GYEONGNAM"
    JEJU = "JEJU"


class PolicyCategory(str, Enum):
    LOAN = "LOAN"
    RENT_SUPPORT = "RENT_SUPPORT"
    PUBLIC_RENTAL = "PUBLIC_RENTAL"


class SupportAmountUnit(str, Enum):
    MONTH = "MONTH"
    YEAR = "YEAR"
    TOTAL = "TOTAL"
    OTHER = "OTHER"


class ApplicationPeriodType(str, Enum):
    FIXED = "FIXED"
    ALWAYS_OPEN = "ALWAYS_OPEN"
    NOTICE_BASED = "NOTICE_BASED"
    UNKNOWN = "UNKNOWN"


class EligibilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONDITIONAL = "CONDITIONAL"
    NEED_MORE_INFO = "NEED_MORE_INFO"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ActionType(str, Enum):
    SAVING = "SAVING"
    POLICY = "POLICY"
    HOUSING = "HOUSING"
    CONTRACT = "CONTRACT"


class Timing(str, Enum):
    NOW = "NOW"
    PREPARE = "PREPARE"
    SEARCH_HOUSE = "SEARCH_HOUSE"
    BEFORE_CONTRACT = "BEFORE_CONTRACT"


class ActionStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ScenarioPriority(str, Enum):
    FAST_MOVE = "FAST_MOVE"
    LOW_MONTHLY_BURDEN = "LOW_MONTHLY_BURDEN"
    POLICY_BENEFIT = "POLICY_BENEFIT"


class ScenarioId(str, Enum):
    LOWER_DEPOSIT = "LOWER_DEPOSIT"
    DELAY_MOVE_IN = "DELAY_MOVE_IN"
    INCREASE_SAVINGS = "INCREASE_SAVINGS"


# =========================================================
# Frontend -> Backend Request
# =========================================================


class UserRequest(BaseModel):
    """Frontend에서 전달하는 P0 User 입력 10개."""

    age: int = Field(ge=19, le=39)

    employment_status: EmploymentStatus
    current_region: Region

    personal_monthly_income: int = Field(ge=0)

    total_assets: int = Field(ge=0)
    monthly_savings: int = Field(ge=0)

    housing_status: HousingStatus

    youth_household_monthly_income: int = Field(ge=0)
    youth_household_size: int = Field(ge=1)

    marital_status: MaritalStatus


class TargetRequest(BaseModel):
    """Frontend에서 전달하는 P0 Target 입력 5개."""

    planned_move_in_date: date

    desired_deposit: int = Field(ge=0)
    desired_monthly_rent: int = Field(ge=0)

    desired_housing_type: HousingType
    desired_region: Region


class PlanRequest(BaseModel):
    user: UserRequest
    target: TargetRequest


# =========================================================
# Re-planning Request
# =========================================================


class ReplanChanges(BaseModel):
    """
    P0 15개 중 변경된 값만 전달한다.

    모든 필드를 optional로 두고,
    실제로 변경할 값만 JSON에 포함한다.
    """

    # User
    age: int | None = Field(default=None, ge=19, le=39)

    employment_status: EmploymentStatus | None = None
    current_region: Region | None = None

    personal_monthly_income: int | None = Field(
        default=None,
        ge=0,
    )

    total_assets: int | None = Field(
        default=None,
        ge=0,
    )

    monthly_savings: int | None = Field(
        default=None,
        ge=0,
    )

    housing_status: HousingStatus | None = None

    youth_household_monthly_income: int | None = Field(
        default=None,
        ge=0,
    )

    youth_household_size: int | None = Field(
        default=None,
        ge=1,
    )

    marital_status: MaritalStatus | None = None

    # Target
    planned_move_in_date: date | None = None

    desired_deposit: int | None = Field(
        default=None,
        ge=0,
    )

    desired_monthly_rent: int | None = Field(
        default=None,
        ge=0,
    )

    desired_housing_type: HousingType | None = None
    desired_region: Region | None = None


class ReplanRequest(BaseModel):
    user_id: int = Field(gt=0)
    target_id: int = Field(gt=0)

    previous_diagnosis_id: int = Field(gt=0)
    previous_plan_id: int = Field(gt=0)

    changes: ReplanChanges


class ScenarioConstraints(BaseModel):
    """시나리오가 사용자의 허용 범위를 벗어나지 않도록 제한한다."""

    model_config = ConfigDict(extra="forbid")

    minimum_desired_deposit: int | None = Field(default=None, ge=0)
    max_additional_monthly_savings: int = Field(default=500_000, ge=0)
    max_move_delay_months: int = Field(default=6, ge=0, le=24)


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(gt=0)
    target_id: int = Field(gt=0)
    previous_diagnosis_id: int = Field(gt=0)
    previous_plan_id: int = Field(gt=0)
    priority: ScenarioPriority
    constraints: ScenarioConstraints = Field(default_factory=ScenarioConstraints)


# =========================================================
# User / Target Response
# =========================================================


class UserResponse(UserRequest):
    user_id: int


class TargetResponse(TargetRequest):
    target_id: int
    user_id: int


# =========================================================
# Diagnosis
# =========================================================


class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    user_id: int
    target_id: int

    readiness_score: int
    fund_score: float
    saving_score: float

    required_initial_fund: int
    initial_fund_gap: int

    required_monthly_saving: int

    # monthly_savings == 0이고 부족액이 남아 있으면
    # 유한한 예상 준비기간을 계산할 수 없으므로 null 가능
    estimated_months: int | None

    calculated_at: datetime


# =========================================================
# Policy Match
# =========================================================


class ConditionDetail(BaseModel):
    """Rule Engine이 생성하는 정책 조건별 상세 판정 정보."""

    condition: str
    result: str

    current_value: Any | None = None

    required_values: list[str] | None = None
    required_min: int | float | None = None
    required_max: int | float | None = None

    message: str


class PolicyMatchResponse(BaseModel):
    match_id: int | None = None

    user_id: int | None = None
    diagnosis_id: int | None = None

    policy_id: int

    title: str
    description: str

    policy_category: PolicyCategory
    policy_region: str
    policy_provider: str | None = None

    eligibility_status: EligibilityStatus

    matched_conditions: list[str] = Field(
        default_factory=list,
    )

    failed_conditions: list[str] = Field(
        default_factory=list,
    )

    missing_conditions: list[str] = Field(
        default_factory=list,
    )

    condition_details: list[ConditionDetail] = Field(
        default_factory=list,
    )

    rank: int | None = None

    support_amount: int | None = None
    support_amount_unit: SupportAmountUnit
    support_amount_text: str

    eligibility_text: str

    application_start: date | None = None
    application_end: date | None = None
    application_period_type: ApplicationPeriodType

    source_url: str

    checked_at: datetime | None = None
    matched_at: datetime | None = None


# =========================================================
# AI Action / ActionPlan
# =========================================================


class AiAction(BaseModel):
    phase: int | None = Field(default=None, ge=1, le=4)
    priority: int = Field(gt=0)

    action_type: ActionType
    timing: Timing

    title: str
    description: str
    reason: str

    policy_id: int | None = None
    due_date: date | None = None


class ActionResponse(AiAction):
    action_id: int
    plan_id: int

    user_id: int
    diagnosis_id: int

    status: ActionStatus

    created_at: datetime


class ActionPlanResponse(BaseModel):
    summary: str
    actions: list[ActionResponse]


# =========================================================
# Plan Response
# =========================================================


class PlanSnapshot(BaseModel):
    user_id: int
    target_id: int
    diagnosis_id: int
    plan_id: int

    target: TargetResponse

    diagnosis: DiagnosisResponse

    matched_policies: list[PolicyMatchResponse]

    action_plan: ActionPlanResponse


class PlanResponse(PlanSnapshot):
    pass


# =========================================================
# Re-plan Response
# =========================================================


class ChangedField(BaseModel):
    """
    P0 전체 변경을 지원하므로
    숫자뿐 아니라 Enum / 날짜도 들어갈 수 있다.
    """

    before: Any
    after: Any


class ReplanResponse(BaseModel):
    user_id: int
    target_id: int

    previous: PlanSnapshot
    current: PlanSnapshot

    changed_fields: dict[str, ChangedField]


# =========================================================
# Scenario Response
# =========================================================


class ScenarioDiagnosis(BaseModel):
    readiness_score: int
    fund_score: float
    saving_score: float
    required_initial_fund: int
    initial_fund_gap: int
    required_monthly_saving: int
    estimated_months: int | None


class PolicyStatusChange(BaseModel):
    policy_id: int
    title: str
    before_status: EligibilityStatus
    after_status: EligibilityStatus


class ScenarioOption(BaseModel):
    scenario_id: ScenarioId
    title: str
    changes: ReplanChanges
    changed_fields: dict[str, ChangedField]
    diagnosis: ScenarioDiagnosis
    policy_changes: list[PolicyStatusChange]
    recommendation_score: int = Field(ge=0, le=100)
    ai_reason: str
    tradeoff: str


class ScenarioResponse(BaseModel):
    recommended_scenario_id: ScenarioId
    summary: str
    scenarios: list[ScenarioOption] = Field(min_length=1)


# =========================================================
# Health
# =========================================================


class HealthResponse(BaseModel):
    status: str


# =========================================================
# Error
# =========================================================


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    code: str
    message: str

    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
