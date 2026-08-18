import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.policy.preprocessing.preprocessing_schema import (
    ExtractedPolicyData,
)


_PROJECT_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(_PROJECT_ROOT / ".env", override=False)

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
            )

        _client = OpenAI(api_key=api_key)

    return _client


SYSTEM_PROMPT = """
당신은 대한민국 청년 주거지원 정책 원문을
구조화된 데이터로 추출하는 데이터 전처리 도구입니다.

반드시 제공된 정책 원문에 명시된 정보만 추출하세요.

규칙:
1. 정책 자격 여부를 판단하지 마세요.
2. 원문에 없는 조건을 추론하거나 생성하지 마세요.
3. 명확하게 확인되지 않는 조건은 null 또는 []로 반환하세요.
4. additional_conditions에는 age, current_region, target_region,
   housing_status, marital_status, employment_status,
   income, assets, housing으로 이미 구조화된 조건을
   절대 중복해서 기록하지 마세요.

   위 필드로 표현할 수 없는 복합 조건만 기록하세요.

   예:
   - 주민등록상 해당 임차주택 주소지 요건
   - 타 월세지원 사업과의 중복수혜 제한
   - 세대주 요건
   - 부모와 별도 거주 요건
   - 순위별 별도 자격요건
5. 다음 필드는 반드시 지정된 표준값으로 반환하세요.

housing_status:
- 무주택, 무주택자 → NO_HOME
- 유주택, 주택 소유 → HAS_HOME

marital_status:
- 미혼, 혼인 중이 아님, 혼인 중인 자 제외 → UNMARRIED
- 기혼, 혼인 중 → MARRIED

employment_status:
- 취업자, 재직자 → EMPLOYED
- 취업준비생, 구직자 → JOB_SEEKER
- 학생, 대학생 → STUDENT
- 위 분류에 해당하지만 다른 유형 → OTHER

단, 단순히 "재직 중이지 않다"는 표현만으로
JOB_SEEKER라고 추론하지 마세요.
원문에서 취업준비생 또는 구직자라는 의미가 명확한 경우에만
JOB_SEEKER를 반환하세요.

housing.type:
- 월세 → MONTHLY_RENT
- 전세 → JEONSE

지역:
- 서울 → SEOUL
- 부산 → BUSAN
- 대구 → DAEGU
- 인천 → INCHEON
- 광주 → GWANGJU
- 대전 → DAEJEON
- 울산 → ULSAN
- 세종 → SEJONG
- 경기 → GYEONGGI
- 강원 → GANGWON
- 충북 → CHUNGBUK
- 충남 → CHUNGNAM
- 전북 → JEONBUK
- 전남 → JEONNAM
- 경북 → GYEONGBUK
- 경남 → GYEONGNAM
- 제주 → JEJU
- 전국 → NATIONAL

명확한 조건이 없으면 임의로 추론하지 말고 []로 반환하세요.
6. 금액 역시 '8천만원', '60만원'처럼 원문 표현을 유지해도 됩니다.
7. income ratio는 기준 중위소득 60%라면 0.6처럼 비율로 추출하세요.
8. 정책 설명과 자격조건을 임의로 보완하지 마세요.
9. source_url과 checked_at은 입력값을 그대로 사용하세요.
10. 소득 조건은 다음 규칙에 따라 추출하세요.

- income.basis에는 소득 기준의 종류만 기록하세요.
  기준 중위소득 조건이면 반드시 "MEDIAN_INCOME"을 반환하세요.
  퍼센트나 설명 문장을 basis에 포함하지 마세요.

- "본인 소득", "개인 소득"이라고 명시된 경우에만
  personal_ratio에 기록하세요.

- "가구 소득", "가구당 기준 중위소득",
  "청년가구 기준 중위소득"이라고 명시된 경우
  youth_household_ratio에 기록하세요.

- 정책 지원대상 전체에 대해 별도 주체 없이
  기준 중위소득 비율이 제시된 경우에도
  youth_household_ratio에 기록하세요.

- 백분율은 반드시 소수 비율로 변환하세요.
  48% -> 0.48
  60% -> 0.6
  100% -> 1.0
  150% -> 1.5

- 원가구, 부모 포함 가구, 부부합산 소득 등
  현재 Schema로 직접 표현하기 어려운 소득 조건은
  임의로 personal_ratio 또는 youth_household_ratio에 넣지 말고
  additional_conditions에 기록하세요.

예:
"기준 중위소득 48% 초과 150% 이하"
→ personal_ratio.min = null
→ personal_ratio.max = null
→ youth_household_ratio.min = 0.48
→ youth_household_ratio.max = 1.5
→ basis = "MEDIAN_INCOME"

소득 비율이 원문에 명시되어 있는데
ratio 필드를 null로 두고 해당 비율을 basis 문자열에 넣지 마세요.

11. policy_category는 정책의 실제 지원 방식을 기준으로
반드시 다음 값 중 하나로 분류하세요.

- RENT_SUPPORT:
  월세, 임차료, 주거비 등을 현금성으로 지원하는 정책

- PUBLIC_RENTAL:
  공공기관이 주택을 공급하거나 임대하는 정책

- LOAN:
  전세자금, 보증금 등 주거 관련 대출을 제공하는 정책

정책을 운영하는 기관이나 사업의 포괄적인 명칭을
policy_category로 사용하지 마세요.

예:
"월 최대 20만원의 월세를 지원"
→ RENT_SUPPORT

"LH가 주택을 매입하여 청년에게 임대"
→ PUBLIC_RENTAL

"전세자금 최대 1억 5천만원 대출"
→ LOAN

12. application_period_type은 반드시 다음 중 하나로 반환하세요.

- FIXED: 신청 시작일과 종료일이 정해진 경우
- ALWAYS_OPEN: 상시 신청 가능한 경우
- NOTICE_BASED: 개별 모집공고에 따라 신청하는 경우
- UNKNOWN: 원문으로 판단할 수 없는 경우

13. support_amount_unit은 반드시 다음 중 하나로 반환하세요.

- MONTH: 월 단위 지원
- YEAR: 연 단위 지원
- TOTAL: 총액 기준 지원
- OTHER: 위 유형에 해당하지 않거나 판단할 수 없는 경우

14. housing.type에는 주거 또는 임대차 형태만 기록하세요.

반드시 다음 의미에 해당하는 경우에만 housing.type에 기록합니다.

- 월세 → MONTHLY_RENT에 해당
- 전세 → JEONSE에 해당

주택 면적, 주택 종류, 건축물 조건 등은
housing.type으로 기록하지 마세요.

현재 Schema에서 별도 필드로 표현할 수 없는
주택 관련 자격조건은 additional_conditions에 기록하세요.

예:
"임차 전용면적 85제곱미터 이하 주택"
→ housing.type에 기록하지 않음
→ additional_conditions에 기록

"전세주택"
→ housing.type에 기록 가능
15. support_amount에는 실제 금액으로 표현할 수 있는 지원금 또는 대출한도만 기록하세요.

예:
"월 최대 20만원 지원"
→ support_amount = "20만원"
→ support_amount_unit = "MONTH"

"최대 1억 5천만원 대출"
→ support_amount = "1억 5천만원"
→ support_amount_unit = "TOTAL"

다음과 같이 금액이 아닌 비율·할인 수준만 제시된 경우에는
support_amount = null 로 반환하세요.

예:
"시중 시세의 40~50% 수준으로 임대"
→ support_amount = null
→ support_amount_unit = "OTHER"
→ 해당 내용은 support_amount_text에 기록

지원금액을 원 단위 숫자로 환산할 수 없는 정보를
support_amount에 넣지 마세요.
"""


def build_extraction_prompt(
    raw_policy: dict[str, Any],
) -> str:
    return f"""
다음 정책 원문에서 정책 정보를 추출하세요.

policy_id:
{raw_policy["policy_id"]}

source_url:
{raw_policy["source_url"]}

checked_at:
{raw_policy["checked_at"]}

정책 원문:
--------------------
{raw_policy["raw_text"]}
--------------------

정책 원문에 명확히 존재하는 정보만 구조화하세요.

특히 다음 정보를 확인하세요.

- 정책명
- 정책 설명
- 정책 카테고리
- 적용 지역
- 제공 기관
- 신청 기간
- 지원 금액 및 단위
- 연령
- 현재 거주 지역 조건
- 희망 거주 지역 조건
- 무주택 여부
- 혼인 상태
- 취업 상태
- 소득 조건
- 자산 조건
- 주거 형태(월세/전세)
- 보증금 상한
- 월세 상한
- 주택 면적 등 현재 Schema로 표현할 수 없는 주거 조건
- 자동 판정이 어려운 추가 조건
"""


def extract_policy(
    raw_policy: dict[str, Any],
) -> dict[str, Any]:
    """
    정책 원문을 LLM을 통해 구조화한다.

    반환 결과는 아직 최종 정책 데이터가 아니며,
    Normalizer와 Validator를 반드시 거쳐야 한다.
    """

    response = _get_client().responses.parse(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-terra",
        ),
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_extraction_prompt(raw_policy),
            },
        ],
        text_format=ExtractedPolicyData,
        reasoning={
            "effort": os.getenv(
                "OPENAI_REASONING_EFFORT",
                "low",
            )
        },
        max_output_tokens=4096,
    )

    if response.output_parsed is None:
        raise ValueError(
            "LLM이 구조화된 정책 데이터를 반환하지 않았습니다."
        )

    result = response.output_parsed.model_dump(
        mode="json"
    )

    # LLM이 변경하면 안 되는 메타데이터는
    # raw input 값을 그대로 사용한다.
    result["policy_id"] = raw_policy["policy_id"]
    result["source_url"] = raw_policy["source_url"]
    result["checked_at"] = raw_policy["checked_at"]

    return result