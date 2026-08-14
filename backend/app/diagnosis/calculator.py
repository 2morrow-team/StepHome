# 진단 결과를 계산하는 모듈
import math
from datetime import date, datetime, timedelta, timezone
from typing import Any


MOVING_INITIAL_COST = 1_000_000
TARGET_EMERGENCY_FUND = 1_500_000
KST = timezone(timedelta(hours=9))


def months_until_target(target_date: date, today: date | None = None) -> int:
    current_date = today or datetime.now(KST).date()
    if target_date < current_date:
        raise ValueError("target_date는 현재 날짜보다 이전일 수 없습니다.")
    months = (target_date.year - current_date.year) * 12 + target_date.month - current_date.month
    return max(months, 1)


def calculate_diagnosis(user: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    usable_initial_fund = user["current_savings"] - user["current_emergency_fund"]
    required_initial_fund = target["deposit_budget"] + MOVING_INITIAL_COST
    initial_fund_gap = max(required_initial_fund - usable_initial_fund, 0)
    emergency_fund_gap = max(TARGET_EMERGENCY_FUND - user["current_emergency_fund"], 0)
    total_gap = initial_fund_gap + emergency_fund_gap
    months = months_until_target(target["target_date"])
    required_monthly_saving = math.ceil(total_gap / months)

    fund_score = min(usable_initial_fund / required_initial_fund, 1) * 50 if required_initial_fund else 50
    saving_score = (
        min(user["monthly_saving"] / required_monthly_saving, 1) * 30
        if required_monthly_saving
        else 30
    )
    emergency_score = (
        min(user["current_emergency_fund"] / TARGET_EMERGENCY_FUND, 1) * 20
        if TARGET_EMERGENCY_FUND
        else 20
    )
    estimated_months = math.ceil(total_gap / user["monthly_saving"]) if total_gap else 0

    return {
        "readiness_score": round(fund_score + saving_score + emergency_score),
        "fund_score": round(fund_score, 2),
        "saving_score": round(saving_score, 2),
        "emergency_score": round(emergency_score, 2),
        "required_initial_fund": required_initial_fund,
        "initial_fund_gap": initial_fund_gap,
        "target_emergency_fund": TARGET_EMERGENCY_FUND,
        "emergency_fund_gap": emergency_fund_gap,
        "required_monthly_saving": required_monthly_saving,
        "estimated_months": estimated_months,
        "calculated_at": datetime.now(KST),
    }
