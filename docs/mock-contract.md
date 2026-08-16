# Mock Contract

> `/mock`은 StepHome 팀 공통 Contract Sample이다.  
> Frontend / Backend / Policy / AI가 E2E 연결 전 동일한 데이터 구조로 병렬 개발하기 위해 사용한다.

## 1. 파일 목록

```text
mock/
├── request-user-target.json
├── diagnosis.json
├── policy-match.json
├── ai-input.json
├── action-plan.json
├── final-response.json
├── replan-request.json
├── replan-final-response.json
├── loading.json
├── error.json
└── errors/
    ├── ai-planner-failed.json
    ├── invalid-input.json
    ├── policy-match-failed.json
    └── plan-not-found.json
```

---

## 2. 흐름

```text
request-user-target.json
        ↓
diagnosis.json
        ↓
policy-match.json
        ↓
ai-input.json
        ↓
action-plan.json
        ↓
final-response.json

replan-request.json
        ↓
replan-final-response.json
```

---

## 3. 담당자별 사용

| Mock | 주요 사용자 | 목적 |
|---|---|---|
| `request-user-target.json` | Frontend / Backend | 최초 입력 |
| `diagnosis.json` | Backend | Diagnosis 테스트 |
| `policy-match.json` | Backend / Policy / AI | 정책 판정 테스트 |
| `ai-input.json` | Backend / AI | AI 입력 테스트 |
| `action-plan.json` | AI / Backend | AI Structured Output 테스트 |
| `final-response.json` | Backend / Frontend | 최초 결과 |
| `replan-request.json` | Frontend / Backend | 조건 변경 |
| `replan-final-response.json` | Backend / Frontend / AI | Re-planning 전후 비교 |
| `loading.json` | Frontend | Loading UI |
| `error.json` | Frontend / Backend | 오류 처리 |

---

## 4. P0 Request Freeze

Frontend가 보내는 P0 입력은 총 15개다.

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

## 5. Demo Persona Freeze

```text
age                            = 25
employment_status              = EMPLOYED
current_region                 = SEOUL
housing_status                 = NO_HOME
marital_status                 = UNMARRIED

personal_monthly_income        = 2,500,000
youth_household_monthly_income = 2,500,000
youth_household_size           = 1
total_assets                   = 30,000,000
monthly_savings                = 500,000

planned_move_in_date           = 2027-03-01
desired_region                 = SEOUL
desired_deposit                = 90,000,000
desired_monthly_rent           = 500,000
desired_housing_type           = MONTHLY_RENT
```

---

## 6. request-user-target.json

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

## 7. Diagnosis Mock 원칙

Diagnosis는 다음 구조를 따른다.

```json
{
  "diagnosis_id": 1,
  "user_id": 1,
  "target_id": 1,
  "readiness_score": 0,
  "fund_score": 0.0,
  "saving_score": 0.0,
  "required_initial_fund": 90000000,
  "initial_fund_gap": 60000000,
  "required_monthly_saving": 0,
  "estimated_months": 120,
  "calculated_at": "2026-08-16T15:00:00+09:00"
}
```

`readiness_score`, `fund_score`, `saving_score`, `required_monthly_saving`은 실제 `calculator.py`의 계산 결과로 채운다.

Contract에 계산 시점 의존 수치를 임의로 Freeze하지 않는다.

다음 기존 필드는 사용하지 않는다.

```text
emergency_score
target_emergency_fund
emergency_fund_gap
```

---

## 8. Policy Mock 기준

Policy Mock은 실제 Demo Policy `policy_id 1~6`을 사용한다.

```text
1 청년월세 지원사업
2 청년전세임대
3 제주 청년 희망충전 월세 지원
4 청년전용 버팀목 전세자금대출
5 청년 매입임대
6 서울시 청년월세지원
```

기존 `101`, `102` Demo ID는 사용하지 않는다.

정책 원본은:

```text
backend/app/policy/data/policies.json
```

을 기준으로 한다.

---

## 9. Re-planning Demo Freeze

대표 Demo:

```text
Before
desired_deposit = 90,000,000
Policy 6 = CONDITIONAL

After
desired_deposit = 70,000,000
Policy 6 = AVAILABLE
```

Policy 6의 보증금 상한:

```text
deposit_max = 80,000,000
```

따라서:

```text
90,000,000 > 80,000,000
→ CONDITIONAL

70,000,000 <= 80,000,000
→ AVAILABLE
```

---

## 10. replan-request.json

```json
{
  "user_id": 1,
  "target_id": 1,
  "previous_diagnosis_id": 1,
  "previous_plan_id": 1,
  "changes": {
    "desired_deposit": 70000000
  }
}
```

---

## 11. P0 Re-planning 원칙

Re-planning 구조는 특정 필드 전용으로 설계하지 않는다.

P0 입력 전체를 변경 가능한 구조로 설계한다.

```text
changes
+ current Diagnosis
+ current PolicyMatch
+ previous ActionPlan
→ Re-planning
```

대표 Demo에서만:

```text
desired_deposit
90,000,000 → 70,000,000
```

을 사용한다.

---

## 12. Loading Mock

```json
{
  "status": "PROCESSING",
  "message": "독립 준비 상태와 이용 가능한 정책을 분석하고 있습니다."
}
```

`loading.json`은 Backend의 중간 Response가 아니라 Frontend Loading UI 구현용 Mock이다.

---

## 13. Frontend Mock 사용

```text
Component
→ API layer
→ Mock adapter
```

실 API 연결:

```text
Component
→ API layer
→ Backend
```

Frontend Component에서 Mock JSON을 직접 import하는 구조는 피한다.

---

## 14. Mock 동기화 원칙

다음 Contract 중 하나가 변경되면 관련 Mock도 함께 변경한다.

```text
data-contract.md
api.md
diagnosis-rules.md
policies.json
```

특히 다음 값은 서로 불일치하지 않도록 한다.

```text
P0 field name
Enum
policy_id
eligibility_status
Diagnosis field
Re-planning changed field
```
