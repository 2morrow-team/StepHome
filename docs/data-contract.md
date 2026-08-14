# Data Contract

## 1. 공통 형식

| 항목 | 규칙 | 예시 |
|---|---|---|
| 금액 | KRW 원 단위 `INT` | `2500000` |
| 날짜 | `YYYY-MM-DD` | `"2027-01-12"` |
| API datetime | ISO 8601 + KST | `"2026-08-12T15:00:00+09:00"` |
| DB 날짜 | `DATE` | `2027-01-12` |
| DB datetime | `DATETIME` | `2026-08-12 15:00:00` |
| 서버 기준 시간대 | `Asia/Seoul (UTC+9)` | - |
| Enum | `UPPER_SNAKE_CASE` | `MONTHLY_RENT` |
| ID | `INT`, Backend/DB 생성 | `user_id: 1` |
| 없는 선택값 | `null`, 빈 문자열 금지 | `"policy_id": null` |

## 2. 핵심 Enum

### `housing_type`

```text
MONTHLY_RENT
JEONSE
```

원룸/오피스텔/신축/역세권은 `housing_type`이 아니다. 필요하면 `housing_preference`에 둔다.

### `eligibility_status`

```text
AVAILABLE
CONDITIONAL
NEED_MORE_INFO
NOT_ELIGIBLE
```

| 값 | 의미 |
|---|---|
| `AVAILABLE` | 현재 조건 충족 |
| `CONDITIONAL` | 현재 미충족이지만 조정 가능한 조건 변경 시 가능 |
| `NEED_MORE_INFO` | 판정에 필요한 사용자 정보 부족 |
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

### `employment_status`

이번 MVP의 Backend Enum은 다음과 같이 확정한다.

| UI label | Backend Enum |
|---|---|
| 취업 준비 중 | `JOB_SEEKER` |
| 재직 중 | `EMPLOYED` |
| 대학생 | `STUDENT` |
| 기타 | `OTHER` |

> 위 label ↔ Enum 매핑은 기존 Notion에 없던 내용을 이번 MVP Contract에 추가한 것이다.

## 3. User

원본 데이터 모델 전체 필드와 MVP 입력 우선순위는 구분한다. P0/P1/P2는 `mvp-scope.md`를 따른다.

| 필드 | 타입 | 의미 | v1 예시 |
|---|---|---|---|
| `user_id` | INT | 사용자 ID, Backend 생성 | `1` |
| `age` | INT | **만 나이** | `24` |
| `region` | VARCHAR | 현재 거주 지역 | `경기도` |
| `employment_status` | VARCHAR | 취업 상태 | `EMPLOYED` |
| `monthly_income` | INT | 본인 월 소득 | `2500000` |
| `current_housing_cost` | INT | 현재 월 주거비 | `0` |
| `current_housing_type` | VARCHAR | 현재 주거 형태 | `FAMILY_HOME` |
| `monthly_living_expense` | INT | 월 생활비 | `500000` |
| `monthly_fixed_expense` | INT | 월 고정지출 | `800000` |
| `monthly_saving` | INT | 월 저축 가능액 | `500000` |
| `current_savings` | INT | 현재 **총 보유자금** | `5000000` |
| `current_emergency_fund` | INT | 총 보유자금 중 비상자금 | `1000000` |
| `debt` | INT | 현재 부채 | `0` |

### 자금 관계

`current_emergency_fund`는 `current_savings`에 포함된다.

```text
usable_initial_fund
= current_savings - current_emergency_fund
```

필수 validation:

```text
0 <= current_emergency_fund <= current_savings
```

## 4. Target

| 필드 | 타입 | 의미 | v1 예시 |
|---|---|---|---|
| `target_id` | INT | 독립 목표 ID, Backend 생성 | `1` |
| `user_id` | INT | User FK | `1` |
| `target_date` | DATE | 희망 독립 시점 | `2027-01-12` |
| `monthly_rent_budget` | INT | 희망 월 주거비/월세 | `500000` |
| `deposit_budget` | INT | 희망 보증금 | `5000000` |
| `housing_type` | VARCHAR | 희망 계약 형태 | `MONTHLY_RENT` |
| `target_region` | VARCHAR | 독립 희망 지역 | `서울` |
| `housing_preference` | TEXT | 기타 선호 조건 | `원룸, 역세권, 풀옵션` |

MVP가 서울 한정으로 확정된 동안 `target_region`은 UI 입력에서 제외하고 Backend가 내부 기본값 `"서울"`로 처리한다. 이 경우에도 Backend/Rule Engine 내부 데이터와 Response에는 필드를 유지한다.

## 5. Policy

| 필드 | 타입 | 의미 |
|---|---|---|
| `policy_id` | INT | 정책 ID |
| `title` | VARCHAR | 정책명 |
| `application_start` | DATE | 신청 시작일 |
| `application_end` | DATE | 신청 종료일 |
| `support_amount` | INT/null | 계산 가능한 대표 지원금액 |
| `region` | VARCHAR | 지원 지역 |
| `provider` | VARCHAR | 제공기관 |
| `category` | VARCHAR | 정책 카테고리 |
| `eligibility_rules` | JSON | Rule Engine 판정용 구조화 조건 |
| `eligibility_text` | TEXT | 사람이 읽는 상세 자격조건 / AI 근거 |
| `support_amount_text` | TEXT | 금액·기간·방식 설명 |
| `description` | TEXT | 정책 목적/내용 |
| `source_url` | TEXT | 공식 정책 출처 |
| `checked_at` | DATETIME | 데이터 마지막 확인 시점 |

`eligibility_rules`와 `eligibility_text`의 역할을 섞지 않는다.

```text
eligibility_rules → Backend Rule Engine
eligibility_text  → 상세 설명 / AI 근거
```

예시:

```json
{
  "age": { "min": 19, "max": 34 },
  "region": ["서울"],
  "income": { "max": 3000000 },
  "housing_type": ["MONTHLY_RENT"],
  "deposit": { "max": 50000000 }
}
```

`support_amount = 0`과 `support_amount = null`은 다르다.

## 6. Diagnosis

| 필드 | 타입 | 의미 |
|---|---|---|
| `diagnosis_id` | INT | 진단 결과 ID |
| `user_id` | INT | 사용자 ID |
| `target_id` | INT | 진단 기준 독립 목표 ID |
| `readiness_score` | INT | 전체 준비도 |
| `fund_score` | FLOAT | 초기자금 준비도(50점) |
| `saving_score` | FLOAT | 저축계획 달성도(30점) |
| `emergency_score` | FLOAT | 비상자금 준비도(20점) |
| `required_initial_fund` | INT | 필요한 독립 초기자금, 비상자금 제외 |
| `initial_fund_gap` | INT | 부족한 초기자금 |
| `target_emergency_fund` | INT | 목표 비상자금 |
| `emergency_fund_gap` | INT | 부족한 비상자금 |
| `required_monthly_saving` | INT | 목표일까지 필요한 월 저축액 |
| `estimated_months` | INT | 현재 저축속도 기준 예상 준비기간 |
| `calculated_at` | DATETIME | 계산 시점 |

계산 계약은 `diagnosis-rules.md`를 따른다.

## 7. PolicyMatch

| 필드 | 타입 | 의미 |
|---|---|---|
| `match_id` | INT | 정책 매칭 결과 ID |
| `user_id` | INT | 사용자 ID |
| `diagnosis_id` | INT | 판정 기준 진단 ID |
| `policy_id` | INT | 정책 ID |
| `eligibility_status` | VARCHAR | 자격 상태 |
| `matched_conditions` | JSON | 충족 조건 |
| `failed_conditions` | JSON | 미충족 조건 |
| `missing_conditions` | JSON | 추가 확인이 필요한 조건 |
| `rank` | INT/null | 추천 우선순위 |
| `matched_at` | DATETIME | 판정 시점 |

Frontend 최종 Response에서는 Policy 상세 표시를 위해 Policy의 일부 필드가 함께 flatten되어 전달된다.

최종 Response는 PolicyMatch 식별자와 Policy 상세 필드를 함께 제공한다. AI input은 이 구조에서 내부 매칭 식별자와 시각 필드를 제외한 Policy Context projection을 사용한다.

## 8. ActionPlan

| 필드 | 타입 | 의미 |
|---|---|---|
| `action_id` | INT | 개별 Action ID, Backend 생성 |
| `plan_id` | INT | 여러 Action을 묶는 계획 ID, Backend 생성 |
| `user_id` | INT | 사용자 ID |
| `diagnosis_id` | INT | 기반 진단 ID |
| `priority` | INT | 우선순위 |
| `action_type` | VARCHAR | 행동 유형 |
| `timing` | VARCHAR | 실행 단계 |
| `title` | VARCHAR | 행동 제목 |
| `description` | TEXT | 구체적 행동 |
| `reason` | TEXT | 추천 이유 |
| `status` | VARCHAR | 진행 상태 |
| `policy_id` | INT/null | 관련 정책 ID |
| `due_date` | DATE/null | 권장 실행기한 |
| `created_at` | DATETIME | 생성 시점 |

AI 출력에는 `action_id`, `plan_id`, `status`, `created_at`이 없다. Backend가 검증 후 생성/부여한다.

최종 Response의 각 Action에는 Backend가 생성한 `action_id`, `plan_id`, `user_id`, `diagnosis_id`, `status`, `created_at`을 포함한다.

`plan_id`는 MVP에서 그룹 ID이며 별도 FK 테이블을 만들지 않는다.

## 9. PK / FK

| 테이블 | PK | FK |
|---|---|---|
| User | `user_id` | - |
| Target | `target_id` | `user_id → User.user_id` |
| Policy | `policy_id` | - |
| Diagnosis | `diagnosis_id` | `user_id`, `target_id` |
| PolicyMatch | `match_id` | `user_id`, `diagnosis_id`, `policy_id` |
| ActionPlan | `action_id` | `user_id`, `diagnosis_id`, `policy_id` |

## 10. 책임 분리

```text
User + Target   → Frontend 입력 / Backend 검증·저장
Diagnosis       → Backend 계산
Policy          → Data 담당
PolicyMatch     → Rule Engine
ActionPlan      → AI 생성 → Backend 검증·ID/status 부여
```
