# Data Contract

> StepHome MVP의 공통 데이터 스키마 계약이다.  
> Frontend / Backend / Diagnosis / Policy Rule Engine / AI / Mock은 이 문서를 공통 기준으로 사용한다.

## 1. 공통 형식

| 항목 | 규칙 | 예시 |
|---|---|---|
| 금액 | KRW 원 단위 `INT` | `2500000` |
| 날짜 | `YYYY-MM-DD` | `"2027-03-01"` |
| API datetime | ISO 8601 + KST | `"2026-08-16T15:00:00+09:00"` |
| DB 날짜 | `DATE` | `2027-03-01` |
| DB datetime | `DATETIME` | `2026-08-16 15:00:00` |
| 서버 기준 시간대 | `Asia/Seoul (UTC+9)` | - |
| Enum | `UPPER_SNAKE_CASE` | `MONTHLY_RENT` |
| ID | `INT`, Backend/DB 생성 | `user_id: 1` |
| nullable | 값이 없으면 `null`, 빈 문자열 사용 금지 | `"policy_id": null` |

---

## 2. 핵심 Enum

### `employment_status`

```text
JOB_SEEKER
EMPLOYED
STUDENT
OTHER
```

| UI | Enum |
|---|---|
| 취업 준비 중 | `JOB_SEEKER` |
| 재직 중 | `EMPLOYED` |
| 대학생 | `STUDENT` |
| 기타 | `OTHER` |

### `housing_type`

```text
MONTHLY_RENT
JEONSE
```

### `housing_status`

```text
NO_HOME
HAS_HOME
```

MVP에서는 **사용자 본인의 주택 소유 여부**만 입력받는다.

가구원의 주택 소유 여부 등 추가 조건이 필요한 정책은 `NEED_MORE_INFO`로 처리할 수 있다.

### `marital_status`

```text
UNMARRIED
MARRIED
```

결혼 예정 등 MVP Enum으로 표현할 수 없는 세부 혼인 조건이 필요한 경우 `NEED_MORE_INFO`로 처리한다.

### `region`

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

`NATIONAL`은 정책의 전국 적용 범위를 표현할 때 사용할 수 있다.

사용자 지역 입력은 시·도 단위로 받고 시·군·구는 MVP에서 받지 않는다.

### `policy_category`

```text
LOAN
RENT_SUPPORT
PUBLIC_RENTAL
```

### `support_amount_unit`

```text
MONTH
YEAR
TOTAL
OTHER
```

### `application_period_type`

```text
FIXED
ALWAYS_OPEN
NOTICE_BASED
UNKNOWN
```

| 값 | 의미 |
|---|---|
| `FIXED` | 정해진 신청 시작일/종료일 존재 |
| `ALWAYS_OPEN` | 상시 신청 |
| `NOTICE_BASED` | 공고별 모집 |
| `UNKNOWN` | 현재 신청기간 확인 불가 |

### `eligibility_status`

```text
AVAILABLE
CONDITIONAL
NEED_MORE_INFO
NOT_ELIGIBLE
```

| 값 | 의미 |
|---|---|
| `AVAILABLE` | 현재 자동 판정 가능한 조건을 충족 |
| `CONDITIONAL` | 현재 미충족이지만 사용자가 조정 가능한 조건을 변경하면 충족 가능 |
| `NEED_MORE_INFO` | 정책 판정에 추가 정보가 필요하거나 MVP Rule Engine에서 자동 판정하지 않는 조건이 존재 |
| `NOT_ELIGIBLE` | 현재 조건상 정책 대상이 아님 |

### `action_type`

```text
SAVING
POLICY
HOUSING
CONTRACT
```

### `timing`

```text
NOW
PREPARE
SEARCH_HOUSE
BEFORE_CONTRACT
```

### `ActionPlan.status`

```text
TODO
IN_PROGRESS
DONE
```

---

## 3. MVP P0 입력

MVP 최초 입력은 총 **15개**다.

### User — 10개

```text
age
employment_status
current_region
personal_monthly_income
total_assets
monthly_savings
housing_status
youth_household_monthly_income
youth_household_size
marital_status
```

### Target — 5개

```text
planned_move_in_date
desired_deposit
desired_monthly_rent
desired_housing_type
desired_region
```

---

## 4. User

| 필드 | 타입 | 의미 | Demo 예시 |
|---|---|---|---|
| `user_id` | INT | 사용자 ID, Backend 생성 | `1` |
| `age` | INT | 만 나이 | `25` |
| `employment_status` | VARCHAR | 취업 상태 | `EMPLOYED` |
| `current_region` | VARCHAR | 현재 거주 시·도 | `SEOUL` |
| `personal_monthly_income` | INT | 본인 월 소득 | `2500000` |
| `total_assets` | INT | 독립 준비에 사용할 수 있는 현재 총 보유자금 | `30000000` |
| `monthly_savings` | INT | 월 저축액 | `500000` |
| `housing_status` | VARCHAR | 본인 주택 소유 여부 | `NO_HOME` |
| `youth_household_monthly_income` | INT | 청년가구 월 소득 | `2500000` |
| `youth_household_size` | INT | 청년가구 가구원 수 | `1` |
| `marital_status` | VARCHAR | 혼인 여부 | `UNMARRIED` |

### 비상자금

`current_emergency_fund`는 최종 P0 입력에서 제거한다.

따라서 MVP Diagnosis에서도 별도의 비상자금 입력값을 사용하지 않는다.

---

## 5. Target

| 필드 | 타입 | 의미 | Demo 예시 |
|---|---|---|---|
| `target_id` | INT | 독립 목표 ID, Backend 생성 | `1` |
| `user_id` | INT | User FK | `1` |
| `planned_move_in_date` | DATE | 독립 예정일 | `2027-03-01` |
| `desired_deposit` | INT | 희망 보증금 | `90000000` |
| `desired_monthly_rent` | INT | 희망 월세 | `500000` |
| `desired_housing_type` | VARCHAR | 희망 주거 형태 | `MONTHLY_RENT` |
| `desired_region` | VARCHAR | 희망 거주 지역 | `SEOUL` |

`desired_region`은 Backend 고정값이 아니라 **Frontend에서 사용자가 직접 입력하는 P0 값**이다.

---

## 6. Frontend → Backend 사용자 입력 JSON

```json
{
  "user": {
    "age": 25,
    "employment_status": "EMPLOYED",
    "current_region": "SEOUL",
    "personal_monthly_income": 2500000,
    "total_assets": 30000000,
    "monthly_savings": 500000,
    "housing_status": "NO_HOME",
    "youth_household_monthly_income": 2500000,
    "youth_household_size": 1,
    "marital_status": "UNMARRIED"
  },
  "target": {
    "planned_move_in_date": "2027-03-01",
    "desired_deposit": 90000000,
    "desired_monthly_rent": 500000,
    "desired_housing_type": "MONTHLY_RENT",
    "desired_region": "SEOUL"
  }
}
```

---

## 7. Policy

| 필드 | 타입 | 의미 |
|---|---|---|
| `policy_id` | INT | 정책 고유 ID |
| `title` | VARCHAR | 정책명 |
| `description` | TEXT | 정책 한 줄 설명 |
| `policy_category` | VARCHAR | 정책 카테고리 |
| `policy_region` | VARCHAR | 정책 적용 지역 |
| `policy_provider` | VARCHAR | 정책 제공기관 |
| `application_start` | DATE/null | 신청 시작일 |
| `application_end` | DATE/null | 신청 종료일 |
| `application_period_type` | VARCHAR | 신청기간 유형 |
| `support_amount` | INT/null | 숫자로 표현 가능한 대표 지원금액 |
| `support_amount_unit` | VARCHAR | 지원금 기준 단위 |
| `support_amount_text` | TEXT | 실제 지원 내용 상세 |
| `family_earnings` | TEXT | 사람이 읽는 가구 소득 조건 |
| `eligibility_text` | TEXT | 사람이 읽는 상세 자격조건 |
| `eligibility_rules` | JSON | Rule Engine 자동 판정용 구조 |
| `source_url` | TEXT | 공식 정책 출처 |
| `checked_at` | DATETIME | 데이터 마지막 확인 시점 |

### `support_amount`

```text
support_amount
→ 숫자로 표현 가능한 대표 지원금액

support_amount_unit
→ MONTH / YEAR / TOTAL / OTHER

support_amount_text
→ 실제 정책의 상세 지원 내용
```

`support_amount = 0`과 `support_amount = null`은 다른 의미다.

---

## 8. Policy eligibility_rules

모든 Demo Policy는 동일한 JSON key 구조를 사용한다.

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

### null / [] 규칙

```text
null
= 해당 정책에 해당 단일 조건/수치 제한이 없음

ratio.min = null
= 소득 비율 하한 없음

ratio.max = null
= 소득 비율 상한 없음

ratio는 항상 { min, max } 객체로 표현한다.
예: { "min": 0.48, "max": 1.5 }

[]
= 해당 배열 조건에 제한 없음

additional_conditions
= 실제 정책 조건은 존재하지만 현재 MVP Rule Engine에서 자동 판정하지 않는 조건
```

Rule Engine은 `additional_conditions`를 임의로 충족했다고 가정하지 않는다.

해당 조건 때문에 자동으로 최종 자격을 확정할 수 없는 경우 `NEED_MORE_INFO` 판정에 활용한다.

---

## 9. Demo Policy

MVP Demo Policy는 실제 정책 데이터 **policy_id 1~6**을 기준으로 한다.

```text
1 청년월세 지원사업
2 청년전세임대
3 제주 청년 희망충전 월세 지원
4 청년전용 버팀목 전세자금대출
5 청년 매입임대
6 서울시 청년월세지원
```

기존 Demo용 `policy_id = 101`, `102`는 사용하지 않는다.

정책 데이터의 최종 원본은:

```text
backend/app/policy/data/policies.json
```

을 따른다.

---

## 10. Diagnosis

| 필드 | 타입 | 의미 |
|---|---|---|
| `diagnosis_id` | INT | 진단 결과 ID |
| `user_id` | INT | 사용자 ID |
| `target_id` | INT | 진단 기준 Target ID |
| `readiness_score` | INT | 전체 독립 준비도, 100점 만점 |
| `fund_score` | FLOAT | 초기자금 준비도, 최대 70점 |
| `saving_score` | FLOAT | 저축계획 준비도, 최대 30점 |
| `required_initial_fund` | INT | 목표 주거조건에 필요한 초기자금 |
| `initial_fund_gap` | INT | 현재 보유자금 대비 부족 초기자금 |
| `required_monthly_saving` | INT | 독립 예정일까지 필요한 월 저축액 |
| `estimated_months` | INT/null | 현재 저축속도 기준 예상 준비기간 |
| `calculated_at` | DATETIME | 계산 시점 |

다음 필드는 최종 MVP에서 제거한다.

```text
current_emergency_fund
target_emergency_fund
emergency_fund_gap
emergency_score
```

계산 계약은 `diagnosis-rules.md`를 따른다.

---

## 11. PolicyMatch

| 필드 | 타입 | 의미 |
|---|---|---|
| `match_id` | INT | 정책 매칭 결과 ID |
| `user_id` | INT | 사용자 ID |
| `diagnosis_id` | INT | 판정 기준 Diagnosis ID |
| `policy_id` | INT | 정책 ID |
| `eligibility_status` | VARCHAR | 자격 상태 |
| `matched_conditions` | JSON | 충족 조건 |
| `failed_conditions` | JSON | 미충족 조건 |
| `missing_conditions` | JSON | 추가 확인이 필요한 조건 |
| `rank` | INT/null | 추천 우선순위 |
| `matched_at` | DATETIME | 판정 시점 |

Frontend 최종 Response와 AI Context에는 필요한 Policy 상세 정보를 함께 제공할 수 있다.

AI는 PolicyMatch를 다시 판정하지 않는다.

---

## 12. ActionPlan

| 필드 | 타입 | 의미 |
|---|---|---|
| `action_id` | INT | Action ID, Backend 생성 |
| `plan_id` | INT | Action Plan 그룹 ID, Backend 생성 |
| `user_id` | INT | 사용자 ID |
| `diagnosis_id` | INT | 기반 Diagnosis ID |
| `priority` | INT | 우선순위 |
| `action_type` | VARCHAR | 행동 유형 |
| `timing` | VARCHAR | 실행 단계 |
| `title` | VARCHAR | 행동 제목 |
| `description` | TEXT | 구체적인 행동 |
| `reason` | TEXT | 추천 이유 |
| `status` | VARCHAR | 진행 상태 |
| `policy_id` | INT/null | 관련 정책 ID |
| `due_date` | DATE/null | 권장 실행기한 |
| `created_at` | DATETIME | 생성 시점 |

AI가 생성:

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

Backend가 생성/부여:

```text
plan_id
action_id
user_id
diagnosis_id
status = TODO
created_at
```

`application_period_type != FIXED`이거나 실제 종료일을 확인할 수 없는 정책에 대해 AI가 임의의 신청 마감일을 생성해서는 안 된다.

---

## 13. PK / FK

| 테이블 | PK | FK |
|---|---|---|
| User | `user_id` | - |
| Target | `target_id` | `user_id → User.user_id` |
| Policy | `policy_id` | - |
| Diagnosis | `diagnosis_id` | `user_id`, `target_id` |
| PolicyMatch | `match_id` | `user_id`, `diagnosis_id`, `policy_id` |
| ActionPlan | `action_id` | `user_id`, `diagnosis_id`, `policy_id` |

`plan_id`는 MVP에서 여러 Action을 묶는 그룹 ID이며 별도 Plan FK 테이블을 필수로 두지 않는다.

---

## 14. 책임 분리

```text
User + Target
→ Frontend 입력 / Backend 검증·저장

Diagnosis
→ Backend 계산

Policy
→ Data 담당

PolicyMatch
→ Rule Engine

ActionPlan
→ AI 생성
→ Backend 검증 및 ID/status 부여
```

AI는 Diagnosis 계산 또는 Policy 자격 판정을 다시 수행하지 않는다.
