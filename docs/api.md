# Backend API Contract

> Version: v1

## 1. Base URL

```text
Local      http://localhost:8000
Production TBD
Swagger    {Base URL}/docs
```

공통 `Content-Type`:

```text
application/json
```

## 2. Endpoint Summary

| Method | Endpoint | 기능 | Request | Response |
|---|---|---|---|---|
| GET | `/api/v1/health` | 서버 상태 확인 | 없음 | Health |
| POST | `/api/v1/plan` | 최초 독립 플랜 생성 | Plan Request | Final Plan Response |
| POST | `/api/v1/replan` | 조건 변경 후 Re-planning | Replan Request | Before/After Response |

## 3. GET `/api/v1/health`

Response `200`:

```json
{
  "status": "OK"
}
```

## 4. POST `/api/v1/plan`

### 목적

```text
User + Target
→ Diagnosis
→ Policy Rule Matching
→ AI Action Plan
→ Backend validation/save
→ Final Response
```

### MVP Request Scope

현재 원본 v1 API 노션에는 전체 User/Target 필드가 들어 있으나, 2026-08-14 MVP 합의에 따라 **초기 UI에서 사용자에게 받는 필드는 P0로 축소**한다.

P0:

```text
age
employment_status
region
monthly_income
current_savings
current_emergency_fund
monthly_saving
target_date
deposit_budget
monthly_rent_budget
housing_type
```

서울 한정 MVP에서는:

```text
target_region = "서울"
```

을 Frontend Request에 포함하지 않고 Backend가 내부 기본값으로 부여한다. `target_region`은 저장·Policy 판정·Response에는 포함하지만, 이번 MVP의 Frontend 입력 필드는 아니다.

Backend Request schema는 이번 MVP에서 P0 11개 입력을 기준으로 한다. P1/P2 필드는 Request와 Mock에 포함하지 않으며, Frontend가 사용하지 않는 임의 숫자를 전송해 validation을 우회하지 않는다.

### Plan Request — 목표 형태

```json
{
  "user": {
    "age": 24,
    "region": "경기도",
    "employment_status": "EMPLOYED",
    "monthly_income": 2500000,
    "monthly_saving": 500000,
    "current_savings": 5000000,
    "current_emergency_fund": 1000000
  },
  "target": {
    "target_date": "2027-01-12",
    "monthly_rent_budget": 500000,
    "deposit_budget": 5000000,
    "housing_type": "MONTHLY_RENT"
  }
}
```

> 위 JSON이 이번 MVP의 **P0 Request 기준 형태**다. `target_region`은 Backend가 `"서울"`로 보완한다.

### Backend 처리 순서

1. User 검증
2. Target 검증
3. User/Target 저장
4. Diagnosis 계산
5. Policy Rule Engine
6. PolicyMatch 생성
7. AI input 생성
8. AI ActionPlan 생성
9. AI output 검증
10. `plan_id`, `action_id`, `status=TODO`, timestamp 부여
11. 저장
12. Final Response 반환

### Success Response

`200 OK`

`/mock/final-response.json`을 구조 기준으로 한다.

최상위:

```json
{
  "user_id": 1,
  "target_id": 1,
  "diagnosis_id": 1,
  "plan_id": 1,
  "target": {},
  "diagnosis": {},
  "matched_policies": [],
  "action_plan": {
    "summary": "...",
    "actions": []
  }
}
```

## 5. POST `/api/v1/replan`

### MVP 대표 시나리오

```text
deposit_budget: 5,000,000 → 4,000,000
```

### Request

```json
{
  "user_id": 1,
  "target_id": 1,
  "previous_diagnosis_id": 1,
  "previous_plan_id": 1,
  "changes": {
    "deposit_budget": 4000000
  }
}
```

### 처리 순서

```text
기존 User/Target 조회
→ changes 적용
→ 변경 저장
→ Diagnosis 재계산
→ Policy 재판정
→ 이전/현재 결과를 AI Re-planning 입력으로 구성
→ 새 ActionPlan 생성
→ 새 plan_id 생성
→ 저장
→ before/after 반환
```

### Success Response

`200 OK`

`/mock/replan-final-response.json`을 기준으로 한다.

```json
{
  "user_id": 1,
  "target_id": 1,
  "previous": {
    "diagnosis_id": 1,
    "plan_id": 1,
    "target": {},
    "diagnosis": {}
  },
  "current": {
    "diagnosis_id": 2,
    "plan_id": 2,
    "target": {},
    "diagnosis": {},
    "matched_policies": [],
    "action_plan": {}
  },
  "changed_fields": {
    "deposit_budget": {
      "before": 5000000,
      "after": 4000000
    }
  }
}
```

MVP에서 반드시 보장하는 변경 필드는 `deposit_budget`이다. 다른 P0 필드까지 `changes`로 허용할지는 구현 후 확대 가능하며, Backend whitelist/validation을 먼저 합의한다.

## 6. Backend → AI

AI에 전달하는 데이터:

```text
IDs
+ User
+ Target
+ Diagnosis
+ Policy Context projection
```

Policy Context에는 `policy_id`, `title`, `eligibility_status`, 조건 결과, 정책 상세 설명과 지원금 정보를 포함한다. 내부 매칭 이력인 `match_id`, `user_id`, `diagnosis_id`, `matched_at`은 Backend 내부 값으로 유지하고 AI input에는 전달하지 않는다.

AI는 다음을 하지 않는다.

- Diagnosis 재계산
- 정책 자격 재판정
- 지원금 임의 계산
- 입력/정책 데이터에 없는 사실 생성

## 7. AI → Backend

AI 출력은 Structured JSON:

```json
{
  "summary": "...",
  "actions": [
    {
      "priority": 1,
      "action_type": "SAVING",
      "timing": "NOW",
      "title": "월 저축계획 유지",
      "description": "현재 월 500000원의 저축을 유지합니다.",
      "reason": "...",
      "policy_id": null,
      "due_date": null
    }
  ]
}
```

Backend가 추가하는 값:

```text
plan_id
action_id
status = TODO
created_at
```

최종 Response의 각 Action에는 위 Backend 생성값과 `plan_id`, `user_id`, `diagnosis_id`가 포함된다.

## 8. Loading

`/plan`, `/replan`은 동기 API다.

```text
request start
→ Frontend isPending = true
→ Loading UI
→ Response
→ isPending = false
```

`loading.json`은 API Response가 아니다.

## 9. Error Contract

공통:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자에게 표시할 메시지"
  }
}
```

상세 validation:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "입력값을 확인해주세요.",
    "details": [
      {
        "field": "current_emergency_fund",
        "reason": "current_savings보다 클 수 없습니다."
      }
    ]
  }
}
```

| HTTP | Code | 의미 |
|---|---|---|
| 422 | `INVALID_INPUT` | 입력 validation 실패 |
| 404 | `PLAN_NOT_FOUND` | 이전 플랜을 찾을 수 없음 |
| 500 | `PLAN_GENERATION_FAILED` | 전체 플랜 생성 실패 |
| 500 | `POLICY_MATCH_FAILED` | Policy Rule Matching 실패 |
| 500 | `AI_PLANNER_FAILED` | AI Action Plan 생성 실패 |

## 10. Frontend 연동 원칙

개별 개발:

```text
Frontend → Mock 기반 화면 개발
Backend  → Mock input 기반 API 개발
```

E2E:

```text
Frontend
→ POST /api/v1/plan
→ Backend
→ final response
→ Frontend
```

Frontend에서 API endpoint나 response shape를 임의로 가정하지 않는다. 변경 필요 시 `api.md`, `data-contract.md`, Mock을 동시에 수정한다.
