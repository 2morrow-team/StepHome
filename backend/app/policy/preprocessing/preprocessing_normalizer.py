import re
from typing import Any

POLICY_CATEGORY_MAP = {
    "월세지원": "RENT_SUPPORT",
    "월세 지원": "RENT_SUPPORT",
    "주거비지원": "RENT_SUPPORT",
    "주거비 지원": "RENT_SUPPORT",
    "RENT_SUPPORT": "RENT_SUPPORT",

    "공공임대": "PUBLIC_RENTAL",
    "공공 임대": "PUBLIC_RENTAL",
    "PUBLIC_RENTAL": "PUBLIC_RENTAL",

    "대출": "LOAN",
    "주거대출": "LOAN",
    "전세자금대출": "LOAN",
    "LOAN": "LOAN",
}


APPLICATION_PERIOD_TYPE_MAP = {
    "기간형": "FIXED",
    "기간 지정": "FIXED",
    "고정기간": "FIXED",
    "FIXED": "FIXED",
    "기간": "FIXED",

    "상시": "ALWAYS_OPEN",
    "상시모집": "ALWAYS_OPEN",
    "ALWAYS_OPEN": "ALWAYS_OPEN",

    "공고형": "NOTICE_BASED",
    "공고별": "NOTICE_BASED",
    "NOTICE_BASED": "NOTICE_BASED",

    "미상": "UNKNOWN",
    "알 수 없음": "UNKNOWN",
    "UNKNOWN": "UNKNOWN",
}


SUPPORT_AMOUNT_UNIT_MAP = {
    "월": "MONTH",
    "월 최대": "MONTH",
    "매월": "MONTH",
    "MONTH": "MONTH",
    "만원/월": "MONTH",
    "원/월": "MONTH",

    "연": "YEAR",
    "연간": "YEAR",
    "YEAR": "YEAR",

    "총액": "TOTAL",
    "총": "TOTAL",
    "TOTAL": "TOTAL",

    "기타": "OTHER",
    "OTHER": "OTHER",
}


INCOME_BASIS_MAP = {
    "기준 중위소득": "MEDIAN_INCOME",
    "중위소득": "MEDIAN_INCOME",
    "MEDIAN_INCOME": "MEDIAN_INCOME",
}

REGION_MAP = {
    "전국": "NATIONAL",

    "서울": "SEOUL",
    "서울시": "SEOUL",
    "서울특별시": "SEOUL",

    "부산": "BUSAN",
    "부산시": "BUSAN",
    "부산광역시": "BUSAN",

    "대구": "DAEGU",
    "대구시": "DAEGU",
    "대구광역시": "DAEGU",

    "인천": "INCHEON",
    "인천시": "INCHEON",
    "인천광역시": "INCHEON",

    "광주": "GWANGJU",
    "광주시": "GWANGJU",
    "광주광역시": "GWANGJU",

    "대전": "DAEJEON",
    "대전시": "DAEJEON",
    "대전광역시": "DAEJEON",

    "울산": "ULSAN",
    "울산시": "ULSAN",
    "울산광역시": "ULSAN",

    "세종": "SEJONG",
    "세종시": "SEJONG",
    "세종특별자치시": "SEJONG",

    "경기": "GYEONGGI",
    "경기도": "GYEONGGI",

    "강원": "GANGWON",
    "강원도": "GANGWON",
    "강원특별자치도": "GANGWON",

    "충북": "CHUNGBUK",
    "충청북도": "CHUNGBUK",

    "충남": "CHUNGNAM",
    "충청남도": "CHUNGNAM",

    "전북": "JEONBUK",
    "전라북도": "JEONBUK",
    "전북특별자치도": "JEONBUK",

    "전남": "JEONNAM",
    "전라남도": "JEONNAM",

    "경북": "GYEONGBUK",
    "경상북도": "GYEONGBUK",

    "경남": "GYEONGNAM",
    "경상남도": "GYEONGNAM",

    "제주": "JEJU",
    "제주도": "JEJU",
    "제주특별자치도": "JEJU",
}


HOUSING_STATUS_MAP = {
    "무주택": "NO_HOME",
    "무주택자": "NO_HOME",
    "주택 미소유": "NO_HOME",

    "유주택": "HAS_HOME",
    "유주택자": "HAS_HOME",
    "주택 소유": "HAS_HOME",
}


HOUSING_TYPE_MAP = {
    "월세": "MONTHLY_RENT",
    "월세주택": "MONTHLY_RENT",

    "전세": "JEONSE",
    "전세주택": "JEONSE",
}


MARITAL_STATUS_MAP = {
    "미혼": "UNMARRIED",
    "혼인 중이 아님": "UNMARRIED",
    "혼인 중인 자 제외": "UNMARRIED",
    "혼인 중인 사람 제외": "UNMARRIED",
    "미혼자": "UNMARRIED",

    "기혼": "MARRIED",
    "혼인": "MARRIED",
    "기혼자": "MARRIED",
}


EMPLOYMENT_STATUS_MAP = {
    "취업자": "EMPLOYED",
    "재직자": "EMPLOYED",
    "직장인": "EMPLOYED",

    "취업준비생": "JOB_SEEKER",
    "취업 준비생": "JOB_SEEKER",
    "구직자": "JOB_SEEKER",
    "직장에 재직 중이지 않은 자": "JOB_SEEKER",

    "학생": "STUDENT",
    "대학생": "STUDENT",

    "기타": "OTHER",
}

def normalize_policy_category(value: str) -> str:
    return _normalize_mapped_value(
        value,
        POLICY_CATEGORY_MAP,
    )


def normalize_application_period_type(
    value: str,
) -> str:
    return _normalize_mapped_value(
        value,
        APPLICATION_PERIOD_TYPE_MAP,
    )


def normalize_support_amount_unit(
    value: str,
) -> str:
    return _normalize_mapped_value(
        value,
        SUPPORT_AMOUNT_UNIT_MAP,
    )


def normalize_income_basis(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    return _normalize_mapped_value(
        value,
        INCOME_BASIS_MAP,
    )

def _normalize_text(value: str) -> str:
    """
    문자열 앞뒤 공백과 불필요한 공백을 정리한다.
    """
    return re.sub(r"\s+", " ", value.strip())

def _normalize_mapped_value(
    value: str,
    mapping: dict[str, str],
) -> str:
    """
    문자열 표현을 mapping에 정의된 표준 Enum 값으로 정규화한다.

    - 앞뒤 및 중복 공백 정리
    - 이미 Enum 값이면 그대로 반환
    - 일반 mapping 조회
    - 내부 공백을 제거한 뒤 다시 mapping 조회
    - 매칭되지 않으면 원래 정리된 값을 반환하여
      이후 Pydantic validation에서 검증하도록 한다.
    """
    cleaned = _normalize_text(value)

    # 이미 표준 Enum 값이면 그대로 반환
    if cleaned in mapping.values():
        return cleaned

    # 정확히 일치하는 표현
    if cleaned in mapping:
        return mapping[cleaned]

    # 내부 공백 차이까지 허용
    compact = cleaned.replace(" ", "")

    compact_mapping = {
        key.replace(" ", ""): mapped_value
        for key, mapped_value in mapping.items()
    }

    if compact in compact_mapping:
        return compact_mapping[compact]

    # 알 수 없는 값을 임의로 추측하지 않는다.
    # 이후 Pydantic validation에서 실패하도록 그대로 전달한다.
    return cleaned


def normalize_region(value: str) -> str:
    """
    지역 표현을 Region Enum 값으로 정규화한다.
    """
    return _normalize_mapped_value(
        value,
        REGION_MAP,
    )


def normalize_housing_status(value: str) -> str:
    """
    주택 소유 여부 표현을 HousingStatus Enum 값으로 정규화한다.
    """
    return _normalize_mapped_value(
        value,
        HOUSING_STATUS_MAP,
    )


def normalize_housing_type(value: str) -> str:
    """
    주거 형태를 HousingType Enum 값으로 정규화한다.
    """
    return _normalize_mapped_value(
        value,
        HOUSING_TYPE_MAP,
    )


def normalize_marital_status(value: str) -> str:
    """
    혼인 상태를 MaritalStatus Enum 값으로 정규화한다.
    """
    return _normalize_mapped_value(
        value,
        MARITAL_STATUS_MAP,
    )


def normalize_employment_status(value: str) -> str:
    """
    고용 상태를 EmploymentStatus Enum 값으로 정규화한다.
    """
    return _normalize_mapped_value(
        value,
        EMPLOYMENT_STATUS_MAP,
    )


def normalize_money(value: int | float | str | None) -> int | None:
    """
    금액 표현을 원 단위 정수로 정규화한다.

    예:
        600000      -> 600000
        "600000"    -> 600000
        "60만원"    -> 600000
        "8천만원"   -> 80000000
        "1억 2,200만원" -> 122000000
    """
    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError("bool 타입은 금액으로 사용할 수 없습니다.")

    if isinstance(value, (int, float)):
        if value < 0:
            raise ValueError("금액은 음수일 수 없습니다.")

        return int(value)

    cleaned = _normalize_text(value)
    cleaned = cleaned.replace(",", "").replace(" ", "")

    # 순수 숫자
    if re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        return int(float(cleaned))

    total = 0

    # 억 단위
    eok_match = re.search(r"(\d+(?:\.\d+)?)억", cleaned)

    if eok_match:
        total += int(float(eok_match.group(1)) * 100_000_000)

    # 천만원 단위
    cheon_man_match = re.search(
        r"(\d+(?:\.\d+)?)천만원",
        cleaned,
    )

    if cheon_man_match:
        total += int(
            float(cheon_man_match.group(1))
            * 10_000_000
        )

    # 만원 단위
    # "8천만원"에서 "만원"을 중복 계산하지 않도록
    # 천만원 패턴을 먼저 제거한다.
    remaining = re.sub(
        r"\d+(?:\.\d+)?천만원",
        "",
        cleaned,
    )

    man_match = re.search(
        r"(\d+(?:\.\d+)?)만원",
        remaining,
    )

    if man_match:
        total += int(float(man_match.group(1)) * 10_000)

    # 원 단위
    won_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)원",
        cleaned,
    )

    if won_match:
        return int(float(won_match.group(1)))

    if total > 0:
        return total

    raise ValueError(
        f"금액 표현을 정규화할 수 없습니다: {value}"
    )


def _normalize_list(
    values: list[str] | None,
    normalizer,
) -> list[str]:
    if not values:
        return []

    return [
        normalizer(value)
        for value in values
    ]


def normalize_policy_data(
    policy: dict[str, Any],
) -> dict[str, Any]:
    """
    LLM이 추출한 정책 dict를
    최종 Policy Schema에 가까운 형태로 정규화한다.

    입력 dict 자체는 수정하지 않고 복사본을 반환한다.
    """
    normalized = policy.copy()

    rules = normalized.get(
        "eligibility_rules",
        {},
    ).copy()

    # 지역
    rules["current_region"] = _normalize_list(
        rules.get("current_region"),
        normalize_region,
    )

    rules["target_region"] = _normalize_list(
        rules.get("target_region"),
        normalize_region,
    )

    # 주택 소유 여부
    rules["housing_status"] = _normalize_list(
        rules.get("housing_status"),
        normalize_housing_status,
    )

    # 혼인 상태
    rules["marital_status"] = _normalize_list(
        rules.get("marital_status"),
        normalize_marital_status,
    )

    # 고용 상태
    rules["employment_status"] = _normalize_list(
        rules.get("employment_status"),
        normalize_employment_status,
    )

    # 소득 조건
    income = rules.get(
        "income",
        {},
    ).copy()

    income["basis"] = normalize_income_basis(
        income.get("basis")
    )

    rules["income"] = income

    # 주거 조건
    housing = rules.get(
        "housing",
        {},
    ).copy()

    housing["type"] = _normalize_list(
        housing.get("type"),
        normalize_housing_type,
    )

    housing["deposit_max"] = normalize_money(
        housing.get("deposit_max")
    )

    housing["monthly_rent_max"] = normalize_money(
        housing.get("monthly_rent_max")
    )

    rules["housing"] = housing

    # 자산
    assets = rules.get(
        "assets",
        {},
    ).copy()

    assets["total_assets_max"] = normalize_money(
        assets.get("total_assets_max")
    )

    rules["assets"] = assets

    normalized["eligibility_rules"] = rules

    # 대표 지원금
    normalized["support_amount"] = normalize_money(
        normalized.get("support_amount")
    )

    normalized["policy_category"] = normalize_policy_category(
        normalized["policy_category"]
    )

    normalized["application_period_type"] = (
        normalize_application_period_type(
            normalized["application_period_type"]
        )
    )

    normalized["support_amount_unit"] = (
        normalize_support_amount_unit(
            normalized["support_amount_unit"]
        )
    )

    return normalized