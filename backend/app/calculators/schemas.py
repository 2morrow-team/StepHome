# 월세 부담도 계산기 Request / Response Schema

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RentBurdenRequest(BaseModel):
    """
    월세 부담도 계산기 입력값.

    기존 StepHome 입력값과 연결 가능한 필드:
    - personal_monthly_income
    - desired_monthly_rent

    계산기에서 추가 입력:
    - monthly_management_fee
    - monthly_living_expense
    - target_monthly_savings
    """

    model_config = ConfigDict(extra="forbid")

    personal_monthly_income: int = Field(
        gt=0,
        description="사용자 본인의 월소득",
    )

    desired_monthly_rent: int = Field(
        ge=0,
        description="고려 중인 월세",
    )

    monthly_management_fee: int = Field(
        default=0,
        ge=0,
        description="월 관리비",
    )

    monthly_living_expense: int = Field(
        default=0,
        ge=0,
        description="월 예상 생활비",
    )

    target_monthly_savings: int = Field(
        default=0,
        ge=0,
        description="유지하고 싶은 목표 월 저축액",
    )


class RentBurdenResponse(BaseModel):
    """
    월세 부담도 계산 결과.

    rent_burden_ratio:
        RIR 개념을 참고한
        월소득 대비 월세 비율.

    monthly_housing_cost:
        월세 + 관리비.

    estimated_monthly_balance:
        월세, 관리비, 생활비, 목표 저축액을
        모두 반영한 뒤 남는 예상 금액.
        음수일 수 있다.
    """

    rent_burden_ratio: float

    monthly_housing_cost: int

    estimated_monthly_balance: int
