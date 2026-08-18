from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.schemas import (
    ApplicationPeriodType,
    EmploymentStatus,
    HousingStatus,
    HousingType,
    MaritalStatus,
    PolicyCategory,
    Region,
    SupportAmountUnit,
)


class RatioRange(BaseModel):
    min: float | None = Field(default=None, ge=0)
    max: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_range(self):
        if (
            self.min is not None
            and self.max is not None
            and self.min > self.max
        ):
            raise ValueError("ratio min은 max보다 클 수 없습니다.")

        return self


class AgeRule(BaseModel):
    min: int | None = Field(default=None, ge=0)
    max: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_range(self):
        if (
            self.min is not None
            and self.max is not None
            and self.min > self.max
        ):
            raise ValueError("age min은 max보다 클 수 없습니다.")

        return self


class IncomeRule(BaseModel):
    personal_ratio: RatioRange
    youth_household_ratio: RatioRange
    basis: str | None = None


class AssetsRule(BaseModel):
    total_assets_max: int | None = Field(default=None, ge=0)


class HousingRule(BaseModel):
    type: list[HousingType]
    deposit_max: int | None = Field(default=None, ge=0)
    monthly_rent_max: int | None = Field(default=None, ge=0)


class EligibilityRules(BaseModel):
    age: AgeRule
    current_region: list[Region]
    target_region: list[Region]
    housing_status: list[HousingStatus]
    marital_status: list[MaritalStatus]
    employment_status: list[EmploymentStatus]

    income: IncomeRule
    assets: AssetsRule
    housing: HousingRule

    additional_conditions: list[str]


class PolicyData(BaseModel):
    policy_id: int = Field(gt=0)

    title: str
    description: str

    policy_category: PolicyCategory
    policy_region: str
    policy_provider: str | None = None

    application_start: date | None = None
    application_end: date | None = None
    application_period_type: ApplicationPeriodType

    support_amount: int | None = Field(default=None, ge=0)
    support_amount_unit: SupportAmountUnit
    support_amount_text: str

    family_earnings: str
    eligibility_text: str
    eligibility_rules: EligibilityRules

    source_url: str
    checked_at: datetime | None = None

    @model_validator(mode="after")
    def validate_application_period(self):
        if (
            self.application_start is not None
            and self.application_end is not None
            and self.application_start > self.application_end
        ):
            raise ValueError(
                "application_start는 application_end보다 늦을 수 없습니다."
            )

        return self


class ExtractedRatioRange(BaseModel):
    min: float | None = None
    max: float | None = None


class ExtractedAgeRule(BaseModel):
    min: int | None = None
    max: int | None = None


class ExtractedIncomeRule(BaseModel):
    personal_ratio: ExtractedRatioRange
    youth_household_ratio: ExtractedRatioRange
    basis: str | None = None


class ExtractedAssetsRule(BaseModel):
    total_assets_max: int | float | str | None = None


class ExtractedHousingRule(BaseModel):
    type: list[str] = Field(default_factory=list)
    deposit_max: int | float | str | None = None
    monthly_rent_max: int | float | str | None = None


class ExtractedEligibilityRules(BaseModel):
    age: ExtractedAgeRule

    current_region: list[str] = Field(default_factory=list)
    target_region: list[str] = Field(default_factory=list)

    housing_status: list[str] = Field(default_factory=list)
    marital_status: list[str] = Field(default_factory=list)
    employment_status: list[str] = Field(default_factory=list)

    income: ExtractedIncomeRule
    assets: ExtractedAssetsRule
    housing: ExtractedHousingRule

    additional_conditions: list[str] = Field(default_factory=list)


class ExtractedPolicyData(BaseModel):
    policy_id: int

    title: str
    description: str

    policy_category: str
    policy_region: str
    policy_provider: str | None = None

    application_start: date | None = None
    application_end: date | None = None
    application_period_type: str

    support_amount: int | float | str | None = None
    support_amount_unit: str
    support_amount_text: str

    family_earnings: str
    eligibility_text: str

    eligibility_rules: ExtractedEligibilityRules

    source_url: str
    checked_at: datetime | None = None