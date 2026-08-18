# 월세 부담도 계산 로직

from __future__ import annotations

from typing import Any


def calculate_rent_burden(
    personal_monthly_income: int,
    desired_monthly_rent: int,
    monthly_management_fee: int = 0,
    monthly_living_expense: int = 0,
    target_monthly_savings: int = 0,
) -> dict[str, Any]:
    """
    사용자의 월소득과 희망 월세를 기준으로
    월세 부담도와 예상 월 잔여금을 계산한다.

    월세 부담률:
        desired_monthly_rent
        / personal_monthly_income
        * 100

    월 주거비:
        desired_monthly_rent
        + monthly_management_fee

    예상 월 잔여금:
        personal_monthly_income
        - desired_monthly_rent
        - monthly_management_fee
        - monthly_living_expense
        - target_monthly_savings

    estimated_monthly_balance는
    지출 및 목표 저축액이 소득보다 크면
    음수가 될 수 있다.
    """

    if personal_monthly_income <= 0:
        raise ValueError(
            "personal_monthly_income은 0보다 커야 합니다."
        )

    rent_burden_ratio = (
        desired_monthly_rent
        / personal_monthly_income
        * 100
    )

    monthly_housing_cost = (
        desired_monthly_rent
        + monthly_management_fee
    )

    estimated_monthly_balance = (
        personal_monthly_income
        - desired_monthly_rent
        - monthly_management_fee
        - monthly_living_expense
        - target_monthly_savings
    )

    return {
        "rent_burden_ratio": round(
            rent_burden_ratio,
            2,
        ),
        "monthly_housing_cost": monthly_housing_cost,
        "estimated_monthly_balance": (
            estimated_monthly_balance
        ),
    }
