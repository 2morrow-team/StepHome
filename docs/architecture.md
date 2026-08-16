# Architecture Contract

> StepHome Backend의 최종 배포 단위는 FastAPI 하나이며, Diagnosis / Policy / AI를 내부 모듈로 포함한다.

## 1. Monorepo

```text
StepHome/
│
├── frontend/                     # Frontend
│
├── backend/                      # 최종 FastAPI 배포 단위
│   ├── app/
│   │   ├── main.py
│   │
│   │   ├── routers/
│   │   │   ├── plan.py
│   │   │   └── replan.py
│   │
│   │   ├── services/
│   │   │   └── plan_service.py   # Backend orchestration
│   │
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │
│   │   ├── models/
│   │   │   └── models.py
│   │
│   │   ├── diagnosis/
│   │   │   └── calculator.py
│   │
│   │   ├── policy/
│   │   │   ├── data/
│   │   │   │   └── policies.json
│   │   │   ├── rules/
│   │   │   └── rule_engine.py
│   │
│   │   ├── ai/
│   │   │   ├── planner.py
│   │   │   ├── validator.py
│   │   │   └── prompts.py
│   │
│   │   └── db/
│   │       └── database.py
│   │
│   └── requirements.txt
│
├── mock/
│
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── data-contract.md
│   ├── diagnosis-rules.md
│   ├── mock-contract.md
│   ├── mvp-scope.md
│   ├── open-decisions.md
│   └── user-flow.md
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. 호출 방향

### 허용

```text
Frontend
   ↓ HTTP
Router
   ↓
Service
   ├── Diagnosis
   ├── Policy / Rule Engine
   ├── AI
   └── DB
```

### 금지

```text
Frontend → AI 직접 호출
Frontend → Rule Engine 직접 호출

Diagnosis → Policy 직접 호출
Policy → AI 직접 호출
AI → Diagnosis 직접 호출
```

모듈 간 전체 연결은 `plan_service.py`가 담당한다.

---

## 3. Router 책임

### `routers/plan.py`

```text
POST /api/v1/plan
→ Request 수신
→ Schema Validation
→ plan_service 호출
→ Response 반환
```

### `routers/replan.py`

```text
POST /api/v1/replan
→ Replan Request 수신
→ Schema Validation
→ plan_service 호출
→ Response 반환
```

Router에 Diagnosis / Rule Engine / AI의 비즈니스 로직을 직접 작성하지 않는다.

---

## 4. `plan_service.py` 책임

### 최초 Plan

```text
validate User / Target
→ save User / Target
→ calculate Diagnosis
→ match Policies
→ create PolicyMatch
→ build AI input
→ generate ActionPlan
→ validate AI output
→ create IDs/status
→ save
→ build Final Response
```

### Re-planning

```text
load previous state
→ validate changes
→ apply changes
→ save updated User / Target
→ recalculate Diagnosis
→ rerun Policy Rule Engine
→ create current PolicyMatch
→ build Re-planning AI input
→ generate new ActionPlan
→ validate AI output
→ create new IDs/status
→ save
→ return Before / After
```

---

## 5. Diagnosis 책임

```text
backend/app/diagnosis/calculator.py
```

담당:

```text
required_initial_fund
initial_fund_gap
required_monthly_saving
estimated_months
fund_score
saving_score
readiness_score
```

담당하지 않음:

```text
Policy 자격 판정
AI Action 생성
```

비상자금 관련 계산은 최종 MVP에서 제거한다.

---

## 6. Policy / Rule Engine 책임

정책 원본:

```text
backend/app/policy/data/policies.json
```

Rule Engine:

```text
backend/app/policy/rule_engine.py
```

흐름:

```text
User + Target
+ Policy.eligibility_rules
→ Rule Engine
→ PolicyMatch
```

Rule Engine은 실제 Demo Policy 1~6을 대상으로 한다.

---

## 7. AI 책임

```text
Diagnosis
+ PolicyMatch
+ User / Target Context
→ AI
→ ActionPlan
```

AI는 다음을 하지 않는다.

```text
Diagnosis 재계산
Policy 자격 재판정
Policy 데이터에 없는 지원금 생성
Policy 신청기간 임의 생성
```

---

## 8. Contract 책임

```text
docs/data-contract.md
→ 데이터 구조 / Enum

docs/api.md
→ HTTP API

docs/diagnosis-rules.md
→ Diagnosis 계산

docs/mock-contract.md
→ Mock 사용 기준

docs/mvp-scope.md
→ MVP 범위

docs/user-flow.md
→ 사용자 흐름

docs/open-decisions.md
→ 아직 확정되지 않은 사항
```

결정이 완료된 내용은 `open-decisions.md`에서 제거하고 해당 Contract 문서에 반영한다.

---

## 9. Contract 변경 원칙

다음 중 하나를 변경할 경우 관련 문서를 함께 확인한다.

```text
P0 field
Enum
API Request/Response
Diagnosis
Policy JSON
PolicyMatch
AI Input/Output
Mock
```

E2E 연결 전에 Mock과 실제 Backend Contract가 동일한지 확인한다.

---

## 10. 환경 변수

`.env`는 Git에 commit하지 않는다.

`.env.example`에는 실제 Secret이 아닌 Key 이름만 작성한다.

```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000

# Backend
AI_API_KEY=
DATABASE_URL=
```

실제 API Key는 `.env`에만 저장한다.
