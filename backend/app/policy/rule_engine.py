# 정책 규칙을 실행하는 엔진
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.schemas.schemas import EligibilityStatus


KST = timezone(timedelta(hours=9))
POLICY_DATA_PATH = Path(__file__).parent / "data" / "policies.json"


# =========================================================
# Rule Engine Constants
# =========================================================

# 2026년 기준 중위소득 (원 / 월)
# 보건복지부 기준
MEDIAN_INCOME_2026 = {
    1: 2_564_238,
    2: 4_199_292,
    3: 5_359_036,
    4: 6_494_738,
    5: 7_556_719,
    6: 8_555_952,
    7: 9_515_150,
}


# 현재 자격 자체가 정책 기준에 맞지 않는 조건
HARD_FAIL_CONDITIONS = {
    "AGE",
    "CURRENT_REGION",
    "HOUSING_STATUS",
    "MARITAL_STATUS",
    "EMPLOYMENT_STATUS",
    "PERSONAL_INCOME",
    "YOUTH_HOUSEHOLD_INCOME",
    "TOTAL_ASSETS",
}


# 사용자가 희망 독립 조건을 변경하면 충족 가능할 수 있는 조건
ADJUSTABLE_FAIL_CONDITIONS = {
    "TARGET_REGION",
    "HOUSING_TYPE",
    "DEPOSIT_LIMIT",
    "MONTHLY_RENT_LIMIT",
}


# =========================================================
# 1. 정책 데이터 로드
# =========================================================

def _load_policies() -> list[dict[str, Any]]:
    return json.loads(
        POLICY_DATA_PATH.read_text(encoding="utf-8")
    )


# =========================================================
# 2. 지역 조건 판정
# =========================================================

def _matches_region(
    allowed_regions: list[str],
    user_region: str,
) -> bool:
    """
    정책 지역 조건과 사용자 지역을 비교한다.

    []:
        해당 정책에 지역 제한 없음

    NATIONAL:
        전국 지역 허용
    """

    if not allowed_regions:
        return True

    if "NATIONAL" in allowed_regions:
        return True

    return user_region in allowed_regions


# =========================================================
# 3. 기준 중위소득 조회
# =========================================================

def _get_median_income(household_size: int) -> int:
    """
    2026년 기준 중위소득 월 금액을 반환한다.

    1~7인:
        보건복지부 기준값 사용

    8인 이상:
        보건복지부 기준에 따라
        7인가구 기준액에 7인가구와 6인가구의 차액을
        가구원 1명 증가할 때마다 더한다.
    """

    if household_size <= 0:
        raise ValueError(
            "household_size는 1 이상이어야 합니다."
        )

    if household_size in MEDIAN_INCOME_2026:
        return MEDIAN_INCOME_2026[household_size]

    increment = (
        MEDIAN_INCOME_2026[7]
        - MEDIAN_INCOME_2026[6]
    )

    return (
        MEDIAN_INCOME_2026[7]
        + increment * (household_size - 7)
    )


# =========================================================
# 4. 정책 하나 판정
# =========================================================

def _policy_result(
    policy: dict[str, Any],
    user: dict[str, Any],
    target: dict[str, Any],
) -> tuple[
    EligibilityStatus,
    list[str],
    list[str],
    list[str],
    list[dict[str, Any]],
]:
    rules = policy["eligibility_rules"]

    matched: list[str] = []
    failed: list[str] = []
    missing: list[str] = []
    condition_details: list[dict[str, Any]] = []

    # -----------------------------------------------------
    # AGE
    # -----------------------------------------------------

    age_rule = rules["age"]
    age_min = age_rule["min"]
    age_max = age_rule["max"]

    age_has_rule = (
        age_min is not None
        or age_max is not None
    )

    if age_has_rule:
        if age_min is not None and user["age"] < age_min:
            failed.append("AGE")

        elif age_max is not None and user["age"] > age_max:
            failed.append("AGE")

        else:
            matched.append("AGE")

    # -----------------------------------------------------
    # CURRENT_REGION
    # -----------------------------------------------------

    current_regions = rules["current_region"]

    if current_regions:
        if _matches_region(
            current_regions,
            user["current_region"],
        ):
            matched.append("CURRENT_REGION")
        else:
            failed.append("CURRENT_REGION")

    # -----------------------------------------------------
    # TARGET_REGION
    # -----------------------------------------------------

    target_regions = rules["target_region"]

    if target_regions:
        if _matches_region(
            target_regions,
            target["desired_region"],
        ):
            matched.append("TARGET_REGION")
        else:
            failed.append("TARGET_REGION")

            condition_details.append(
                {
                    "condition": "TARGET_REGION",
                    "result": "FAILED",
                    "current_value": target["desired_region"],
                    "required_values": target_regions,
                    "message": (
                        f"희망 거주지역을 "
                        f"{', '.join(target_regions)} 중 하나로 조정 필요"
                    ),
                }
            )

    # -----------------------------------------------------
    # HOUSING_STATUS
    # -----------------------------------------------------

    housing_status_rules = rules["housing_status"]

    if housing_status_rules:
        if user["housing_status"] in housing_status_rules:
            matched.append("HOUSING_STATUS")
        else:
            failed.append("HOUSING_STATUS")

    # -----------------------------------------------------
    # MARITAL_STATUS
    # -----------------------------------------------------

    marital_status_rules = rules["marital_status"]

    if marital_status_rules:
        if user["marital_status"] in marital_status_rules:
            matched.append("MARITAL_STATUS")
        else:
            failed.append("MARITAL_STATUS")

    # -----------------------------------------------------
    # EMPLOYMENT_STATUS
    # -----------------------------------------------------

    employment_status_rules = rules["employment_status"]

    if employment_status_rules:
        if (
            user["employment_status"]
            in employment_status_rules
        ):
            matched.append("EMPLOYMENT_STATUS")
        else:
            failed.append("EMPLOYMENT_STATUS")

    # -----------------------------------------------------
    # HOUSING
    # -----------------------------------------------------

    housing_rule = rules["housing"]

    # HOUSING_TYPE

    housing_types = housing_rule["type"]

    if housing_types:
        if (
            target["desired_housing_type"]
            in housing_types
        ):
            matched.append("HOUSING_TYPE")
        else:
            failed.append("HOUSING_TYPE")

            condition_details.append(
                {
                    "condition": "HOUSING_TYPE",
                    "result": "FAILED",
                    "current_value": target["desired_housing_type"],
                    "required_values": housing_types,
                    "message": (
                        f"희망 주거형태를 "
                        f"{', '.join(housing_types)} 중 하나로 조정 필요"
                    ),
                }
            )

    # DEPOSIT

    deposit_max = housing_rule["deposit_max"]

    if deposit_max is not None:
        if target["desired_deposit"] <= deposit_max:
            matched.append("DEPOSIT_LIMIT")
        else:
            failed.append("DEPOSIT_LIMIT")

            condition_details.append(
                {
                    "condition": "DEPOSIT_LIMIT",
                    "result": "FAILED",
                    "current_value": target["desired_deposit"],
                    "required_max": deposit_max,
                    "message": (
                        f"희망 보증금 {deposit_max:,}원 이하 필요"
                    ),
                }
            )

    # MONTHLY_RENT

    monthly_rent_max = housing_rule["monthly_rent_max"]

    if monthly_rent_max is not None:
        if (
            target["desired_monthly_rent"]
            <= monthly_rent_max
        ):
            matched.append("MONTHLY_RENT_LIMIT")
        else:
            failed.append("MONTHLY_RENT_LIMIT")

            condition_details.append(
                {
                    "condition": "MONTHLY_RENT_LIMIT",
                    "result": "FAILED",
                    "current_value": target["desired_monthly_rent"],
                    "required_max": monthly_rent_max,
                    "message": (
                        f"희망 월세 {monthly_rent_max:,}원 이하 필요"
                    ),
                }
            )

    # -----------------------------------------------------
    # INCOME
    # -----------------------------------------------------

    income_rule = rules["income"]

    personal_ratio = income_rule["personal_ratio"]
    youth_household_ratio = income_rule["youth_household_ratio"]
    income_basis = income_rule["basis"]

    if income_basis == "MEDIAN_INCOME":
        median_income = _get_median_income(
            user["youth_household_size"]
        )

        # -------------------------------------------------
        # 청년가구 소득
        # -------------------------------------------------

        youth_min_ratio = youth_household_ratio["min"]
        youth_max_ratio = youth_household_ratio["max"]

        if youth_min_ratio is not None or youth_max_ratio is not None:
            youth_income = user["youth_household_monthly_income"]

            youth_min_income = (
                median_income * youth_min_ratio
                if youth_min_ratio is not None
                else None
            )

            youth_max_income = (
                median_income * youth_max_ratio
                if youth_max_ratio is not None
                else None
            )

            # 최소 소득 기준 미충족
            if (
                youth_min_income is not None
                and youth_income <= youth_min_income
            ):
                failed.append("YOUTH_HOUSEHOLD_INCOME")

                condition_details.append(
                    {
                        "condition": "YOUTH_HOUSEHOLD_INCOME",
                        "result": "FAILED",
                        "current_value": youth_income,
                        "required_min": int(youth_min_income),
                        "message": (
                            f"청년가구 월 소득이 "
                            f"{int(youth_min_income):,}원 초과 필요"
                        ),
                    }
                )

            # 최대 소득 기준 초과
            elif (
                youth_max_income is not None
                and youth_income > youth_max_income
            ):
                failed.append("YOUTH_HOUSEHOLD_INCOME")

                condition_details.append(
                    {
                        "condition": "YOUTH_HOUSEHOLD_INCOME",
                        "result": "FAILED",
                        "current_value": youth_income,
                        "required_max": int(youth_max_income),
                        "message": (
                            f"청년가구 월 소득이 "
                            f"{int(youth_max_income):,}원 이하 필요"
                        ),
                    }
                )

            else:
                matched.append("YOUTH_HOUSEHOLD_INCOME")

        # -------------------------------------------------
        # 본인 소득
        # -------------------------------------------------

        personal_min_ratio = personal_ratio["min"]
        personal_max_ratio = personal_ratio["max"]

        if personal_min_ratio is not None or personal_max_ratio is not None:
            personal_income = user["personal_monthly_income"]

            personal_min_income = (
                median_income * personal_min_ratio
                if personal_min_ratio is not None
                else None
            )

            personal_max_income = (
                median_income * personal_max_ratio
                if personal_max_ratio is not None
                else None
            )

            if (
                personal_min_income is not None
                and personal_income <= personal_min_income
            ):
                failed.append("PERSONAL_INCOME")

                condition_details.append(
                    {
                        "condition": "PERSONAL_INCOME",
                        "result": "FAILED",
                        "current_value": personal_income,
                        "required_min": int(personal_min_income),
                        "message": (
                            f"본인 월 소득이 "
                            f"{int(personal_min_income):,}원 초과 필요"
                        ),
                    }
                )

            elif (
                personal_max_income is not None
                and personal_income > personal_max_income
            ):
                failed.append("PERSONAL_INCOME")

                condition_details.append(
                    {
                        "condition": "PERSONAL_INCOME",
                        "result": "FAILED",
                        "current_value": personal_income,
                        "required_max": int(personal_max_income),
                        "message": (
                            f"본인 월 소득이 "
                            f"{int(personal_max_income):,}원 이하 필요"
                        ),
                    }
                )

            else:
                matched.append("PERSONAL_INCOME")


    # -----------------------------------------------------
    # ASSETS
    # -----------------------------------------------------

    assets_rule = rules["assets"]
    total_assets_max = assets_rule["total_assets_max"]

    if total_assets_max is not None:
        if user["total_assets"] <= total_assets_max:
            matched.append("TOTAL_ASSETS")
        else:
            failed.append("TOTAL_ASSETS")

    # -----------------------------------------------------
    # ADDITIONAL_CONDITIONS
    # -----------------------------------------------------

    # 실제 정책 조건은 존재하지만
    # P0 15개 입력만으로 자동판정하지 않는 조건
    for condition in rules["additional_conditions"]:
        missing.append(condition)

        condition_details.append(
            {
                "condition": condition,
                "result": "MISSING",
                "current_value": None,
                "message": f"{condition} 추가 확인 필요",
            }
        )

    # -----------------------------------------------------
    # FINAL STATUS
    # -----------------------------------------------------

    hard_failed = [
        condition
        for condition in failed
        if condition in HARD_FAIL_CONDITIONS
    ]

    adjustable_failed = [
        condition
        for condition in failed
        if condition in ADJUSTABLE_FAIL_CONDITIONS
    ]

    # 1순위:
    # 현재 자격 자체에서 명확한 탈락 조건 존재
    if hard_failed:
        status = EligibilityStatus.NOT_ELIGIBLE

    # 2순위:
    # 희망 독립 조건을 조정하면 가능
    elif adjustable_failed:
        status = EligibilityStatus.CONDITIONAL

    # 3순위:
    # 자동판정 가능한 조건은 통과했지만
    # 추가 확인 조건 존재
    elif missing:
        status = EligibilityStatus.NEED_MORE_INFO

    # 4순위:
    # 모든 자동판정 조건 충족
    else:
        status = EligibilityStatus.AVAILABLE

    return status, matched, failed, missing, condition_details


# =========================================================
# 5. 전체 정책 매칭
# =========================================================

def match_policies(
    user: dict[str, Any],
    target: dict[str, Any],
    diagnosis_id: int,
    first_match_id: int,
) -> list[dict[str, Any]]:

    matches: list[dict[str, Any]] = []
    matched_at = datetime.now(KST)

    policies = _load_policies()

    for offset, policy in enumerate(policies):

        status, matched, failed, missing, condition_details = _policy_result(
            policy,
            user,
            target,
        )

        matches.append(
            {
                "match_id": first_match_id + offset,
                "user_id": user.get("user_id"),
                "diagnosis_id": diagnosis_id,
                "policy_id": policy["policy_id"],

                "title": policy["title"],
                "description": policy["description"],

                "policy_category": policy[
                    "policy_category"
                ],
                "policy_region": policy[
                    "policy_region"
                ],
                "policy_provider": policy[
                    "policy_provider"
                ],

                "eligibility_status": status,

                "matched_conditions": matched,
                "failed_conditions": failed,
                "missing_conditions": missing,
                "condition_details": condition_details,

                "rank": offset + 1,

                "support_amount": policy[
                    "support_amount"
                ],
                "support_amount_unit": policy[
                    "support_amount_unit"
                ],
                "support_amount_text": policy[
                    "support_amount_text"
                ],

                "eligibility_text": policy[
                    "eligibility_text"
                ],

                "application_start": policy[
                    "application_start"
                ],
                "application_end": policy[
                    "application_end"
                ],
                "application_period_type": policy[
                    "application_period_type"
                ],

                "source_url": policy["source_url"],
                "checked_at": policy["checked_at"],
                "matched_at": matched_at,
            }
        )

    return matches