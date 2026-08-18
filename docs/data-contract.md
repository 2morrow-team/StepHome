# Data Contract

> StepHome MVP의 Frontend / Backend / Policy / AI 공통 데이터 계약이다.  
> 필드명, 타입, Enum, nullable 여부와 JSON 구조를 임의로 변경하지 않는다.

## 1. 공통 형식

| 항목 | 규칙 | 예시 |
|---|---|---|
| 금액 | KRW 원 단위 `INT` | `2500000` |
| 날짜 | `YYYY-MM-DD` | `"2027-03-01"` |
| API datetime | ISO 8601 | `"2026-08-16T20:00:00+09:00"` |
| DB 날짜 | `DATE` | `2027-03-01` |
| DB datetime | `DATETIME` | `2026-08-16 20:00:00` |
| 서버 기준 시간대 | `Asia/Seoul (UTC+9)` | - |
| Enum | `UPPER_SNAKE_CASE` | `MONTHLY_RENT` |
| ID | `INT`, Backend 생성 | `user_id: 1` |
| 없는 값 | 빈 문자열 대신 `null` | `"policy_id": null` |

---

## 2. 핵심 Enum

### EmploymentStatus

```text
JOB_SEEKER
EMPLOYED
STUDENT
OTHER
```

### HousingType

```text
MONTHLY_RENT
JEONSE
```

### HousingStatus

```text
NO_HOME
HAS_HOME
```

`housing_status`는 현재 거주 형태가 아니라 **본인 주택 소유 여부**를 의미한다.

```text
NO_HOME
→ 본인 소유 주택 없음

HAS_HOME
→ 본인 소유 주택 있음
```

기존 `FAMILY_HOME` 등 현재 거주 형태를 나타내는 값과는 의미가 다르다.

### MaritalStatus

```text
UNMARRIED
MARRIED
```

결혼 예정 등 MVP P0만으로 확정할 수 없는 조건은 정책에 따라 `NEED_MORE_INFO`로 처리할 수 있다.

### Region

```text
NATIONAL
SEOUL
BUSAN
DAEGU
INCHEON
GWANGJU
DAEJEON
ULSAN
SEJONG
GYEONGGI
GANGWON
CHUNGBUK
CHUNGNAM
JEONBUK
JEONNAM
GYEONGBUK
GYEONGNAM
JEJU
```

### PolicyCategory

```text
LOAN
RENT_SUPPORT
PUBLIC_RENTAL
```

### SupportAmountUnit

```text
MONTH
YEAR
TOTAL
OTHER
```

### ApplicationPeriodType

```text
FIXED
ALWAYS_OPEN
NOTICE_BASED
UNKNOWN
```

의미:

```text
FIXED
→ 정해진 신청기간 있음

ALWAYS_OPEN
→ 상시 신청

NOTICE_BASED
→ 공고별 모집

UNKNOWN
→ 현재 확인 불가
```

### EligibilityStatus

```text
AVAILABLE
CONDITIONAL
NEED_MORE_INFO
NOT_ELIGIBLE
```

| 값 | 의미 |
|---|---|
| `AVAILABLE` | 자동 판정 가능한 현재 조건을 충족 |
| `CONDITIONAL` | 희망 독립 조건을 조정하면 충족 가능 |
| `NEED_MORE_INFO` | 추가 확인 조건 때문에 자동 판정을 완료할 수 없음 |
| `NOT_ELIGIBLE` | 현재 사용자 자격 조건에서 명확한 미충족 조건 존재 |

### ActionType

```text
SAVING
POLICY
HOUSING
CONTRACT
```

### Timing

```text
NOW
PREPARE
SEARCH_HOUSE
BEFORE_CONTRACT
```

### ActionStatus

```text
TODO
IN_PROGRESS
DONE
```

---

## 3. P0 입력

Frontend는 최초 `/plan` 요청에서 총 **15개 필드**를 Backend에 전달한다.

```text
User   10개
Target  5개
--------------
총      15개
```

---

## 4. User

| 필드 | 타입 | 의미 | Demo |
|---|---|---|---|
| `user_id` | INT | 사용자 ID, Backend 생성 | `1` |
| `age` | INT | 만 나이 | `25` |
| `employment_status` | ENUM | 취업 상태 | `EMPLOYED` |
| `current_region` | ENUM | 현재 거주 지역 | `SEOUL` |
| `personal_monthly_income` | INT | 본인 월 소득 | `2500000` |
| `total_assets` | INT | 독립 준비에 활용 가능한 현재 보유자금 | `30000000` |
| `monthly_savings` | INT | 월 저축액 | `500000` |
| `housing_status` | ENUM | 본인 주택 소유 여부 | `NO_HOME` |
| `youth_household_monthly_income` | INT | 청년가구 월 소득 | `2500000` |
| `youth_household_size` | INT | 청년가구 가구원 수 | `1` |
| `marital_status` | ENUM | 혼인 여부 | `UNMARRIED` |

Validation:

```text
age
→ 19~39

금액
→ 0 이상 정수

monthly_savings
→ 0 이상

youth_household_size
→ 1 이상
```

비상자금은 P0 입력에서 사용하지 않는다.

---

## 5. Target

| 필드 | 타입 | 의미 | Demo |
|---|---|---|---|
| `target_id` | INT | 독립 목표 ID, Backend 생성 | `1` |
| `user_id` | INT | User ID | `1` |
| `planned_move_in_date` | DATE | 독립 예정일 | `2027-03-01` |
| `desired_deposit` | INT | 희망 보증금 | `90000000` |
| `desired_monthly_rent` | INT | 희망 월세 | `500000` |
| `desired_housing_type` | ENUM | 희망 주거 형태 | `MONTHLY_RENT` |
| `desired_region` | ENUM | 희망 거주 지역 | `SEOUL` |

Validation:

```text
planned_move_in_date
→ 오늘보다 미래

desired_deposit
→ 0 이상

desired_monthly_rent
→ 0 이상
```

`desired_region`은 Frontend에서 직접 입력받는다.

Backend가 임의로 서울을 기본값으로 넣지 않는다.

---

## 6. Policy

| 필드 | 타입 | 의미 |
|---|---|---|
| `policy_id` | INT | 정책 ID |
| `title` | VARCHAR | 정책명 |
| `description` | TEXT | 정책 설명 |
| `policy_category` | ENUM | 정책 카테고리 |
| `policy_region` | VARCHAR | 정책 적용 지역 |
| `policy_provider` | VARCHAR/null | 정책 제공기관 |
| `application_start` | DATE/null | 신청 시작일 |
| `application_end` | DATE/null | 신청 종료일 |
| `application_period_type` | ENUM | 신청기간 형태 |
| `support_amount` | INT/null | 대표 지원금액 |
| `support_amount_unit` | ENUM | 대표 지원금액 단위 |
| `support_amount_text` | TEXT | 지원 내용 상세 |
| `family_earnings` | TEXT/null | 사람이 읽는 가구소득 조건 |
| `eligibility_text` | TEXT | 상세 자격조건 |
| `eligibility_rules` | JSON | Rule Engine 자동 판정 구조 |
| `source_url` | TEXT | 공식 출처 |
| `checked_at` | DATETIME | 마지막 확인 시점 |

현재 Demo에서는 실제 정책 `policy_id 1~6`을 사용한다.

---

## 7. Policy eligibility_rules

모든 Demo Policy는 다음 공통 JSON 구조를 따른다.

```json
{
  "age": {
    "min": null,
    "max": null
  },
  "current_region": [],
  "target_region": [],
  "housing_status": [],
  "marital_status": [],
  "employment_status": [],
  "income": {
    "personal_ratio": {
      "min": null,
      "max": null
    },
    "youth_household_ratio": {
      "min": null,
      "max": null
    },
    "basis": null
  },
  "assets": {
    "total_assets_max": null
  },
  "housing": {
    "type": [],
    "deposit_max": null,
    "monthly_rent_max": null
  },
  "additional_conditions": []
}
```

### null / 빈 배열 의미

연령 조건:

```text
age.min = null
→ 최소 연령 조건 없음

age.max = null
→ 최대 연령 조건 없음
```

배열 조건:

```text
[]
→ 해당 배열 조건에 자동 판정 제한 없음
```

예:

```json
"employment_status": []
```

이면 취업 상태 때문에 자동 탈락시키지 않는다.

### Income Ratio

`personal_ratio`와 `youth_household_ratio`는 항상 `{min, max}` 객체 구조를 사용한다.

예:

```json
"youth_household_ratio": {
  "min": 0.48,
  "max": 1.5
}
```

의미:

```text
기준 중위소득 48% 초과 ~ 150% 이하
```

각 값의 의미:

```text
ratio.min = null
→ 소득비율 하한 조건 없음

ratio.max = null
→ 소득비율 상한 조건 없음
```

둘 다 `null`인 경우:

```json
{
  "min": null,
  "max": null
}
```

해당 소득비율 조건으로 자동 제한하지 않는다.

### income.basis

현재 Rule Engine에서 자동 계산하는 기준:

```text
MEDIAN_INCOME
→ 기준 중위소득
```

`basis = null`이면 해당 소득 기준에 따른 자동 계산을 수행하지 않는다.

### additional_conditions

```text
additional_conditions
→ 실제 정책 조건은 존재하지만
   현재 P0 15개만으로 자동 판정하지 않는 조건
```

예:

```text
LIVE_SEPARATELY_FROM_PARENTS
ORIGINAL_HOUSEHOLD_INCOME_REQUIREMENT
PRIORITY_REQUIREMENTS
ASSET_REQUIREMENT
HOUSEHOLD_HEAD_REQUIREMENT
```

추가 확인 조건이 남아 있고 다른 명확한 실패 조건이 없다면 Rule Engine은 `NEED_MORE_INFO`로 판정할 수 있다.

---

## 8. Diagnosis

| 필드 | 타입 | 의미 |
|---|---|---|
| `diagnosis_id` | INT | 진단 ID |
| `user_id` | INT | 사용자 ID |
| `target_id` | INT | Target ID |
| `readiness_score` | INT | 전체 준비도, 0~100 |
| `fund_score` | FLOAT | 초기자금 준비도, 최대 70 |
| `saving_score` | FLOAT | 저축계획 준비도, 최대 30 |
| `required_initial_fund` | INT | 필요한 초기자금 |
| `initial_fund_gap` | INT | 부족 초기자금 |
| `required_monthly_saving` | INT | 목표일까지 필요한 월 저축액 |
| `estimated_months` | INT/null | 현재 저축속도 기준 예상 준비기간 |
| `calculated_at` | DATETIME | 계산 시점 |

사용하지 않는 기존 필드:

```text
emergency_score
target_emergency_fund
emergency_fund_gap
```

또한 별도의 고정 이사비/초기비용을 `required_initial_fund`에 임의로 추가하지 않는다.

상세 계산식은 `diagnosis-rules.md`를 따른다.

---

## 9. PolicyMatch

| 필드 | 타입 | 의미 |
|---|---|---|
| `match_id` | INT/null | 매칭 결과 ID |
| `user_id` | INT/null | 사용자 ID |
| `diagnosis_id` | INT/null | 진단 ID |
| `policy_id` | INT | 정책 ID |
| `title` | VARCHAR | 정책명 |
| `description` | TEXT | 정책 설명 |
| `policy_category` | ENUM | 정책 카테고리 |
| `policy_region` | VARCHAR | 정책 적용 지역 |
| `policy_provider` | VARCHAR/null | 제공기관 |
| `eligibility_status` | ENUM | 정책 판정 상태 |
| `matched_conditions` | JSON | 충족된 자동 판정 조건 |
| `failed_conditions` | JSON | 미충족 조건 |
| `missing_conditions` | JSON | 추가 확인 조건 |
| `condition_details` | JSON | 조건별 상세 판정값 |
| `rank` | INT/null | 표시 순위 |
| `support_amount` | INT/null | 대표 지원금액 |
| `support_amount_unit` | ENUM | 지원금 기준 단위 |
| `support_amount_text` | TEXT | 지원 상세 |
| `eligibility_text` | TEXT | 자격조건 설명 |
| `application_start` | DATE/null | 신청 시작일 |
| `application_end` | DATE/null | 신청 종료일 |
| `application_period_type` | ENUM | 신청기간 형태 |
| `source_url` | TEXT | 공식 출처 |
| `checked_at` | DATETIME/null | 정책 확인 시점 |
| `matched_at` | DATETIME/null | 정책 판정 시점 |

### condition_details

Rule Engine은 자동 판정 결과의 상세 값을 `condition_details`로 제공할 수 있다.

보증금 조건 실패 예:

```json
{
  "condition": "DEPOSIT_LIMIT",
  "result": "FAILED",
  "current_value": 90000000,
  "required_max": 80000000,
  "message": "희망 보증금 80,000,000원 이하 필요"
}
```

지역 조건 실패 예:

```json
{
  "condition": "TARGET_REGION",
  "result": "FAILED",
  "current_value": "BUSAN",
  "required_values": [
    "SEOUL"
  ],
  "message": "희망 거주지역을 SEOUL 중 하나로 조정 필요"
}
```

추가 확인 조건 예:

```json
{
  "condition": "ASSET_REQUIREMENT",
  "result": "MISSING",
  "current_value": null,
  "message": "ASSET_REQUIREMENT 추가 확인 필요"
}
```

---

## 10. Policy 판정 우선순위

Rule Engine은 실패 조건을 크게 Hard Fail과 Adjustable Fail로 구분한다.

### Hard Fail

현재 사용자 자격 자체가 정책 기준을 충족하지 못하는 조건:

```text
AGE
CURRENT_REGION
HOUSING_STATUS
MARITAL_STATUS
EMPLOYMENT_STATUS
PERSONAL_INCOME
YOUTH_HOUSEHOLD_INCOME
TOTAL_ASSETS
```

Hard Fail이 존재하면:

```text
NOT_ELIGIBLE
```

### Adjustable Fail

사용자가 희망 독립 조건을 변경하면 충족할 수 있는 조건:

```text
TARGET_REGION
HOUSING_TYPE
DEPOSIT_LIMIT
MONTHLY_RENT_LIMIT
```

Hard Fail 없이 Adjustable Fail이 존재하면:

```text
CONDITIONAL
```

`CONDITIONAL` 상태에서 `missing_conditions`도 존재할 수 있다.

이 경우 AI는 조건 조정만으로 즉시 신청 가능하다고 단정하지 않고, 추가 확인이 필요하다는 내용도 함께 안내한다.

### Missing

P0 15개만으로 자동 판정하지 않는 조건:

```text
additional_conditions
```

Hard Fail과 Adjustable Fail이 없고 Missing만 존재하면:

```text
NEED_MORE_INFO
```

모든 자동 판정 조건을 충족하고 Missing도 없으면:

```text
AVAILABLE
```

---

## 11. ActionPlan

AI가 생성하는 값:

```text
priority
action_type
timing
title
description
reason
policy_id
due_date
```

Backend가 생성하는 값:

```text
action_id
plan_id
user_id
diagnosis_id
status
created_at
```

`status` 기본값:

```text
TODO
```

### due_date 규칙

AI Planner는 정책의 `application_period_type`을 기준으로 `due_date`를 생성한다.

```text
FIXED
→ due_date = application_end

ALWAYS_OPEN
NOTICE_BASED
UNKNOWN
→ due_date = null
```

Backend/AI Validator는 `FIXED` 정책의 `due_date`가 `application_end`와 동일한지 검증한다.

---

## 12. Re-planning

P0 15개는 모두 변경 가능한 구조로 구현한다.

Request에서는 실제로 변경할 값만 `changes`에 전달한다.

대표 Demo:

```json
{
  "changes": {
    "desired_deposit": 70000000
  }
}
```

Before:

```text
desired_deposit = 90,000,000
```

After:

```text
desired_deposit = 70,000,000
```

Backend는 실제 변경된 필드를 다음과 같이 전달한다.

```json
{
  "changed_fields": {
    "desired_deposit": {
      "before": 90000000,
      "after": 70000000
    }
  }
}
```

대표 Demo에서 Policy 6:

```text
Before
desired_deposit = 90,000,000
→ deposit_max 80,000,000 초과
→ CONDITIONAL

After
desired_deposit = 70,000,000
→ deposit_max 충족
→ AVAILABLE
```

Re-planning 시 Backend는:

```text
changed_fields
previous Diagnosis
previous PolicyMatch
previous ActionPlan
current User
current Target
current Diagnosis
current PolicyMatch
```

를 바탕으로 AI Re-planning Input을 구성한다.

---

## 13. AI Input Contract

AI는 Backend에서 이미 계산·판정된 결과를 사용한다.

AI가 Diagnosis를 다시 계산하거나 Policy 자격을 다시 판정하지 않는다.

### User Context

```text
age
current_region
employment_status
marital_status
youth_household_monthly_income
youth_household_size
personal_monthly_income
total_assets
monthly_savings
housing_status
```

### Target Context

```text
planned_move_in_date
desired_region
desired_deposit
desired_monthly_rent
desired_housing_type
```

### Diagnosis Context

```text
readiness_score
fund_score
saving_score
required_initial_fund
initial_fund_gap
required_monthly_saving
estimated_months
```

### Policy Context

최종 AI `prompts.py` 기준으로 다음 필드를 전달한다.

```text
policy_id
title
policy_category
policy_region
policy_provider
eligibility_status
matched_conditions
failed_conditions
missing_conditions
condition_details
rank
support_amount
support_amount_unit
support_amount_text
eligibility_text
description
application_start
application_end
application_period_type
source_url
checked_at
```

AI 입력에는 Rule Engine이 판정한 값을 그대로 전달한다.

---

## 14. AI Candidate 규칙

AI는 LLM이 임의로 Action 종류를 결정하도록 두지 않고, Candidate Generator가 먼저 허용 가능한 Action 후보를 만든다.

### Saving

항상 SAVING 후보를 생성한다.

```text
monthly_savings >= required_monthly_saving
→ SAVING_MAINTAIN

monthly_savings < required_monthly_saving
→ SAVING_ADJUST
```

### AVAILABLE

```text
AVAILABLE
→ POLICY / POLICY_APPLY
```

### CONDITIONAL

실패 조건이 주거 조건이면:

```text
TARGET_REGION
HOUSING_TYPE
DEPOSIT_LIMIT
MONTHLY_RENT_LIMIT
```

```text
→ HOUSING / CONDITION_ADJUST
```

그 외 조정 가능한 조건이면:

```text
→ POLICY / CONDITION_ADJUST
```

### NEED_MORE_INFO

```text
→ POLICY / INFORMATION_NOTICE
```

### NOT_ELIGIBLE

```text
→ 해당 정책 Action 후보 생성하지 않음
```

### CONTRACT

첫 독립 계약 전 안전 확인 Action을 위해 CONTRACT 후보를 항상 포함한다.

---

## 15. Re-plan AI Input

Re-planning AI는 다음 구조를 사용한다.

```text
changed_fields

previous
├── diagnosis
├── matched_policies
└── actions

current
├── user
├── target
├── diagnosis
└── matched_policies
```

`previous.actions`에는 다음 필드를 전달할 수 있다.

```text
priority
action_type
timing
title
description
reason
policy_id
due_date
```

AI는 이전/현재 차이를 활용하여 새로운 전체 ActionPlan을 생성한다.

---

## 16. PK / FK

| 테이블 | PK | FK |
|---|---|---|
| User | `user_id` | - |
| Target | `target_id` | `user_id` |
| Policy | `policy_id` | - |
| Diagnosis | `diagnosis_id` | `user_id`, `target_id` |
| PolicyMatch | `match_id` | `user_id`, `diagnosis_id`, `policy_id` |
| ActionPlan | `action_id` | `user_id`, `diagnosis_id`, `policy_id` |

`plan_id`는 MVP에서 여러 Action을 하나의 플랜으로 묶는 그룹 ID로 사용한다.

---

## 17. 책임 분리

```text
Frontend
→ P0 User / Target 입력

Backend
→ Request Validation
→ Diagnosis 계산
→ 전체 흐름 연결

Policy Rule Engine
→ eligibility_rules 기반 Policy 자격 판정
→ PolicyMatch 생성

AI Candidate Generator
→ PolicyMatch 상태에 따라 허용 가능한 Action 후보 생성

AI Planner
→ Diagnosis + PolicyMatch + Candidate 기반 ActionPlan 생성

AI Validator
→ Action 구조 / Candidate / due_date 규칙 검증

Backend
→ action_id / plan_id / status / timestamp 부여
→ 저장
→ Frontend Response 반환
```
