# 정책 규칙을 실행하는 엔진
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.schemas.schemas import EligibilityStatus


KST = timezone(timedelta(hours=9))
POLICY_DATA_PATH = Path(__file__).parent / "data" / "policies.json"


# --------------------------------------------------
# 1. 정책 데이터 로드
# --------------------------------------------------

def _load_policies() -> list[dict[str, Any]]:
    return json.loads(POLICY_DATA_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------
# 2. 지역 조건 판정
# --------------------------------------------------

def _matches_region(
    allowed_regions: list[str],
    user_region: str,
) -> bool:
    # [] = 해당 정책에 지역 제한 없음
    if not allowed_regions:
        return True

    # NATIONAL = 전국 허용
    if "NATIONAL" in allowed_regions:
        return True

    return user_region in allowed_regions


# --------------------------------------------------
# 3. 기준 중위소득 조회
# --------------------------------------------------

def _get_median_income(household_size: int) -> int | None:
    """
    가구원 수에 따른 기준 중위소득 월 금액을 반환한다.

    TODO:
    최종적으로 팀에서 사용하는 기준 중위소득 표를 여기에 연결해야 한다.

    현재 임의의 금액을 넣지 않기 위해 None을 반환한다.
    """
    return None


# --------------------------------------------------
# 4. 정책 하나 판정
# --------------------------------------------------

def _policy_result(
    policy: dict[str, Any],
    user: dict[str, Any],
    target: dict[str, Any],
) -> tuple[
    EligibilityStatus,
    list[str],
    list[str],
    list[str],
]:
    rules = policy["eligibility_rules"]

    matched: list[str] = []
    failed: list[str] = []
    missing: list[str] = []

    # --------------------------------------------------
    # AGE
    # --------------------------------------------------

    age_rule = rules["age"]
    age_min = age_rule["min"]
    age_max = age_rule["max"]

    if age_min is not None and user["age"] < age_min:
        failed.append("AGE")

    elif age_max is not None and user["age"] > age_max:
        failed.append("AGE")

    else:
        matched.append("AGE")

    # --------------------------------------------------
    # CURRENT_REGION
    # --------------------------------------------------

    current_regions = rules["current_region"]

    if current_regions:
        if _matches_region(
            current_regions,
            user["current_region"],
        ):
            matched.append("CURRENT_REGION")
        else:
            failed.append("CURRENT_REGION")

    # []이면 제한 자체가 없으므로 matched에도 기록하지 않음

    # --------------------------------------------------
    # TARGET_REGION
    # --------------------------------------------------

    target_regions = rules["target_region"]

    if target_regions:
        if _matches_region(
            target_regions,
            target["desired_region"],
        ):
            matched.append("TARGET_REGION")
        else:
            failed.append("TARGET_REGION")

    # --------------------------------------------------
    # HOUSING_STATUS
    # --------------------------------------------------

    housing_status_rules = rules["housing_status"]

    if housing_status_rules:
        if user["housing_status"] in housing_status_rules:
            matched.append("HOUSING_STATUS")
        else:
            failed.append("HOUSING_STATUS")

    # --------------------------------------------------
    # MARITAL_STATUS
    # --------------------------------------------------

    marital_status_rules = rules["marital_status"]

    if marital_status_rules:
        if user["marital_status"] in marital_status_rules:
            matched.append("MARITAL_STATUS")
        else:
            failed.append("MARITAL_STATUS")

    # --------------------------------------------------
    # EMPLOYMENT_STATUS
    # --------------------------------------------------

    employment_status_rules = rules["employment_status"]

    if employment_status_rules:
        if user["employment_status"] in employment_status_rules:
            matched.append("EMPLOYMENT_STATUS")
        else:
            failed.append("EMPLOYMENT_STATUS")

    # --------------------------------------------------
    # HOUSING_TYPE
    # --------------------------------------------------

    housing_rule = rules["housing"]
    housing_types = housing_rule["type"]

    if housing_types:
        if target["desired_housing_type"] in housing_types:
            matched.append("HOUSING_TYPE")
        else:
            failed.append("HOUSING_TYPE")

    # --------------------------------------------------
    # DEPOSIT
    # --------------------------------------------------

    deposit_max = housing_rule["deposit_max"]

    if deposit_max is not None:
        if target["desired_deposit"] <= deposit_max:
            matched.append("DEPOSIT_LIMIT")
        else:
            failed.append("DEPOSIT_LIMIT")

    # --------------------------------------------------
    # MONTHLY_RENT
    # --------------------------------------------------

    monthly_rent_max = housing_rule["monthly_rent_max"]

    if monthly_rent_max is not None:
        if target["desired_monthly_rent"] <= monthly_rent_max:
            matched.append("MONTHLY_RENT_LIMIT")
        else:
            failed.append("MONTHLY_RENT_LIMIT")

    # --------------------------------------------------
    # INCOME
    # --------------------------------------------------

    income_rule = rules["income"]

    personal_ratio = income_rule["personal_ratio"]
    youth_household_ratio = income_rule["youth_household_ratio"]
    income_basis = income_rule["basis"]

    # 현재 Demo Policy에서 자동판정하는 소득조건은
    # MEDIAN_INCOME 기준만 대상으로 한다.
    if income_basis == "MEDIAN_INCOME":

        median_income = _get_median_income(
            user["youth_household_size"]
        )

        # 기준 중위소득표가 아직 연결되지 않은 경우
        if median_income is None:
            missing.append("MEDIAN_INCOME_STANDARD")

        else:
            # 청년가구 소득 조건
            if youth_household_ratio is not None:
                income_limit = (
                    median_income * youth_household_ratio
                )

                if (
                    user["youth_household_monthly_income"]
                    <= income_limit
                ):
                    matched.append(
                        "YOUTH_HOUSEHOLD_INCOME"
                    )
                else:
                    failed.append(
                        "YOUTH_HOUSEHOLD_INCOME"
                    )

            # 본인 소득 조건
            if personal_ratio is not None:
                personal_income_limit = (
                    median_income * personal_ratio
                )

                if (
                    user["personal_monthly_income"]
                    <= personal_income_limit
                ):
                    matched.append(
                        "PERSONAL_INCOME"
                    )
                else:
                    failed.append(
                        "PERSONAL_INCOME"
                    )

    # --------------------------------------------------
    # ASSETS
    # --------------------------------------------------

    assets_rule = rules["assets"]
    total_assets_max = assets_rule["total_assets_max"]

    if total_assets_max is not None:
        if user["total_assets"] <= total_assets_max:
            matched.append("TOTAL_ASSETS")
        else:
            failed.append("TOTAL_ASSETS")

    # --------------------------------------------------
    # ADDITIONAL_CONDITIONS
    # --------------------------------------------------

    additional_conditions = rules["additional_conditions"]

    # additional_conditions는
    # 실제 정책 조건이지만 현재 MVP 입력만으로
    # Rule Engine이 자동 판정할 수 없는 조건
    for condition in additional_conditions:
        missing.append(condition)

    # --------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------

    # 사용자가 목표조건을 바꾸면 충족할 수 있는 조건
    adjustable_conditions = {
        "TARGET_REGION",
        "HOUSING_TYPE",
        "DEPOSIT_LIMIT",
        "MONTHLY_RENT_LIMIT",
    }

    if failed:
        # 실패한 조건이 전부 사용자가 조정 가능한 조건이라면
        # CONDITIONAL
        if all(
            condition in adjustable_conditions
            for condition in failed
        ):
            status = EligibilityStatus.CONDITIONAL

        # 나이, 무주택 여부, 혼인 여부, 소득 등
        # 조정 가능한 조건 외의 실패가 하나라도 있으면
        # NOT_ELIGIBLE
        else:
            status = EligibilityStatus.NOT_ELIGIBLE

    # 명확한 실패는 없지만
    # 추가 확인이 필요한 조건이 존재
    elif missing:
        status = EligibilityStatus.NEED_MORE_INFO

    # 자동 판정 가능한 모든 조건을 충족
    else:
        status = EligibilityStatus.AVAILABLE

    return status, matched, failed, missing


# --------------------------------------------------
# 5. 전체 정책 매칭
# --------------------------------------------------

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

        status, matched, failed, missing = _policy_result(
            policy,
            user,
            target,
        )

        matches.append(
            {
                "match_id": first_match_id + offset,
                "user_id": user["user_id"],
                "diagnosis_id": diagnosis_id,
                "policy_id": policy["policy_id"],
                "title": policy["title"],

                "eligibility_status": status,
                "matched_conditions": matched,
                "failed_conditions": failed,
                "missing_conditions": missing,

                "rank": offset + 1,

                "support_amount": policy["support_amount"],
                "support_amount_text": policy[
                    "support_amount_text"
                ],
                "eligibility_text": policy[
                    "eligibility_text"
                ],
                "description": policy["description"],

                "application_start": policy[
                    "application_start"
                ],
                "application_end": policy[
                    "application_end"
                ],
                "application_period_type": policy[
                    "application_period_type"
                ],

                "region": policy["policy_region"],
                "provider": policy["policy_provider"],
                "category": policy["policy_category"],

                "source_url": policy["source_url"],
                "checked_at": policy["checked_at"],
                "matched_at": matched_at,
            }
        )

    return matches