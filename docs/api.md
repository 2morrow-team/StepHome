# Backend API Contract

> Version: v1  
> StepHome MVP Frontend ↔ Backend API Contract

## 1. Base URL

```text
Local      http://localhost:8000
Production TBD
Swagger    {Base URL}/docs
```

공통 Content-Type:

```text
application/json
```

---

## 2. 공통 데이터 규칙

| 항목 | 규칙 | 예시 |
|---|---|---|
| 금액 | KRW 원 단위 `INT` | `90000000` |
| 날짜 | `YYYY-MM-DD` | `"2027-03-01"` |
| 시간 | ISO 8601 + KST | `"2026-08-16T15:00:00+09:00"` |
| Enum | `UPPER_SNAKE_CASE` | `MONTHLY_RENT` |
| nullable | 값이 없으면 `null` | `"policy_id": null` |

---

## 3. Endpoint Summary

| Method | Endpoint | 기능 | Request | Response |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | 서버 상태 확인 | 없음 | Health |
| `POST` | `/api/v1/plan` | 최초 독립 플랜 생성 | Plan Request | Final Plan Response |
| `POST` | `/api/v1/replan` | 조건 변경 후 Re-planning | Replan Request | Before/After Response |

---

## 4. GET `/api/v1/health`

### Request

```text
GET /api/v1/health
```

Request Body 없음.

### Response

```text
200 OK
```

```json
{
  "status": "OK"
}
```

---

# 5. POST `/api/v1/plan`

## 목적

```text
User + Target
→ Diagnosis
→ Policy Rule Matching
→ AI Action Plan
→ Backend Validation / Save
→ Final Response
```

## Request

```text
POST /api/v1/plan
Content-Type: application/json
```

## Request Body

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

P0 입력은 총 15개다.

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

## 6. 주요 Validation

```text
age
→ 0 이상의 정수
→ 정책별 실제 연령 자격은 Rule Engine에서 판정

금액
→ 0 이상의 정수

monthly_savings
→ 0 이상의 정수

youth_household_size
→ 1 이상의 정수

planned_move_in_date
→ 요청 시점 기준 미래 날짜

employment_status
→ JOB_SEEKER / EMPLOYED / STUDENT / OTHER

housing_status
→ NO_HOME / HAS_HOME

marital_status
→ UNMARRIED / MARRIED

desired_housing_type
→ MONTHLY_RENT / JEONSE

current_region / desired_region
→ 확정 Region Enum
```

정책 자체의 연령 제한 등을 API Validation으로 제한하지 않는다.

예를 들어 사용자가 40세라고 해서 Request 자체가 잘못된 것은 아니다. 정책 자격 여부는 Rule Engine이 판정한다.

---

## 7. Backend 처리 순서

```text
1. User Request 검증
2. Target Request 검증
3. User / Target 저장
4. Diagnosis 계산
5. Policy 데이터 조회
6. Rule Engine 실행
7. PolicyMatch 생성
8. AI Input 구성
9. AI ActionPlan 생성
10. AI Output 검증
11. plan_id / action_id 생성
12. status = TODO
13. timestamp 생성
14. ActionPlan 저장
15. Final Response 반환
```

---

## 8. Plan Success Response

```text
200 OK
```

구조:

```json
{
  "user_id": 1,
  "target_id": 1,
  "diagnosis_id": 1,
  "plan_id": 1,

  "target": {
    "planned_move_in_date": "2027-03-01",
    "desired_deposit": 90000000,
    "desired_monthly_rent": 500000,
    "desired_housing_type": "MONTHLY_RENT",
    "desired_region": "SEOUL"
  },

  "diagnosis": {
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
  },

  "matched_policies": [],

  "action_plan": {
    "summary": "현재 독립 준비 상태를 기반으로 생성된 Action Plan입니다.",
    "actions": []
  }
}
```

`readiness_score`, `fund_score`, `saving_score`, `required_monthly_saving` 등 실행 시점에 의존하는 Diagnosis 값은 실제 Calculator 결과를 사용한다.

Response 전체 구조는 `/mock/final-response.json`과 동일하게 유지한다.

---

# 9. Backend → AI

AI Input은 다음 Context를 포함한다.

```text
IDs
+ User
+ Target
+ Diagnosis
+ Policy Context
```

AI는 Diagnosis 계산이나 Policy 자격 판정을 다시 하지 않는다.

### Policy Context 예시

```json
{
  "policy_id": 6,
  "title": "서울시 청년월세지원",
  "eligibility_status": "CONDITIONAL",

  "matched_conditions": [
    "AGE",
    "CURRENT_REGION",
    "TARGET_REGION",
    "HOUSING_STATUS",
    "HOUSING_TYPE",
    "MONTHLY_RENT_LIMIT"
  ],

  "failed_conditions": [
    "DEPOSIT_LIMIT"
  ],

  "missing_conditions": [],

  "rank": 1,

  "support_amount": 200000,
  "support_amount_unit": "MONTH",
  "support_amount_text": "월 최대 20만원의 임차료를 최대 12개월 지원하며 생애 1회 지원",

  "eligibility_text": "신청일 기준 서울시에 거주하는 19~39세 무주택 청년 등",
  "description": "서울에 거주하는 청년의 주거비 부담 완화를 위한 사업",

  "application_start": "2026-05-06",
  "application_end": "2026-05-19",
  "application_period_type": "FIXED",

  "source_url": "...",
  "checked_at": "2026-08-16T00:00:00+09:00"
}
```

AI Input에는 내부 매칭 식별자로만 사용되는 값은 필요에 따라 제외할 수 있다.

```text
match_id
matched_at
```

AI는 다음을 하지 않는다.

- Diagnosis 재계산
- 정책 자격 재판정
- 정책 지원금 임의 계산
- 정책 데이터에 없는 조건 생성
- 존재하지 않는 신청 마감일 생성

---

# 10. AI → Backend

AI Structured Output:

```json
{
  "summary": "현재 독립 준비 상태와 이용 가능한 정책을 기반으로 다음 행동을 추천합니다.",
  "actions": [
    {
      "priority": 1,
      "action_type": "HOUSING",
      "timing": "SEARCH_HOUSE",
      "title": "보증금 조건 조정 검토",
      "description": "서울시 청년월세지원의 보증금 기준을 고려해 희망 보증금을 조정합니다.",
      "reason": "현재 희망 보증금이 정책 상한을 초과하고 있습니다.",
      "policy_id": 6,
      "due_date": null
    }
  ]
}
```

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

Backend가 생성:

```text
plan_id
action_id
user_id
diagnosis_id
status = TODO
created_at
```

---

# 11. POST `/api/v1/replan`

사용자가 P0 입력값을 변경하면 현재 조건을 기준으로 전체 결과를 다시 생성한다.

```text
조건 변경
→ Diagnosis 재계산
→ Policy 재판정
→ AI Re-planning
→ 새로운 ActionPlan
```

---

## 12. Re-planning 변경 가능 필드

### User

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

### Target

```text
planned_move_in_date
desired_deposit
desired_monthly_rent
desired_housing_type
desired_region
```

대표 Demo에서는 `desired_deposit`만 변경한다.

---

## 13. Replan Request

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

## 14. Re-planning Demo

### Before

```text
desired_deposit = 90,000,000
```

Policy 6:

```text
deposit_max = 80,000,000
```

따라서:

```text
90,000,000 > 80,000,000
→ CONDITIONAL
```

### After

```text
desired_deposit = 70,000,000
```

따라서:

```text
70,000,000 <= 80,000,000
→ AVAILABLE
```

최종 Demo 핵심 변화:

```text
희망 보증금
90,000,000 → 70,000,000

Policy 6 서울시 청년월세지원
CONDITIONAL → AVAILABLE

Diagnosis
재계산

ActionPlan
재생성
```

---

## 15. Re-planning Backend 처리

```text
1. 기존 User / Target 조회

2. changes Validation

3. 허용된 P0 필드에 changes 적용

4. 변경된 User / Target 저장

5. Diagnosis 재계산

6. Policy Rule Engine 재실행

7. 현재 PolicyMatch 생성

8. previous/current Context 구성

9. AI Re-planning 실행

10. 새로운 diagnosis_id 생성

11. 새로운 plan_id 생성

12. 새로운 action_id 생성

13. status = TODO

14. created_at 생성

15. 새로운 ActionPlan 저장

16. Before / After Response 반환
```

Backend가 별도의 `policy_status_changes` 객체를 반드시 생성할 필요는 없다.

이전/현재 PolicyMatch를 AI에 전달하여 Re-planning Context로 활용할 수 있다.

---

## 16. Replan Success Response

```json
{
  "user_id": 1,
  "target_id": 1,

  "previous": {
    "diagnosis_id": 1,
    "plan_id": 1,
    "target": {
      "desired_deposit": 90000000
    },
    "diagnosis": {},
    "matched_policies": [],
    "action_plan": {}
  },

  "current": {
    "diagnosis_id": 2,
    "plan_id": 2,
    "target": {
      "desired_deposit": 70000000
    },
    "diagnosis": {},
    "matched_policies": [],
    "action_plan": {}
  },

  "changed_fields": {
    "desired_deposit": {
      "before": 90000000,
      "after": 70000000
    }
  }
}
```

전체 Snapshot 구조는 `/mock/replan-final-response.json`과 동일하게 유지한다.

---

# 17. Loading

`/plan`, `/replan`은 MVP에서 동기식 API다.

```text
Frontend Request
→ isPending = true
→ Loading UI
→ Backend Response
→ isPending = false
```

`loading.json`은 Frontend UI Mock이며 Backend 중간 Response가 아니다.

---

# 18. Error Contract

공통:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자에게 표시할 메시지"
  }
}
```

Validation 상세:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "입력값을 확인해주세요.",
    "details": [
      {
        "field": "target.desired_deposit",
        "reason": "희망 보증금은 0원 이상이어야 합니다."
      }
    ]
  }
}
```

Error의 `field`는 Request 구조를 그대로 사용한다.

예:

```text
user.age
user.monthly_savings
user.youth_household_size
target.planned_move_in_date
target.desired_deposit
changes.desired_deposit
```

FastAPI Validation 내부 경로의 `body` 등은 Frontend Response에서 제거한다.

---

## 19. Error Code

| HTTP | Code | 의미 |
|---|---|---|
| `422` | `INVALID_INPUT` | 입력 Validation 실패 |
| `404` | `PLAN_NOT_FOUND` | 이전 플랜을 찾을 수 없음 |
| `500` | `PLAN_GENERATION_FAILED` | 전체 플랜 생성 실패 |
| `500` | `POLICY_MATCH_FAILED` | Policy Rule Matching 실패 |
| `500` | `AI_PLANNER_FAILED` | AI Action Plan 생성 실패 |

### AI 실패

```json
{
  "error": {
    "code": "AI_PLANNER_FAILED",
    "message": "Action Plan 생성에 실패했습니다. 다시 시도해주세요."
  }
}
```

### Policy Matching 실패

```json
{
  "error": {
    "code": "POLICY_MATCH_FAILED",
    "message": "정책 정보를 분석하는 중 오류가 발생했습니다."
  }
}
```

---

# 20. API 전체 요약

| Method | Endpoint | 기능 | Request | Response |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | 서버 상태 확인 | 없음 | Health |
| `POST` | `/api/v1/plan` | 최초 독립 플랜 생성 | `request-user-target.json` | `final-response.json` |
| `POST` | `/api/v1/replan` | 조건 변경 후 Re-planning | `replan-request.json` | `replan-final-response.json` |

---

# 21. Frontend 연동

개별 개발:

```text
Frontend
Mock → UI

Backend
Mock Input → API

Policy
policies.json → Rule Engine

AI
ai-input.json → ActionPlan
```

E2E:

```text
Frontend
   ↓
POST /api/v1/plan
   ↓
Backend Router
   ↓
Plan Service
   ├── Diagnosis
   ├── Policy Rule Engine
   └── AI Planner
   ↓
Final Response
   ↓
Frontend
```

개발 환경:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Production Base URL은 배포 후 Frontend에 공유한다.
