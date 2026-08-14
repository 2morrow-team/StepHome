# API 요청과 응답 스키마 정의
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class EmploymentStatus(str, Enum):
    JOB_SEEKER = "JOB_SEEKER"
    EMPLOYED = "EMPLOYED"
    STUDENT = "STUDENT"
    OTHER = "OTHER"


class HousingType(str, Enum):
    MONTHLY_RENT = "MONTHLY_RENT"
    JEONSE = "JEONSE"


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


class UserRequest(BaseModel):
    age: int = Field(ge=0)
    employment_status: EmploymentStatus
    region: str = Field(min_length=1)
    monthly_income: int = Field(ge=0)
    current_savings: int = Field(ge=0)
    current_emergency_fund: int = Field(ge=0)
    monthly_saving: int = Field(gt=0)

    @validator("current_emergency_fund")
    def emergency_fund_must_be_within_savings(cls, value, values):
        current_savings = values.get("current_savings")
        if current_savings is not None and value > current_savings:
            raise ValueError("current_emergency_fund는 current_savings보다 클 수 없습니다.")
        return value


class TargetRequest(BaseModel):
    target_date: date
    monthly_rent_budget: int = Field(ge=0)
    deposit_budget: int = Field(ge=0)
    housing_type: HousingType


class PlanRequest(BaseModel):
    user: UserRequest
    target: TargetRequest


class ReplanChanges(BaseModel):
    deposit_budget: Optional[int] = Field(default=None, ge=0)


class ReplanRequest(BaseModel):
    user_id: int = Field(gt=0)
    target_id: int = Field(gt=0)
    previous_diagnosis_id: int = Field(gt=0)
    previous_plan_id: int = Field(gt=0)
    changes: ReplanChanges


class TargetResponse(TargetRequest):
    target_region: str


class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    user_id: int
    target_id: int
    readiness_score: int
    fund_score: float
    saving_score: float
    emergency_score: float
    required_initial_fund: int
    initial_fund_gap: int
    target_emergency_fund: int
    emergency_fund_gap: int
    required_monthly_saving: int
    estimated_months: int
    calculated_at: datetime


class PolicyMatchResponse(BaseModel):
    match_id: int
    user_id: int
    diagnosis_id: int
    policy_id: int
    title: str
    eligibility_status: EligibilityStatus
    matched_conditions: list[str]
    failed_conditions: list[str]
    missing_conditions: list[str]
    rank: int
    support_amount: Optional[int]
    support_amount_text: str
    eligibility_text: str
    description: str
    application_start: date
    application_end: date
    region: str
    provider: str
    category: str
    source_url: str
    checked_at: datetime
    matched_at: datetime


class AiAction(BaseModel):
    priority: int = Field(gt=0)
    action_type: ActionType
    timing: Timing
    title: str
    description: str
    reason: str
    policy_id: Optional[int] = None
    due_date: Optional[date] = None


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


class ChangedField(BaseModel):
    before: int
    after: int


class ReplanResponse(BaseModel):
    user_id: int
    target_id: int
    previous: PlanSnapshot
    current: PlanSnapshot
    changed_fields: dict[str, ChangedField]


class HealthResponse(BaseModel):
    status: str


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[list[ErrorDetail]] = None


class ErrorResponse(BaseModel):
    error: ErrorBody
