# Architecture Contract

> Backend 최종 배포 단위는 FastAPI 하나이며, Diagnosis / Policy / AI를 내부 모듈로 포함한다.

## 1. Monorepo

```text
2morrow/
│
├── frontend/                     # 윤재
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
│   │   ├── diagnosis/            # 은총
│   │   │   └── calculator.py
│   │
│   │   ├── policy/               # 서우
│   │   │   ├── data/
│   │   │   ├── rules/
│   │   │   └── rule_engine.py
│   │
│   │   ├── ai/                   # 채린
│   │   │   ├── planner.py
│   │   │   ├── validator.py
│   │   │   └── prompts.py
│   │
│   │   └── db/
│   │       └── database.py
│   │
│   └── requirements.txt
│
├── mock/                         # 전원 공통 Mock
│
├── docs/                         # 전원 공통 Contract
│
├── .env.example
├── .gitignore
└── README.md
```

## 2. 호출 방향

### 허용

```text
Frontend
  ↓ HTTP
Router
  ↓
Service
  ├→ Diagnosis
  ├→ Policy / Rule Engine
  ├→ AI
  └→ DB
```

### 금지

```text
Frontend → AI 직접 호출
Frontend → Rule Engine 직접 호출
Diagnosis → Policy 직접 호출
Policy → AI 직접 호출
AI → Diagnosis 직접 호출
```

모듈 간 연결은 `plan_service.py`에서만 수행한다.

## 3. `plan_service.py` 책임

`plan_service.py`의 "전체 흐름 연결"은 **Backend 내부 orchestration**을 의미한다. Frontend 코드를 포함하지 않는다.

최초 플랜:

```text
validate User/Target
→ save User/Target
→ calculate Diagnosis
→ match Policies
→ build AI input
→ generate ActionPlan
→ validate AI output
→ create IDs/status
→ save
→ build final response
```

Re-planning:

```text
load previous User/Target/Diagnosis/Plan
→ apply changes
→ recalculate Diagnosis
→ rerun Policy Rule Engine
→ build replan AI input
→ generate new ActionPlan
→ create new plan_id/action_id
→ save
→ return before/after response
```

## 4. 환경 변수

`.env`는 commit하지 않는다.

공통 `.env.example`에는 실제 secret이 아닌 key 이름만 둔다.

예시:

```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000

# Backend
AI_API_KEY=
DATABASE_URL=
```

실제 key 이름은 AI/Backend 구현에 맞춰 확정한다.
