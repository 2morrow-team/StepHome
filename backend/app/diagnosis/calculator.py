# 독립 준비도 Diagnosis 계산 모듈

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any


KST = timezone(timedelta(hours=9))


def months_until_target(
    planned_move_in_date: date,
    today: date | None = None,
) -> int:
    """
    오늘부터 독립 예정일까지 남은 기간을 30일 = 1개월 기준으로 계산한다.

    예:
    1~30일   -> 1개월
    31~60일  -> 2개월

    독립 예정일은 오늘보다 미래 날짜여야 한다.
    """

    current_date = today or datetime.now(KST).date()

    if planned_move_in_date <= current_date:
        raise ValueError(
            "입주 예정일은 오늘보다 이후 날짜로 선택해주세요."
        )

    remaining_days = (planned_move_in_date - current_date).days

    return max(
        math.ceil(remaining_days / 30),
        1,
    )


def calculate_diagnosis(
    user: dict[str, Any],
    target: dict[str, Any],
    today: date | None = None,
) -> dict[str, Any]:
    """
    User / Target 입력값을 기반으로 독립 준비도를 계산한다.

    최종 MVP 기준:
    - 비상자금 별도 계산 없음
    - 고정 이사비/초기비용 없음
    - required_initial_fund = desired_deposit
    - fund_score 최대 70점
    - saving_score 최대 30점
    """

    total_assets = user["total_assets"]
    monthly_savings = user["monthly_savings"]

    desired_deposit = target["desired_deposit"]
    planned_move_in_date = target["planned_move_in_date"]

    # -----------------------------------------------------
    # 1. 필요 초기자금
    # -----------------------------------------------------

    required_initial_fund = desired_deposit

    # -----------------------------------------------------
    # 2. 초기자금 부족액
    # -----------------------------------------------------

    initial_fund_gap = max(
        required_initial_fund - total_assets,
        0,
    )

    # -----------------------------------------------------
    # 3. 목표일까지 남은 개월 수
    # -----------------------------------------------------

    months = months_until_target(
        planned_move_in_date,
        today=today,
    )

    # -----------------------------------------------------
    # 4. 목표일까지 필요한 월 저축액
    # -----------------------------------------------------

    if initial_fund_gap == 0:
        required_monthly_saving = 0
    else:
        required_monthly_saving = math.ceil(
            initial_fund_gap / months
        )

    # -----------------------------------------------------
    # 5. 초기자금 준비도 - 최대 70점
    # -----------------------------------------------------

    if required_initial_fund == 0:
        fund_score = 70.0
    else:
        fund_score = (
            min(
                total_assets / required_initial_fund,
                1,
            )
            * 70
        )

    # -----------------------------------------------------
    # 6. 저축계획 준비도 - 최대 30점
    # -----------------------------------------------------

    if required_monthly_saving == 0:
        saving_score = 30.0
    else:
        saving_score = (
            min(
                monthly_savings / required_monthly_saving,
                1,
            )
            * 30
        )

    # -----------------------------------------------------
    # 7. 예상 준비기간
    # -----------------------------------------------------

    if initial_fund_gap == 0:
        estimated_months: int | None = 0

    elif monthly_savings == 0:
        # 부족액은 있지만 현재 저축액이 0원이므로
        # 유한한 준비기간을 계산할 수 없다.
        estimated_months = None

    else:
        estimated_months = math.ceil(
            initial_fund_gap / monthly_savings
        )

    # -----------------------------------------------------
    # 8. 최종 준비도
    # -----------------------------------------------------

    readiness_score = round(
        fund_score + saving_score
    )

    # 안전하게 0~100 범위 유지
    readiness_score = min(
        max(readiness_score, 0),
        100,
    )

    return {
        "readiness_score": readiness_score,
        "fund_score": round(fund_score, 2),
        "saving_score": round(saving_score, 2),

        "required_initial_fund": required_initial_fund,
        "initial_fund_gap": initial_fund_gap,

        "required_monthly_saving": required_monthly_saving,
        "estimated_months": estimated_months,

        "calculated_at": datetime.now(KST),
    }
