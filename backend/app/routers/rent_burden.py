# 월세 부담도 계산기 API Router

from fastapi import APIRouter

from app.calculators.rent_burden import (
    calculate_rent_burden,
)
from app.calculators.schemas import (
    RentBurdenRequest,
    RentBurdenResponse,
)


router = APIRouter()


@router.post(
    "/api/v1/calculators/rent-burden",
    response_model=RentBurdenResponse,
)
def calculate_rent_burden_api(
    request: RentBurdenRequest,
) -> RentBurdenResponse:
    """
    월소득과 월세를 기반으로 월세 부담률을 계산하고,
    생활비와 목표 저축액을 반영한 예상 잔여금을 반환한다.
    """

    result = calculate_rent_burden(
        personal_monthly_income=(
            request.personal_monthly_income
        ),
        desired_monthly_rent=(
            request.desired_monthly_rent
        ),
        monthly_management_fee=(
            request.monthly_management_fee
        ),
        monthly_living_expense=(
            request.monthly_living_expense
        ),
        target_monthly_savings=(
            request.target_monthly_savings
        ),
    )

    return RentBurdenResponse(
        **result
    )
