# 2Morrow Convention

2Morrow 프로젝트의 최소 협업 규칙입니다.

24시간 해커톤이라는 짧은 개발 기간을 고려하여 복잡한 Git Flow나 세부 코드 스타일보다 **작업 충돌 방지와 공통 데이터 Contract 유지**를 우선합니다.

---

## 1. Repository Structure

```text
2morrow/
├── frontend/       # Frontend
├── backend/        # Backend
├── policy/         # Policy Data / Rule Engine
├── ai/             # AI Action Plan
├── mock/           # 공통 Mock Data
├── docs/           # API / Schema / 개발 문서
├── README.md
└── .gitignore
```

### 기본 원칙

* 각 담당자는 자신의 담당 디렉토리를 중심으로 작업합니다.
* 다른 담당자의 디렉토리를 수정해야 하는 경우 해당 담당자에게 공유합니다.
* `mock/`, `docs/`는 특정 파트 소유가 아닌 **팀 공통 영역**으로 관리합니다.
* 공통 데이터 구조 변경 시 관련 파트에 반드시 공유합니다.

---

## 2. Branch Convention

`main` 브랜치를 기준으로 기능별 브랜치를 생성합니다.

### Branch Naming

```text
feat/<기능명>
fix/<수정내용>
docs/<문서내용>
refactor/<대상>
chore/<작업내용>
```

예시:

```text
feat/survey-form
feat/diagnosis-api
feat/policy-rule-engine
feat/action-plan
fix/result-rendering
docs/api-contract
chore/project-setup
```

### Branch Rules

* `main`에서 새로운 브랜치를 생성합니다.
* 작업 완료 후 `main`으로 PR을 생성합니다.
* 가능하면 `main`에 직접 push하지 않습니다.
* 하나의 브랜치에서는 하나의 목적을 중심으로 작업합니다.

---

## 3. Commit Convention

다음 prefix를 사용합니다.

| Prefix     | 용도                 |
| ---------- | ------------------ |
| `feat`     | 새로운 기능             |
| `fix`      | 버그 수정              |
| `docs`     | 문서 수정              |
| `refactor` | 기능 변화 없는 코드 개선     |
| `style`    | UI/CSS 또는 코드 포맷 수정 |
| `test`     | 테스트 추가/수정          |
| `chore`    | 설정, 패키지, 기타 작업     |

형식:

```text
<type>: <작업 내용>
```

예시:

```text
feat: 독립 정보 입력 폼 구현
feat: 진단 API 연동
fix: 결과 페이지 준비도 렌더링 오류 수정
docs: diagnosis response schema 수정
chore: frontend dependencies 추가
```

커밋 메시지는 작업 내용을 알아볼 수 있을 정도로 간결하게 작성합니다.

---

## 4. File & Directory Naming

### Directory

기본적으로 소문자를 사용합니다.

```text
components/
pages/
features/
hooks/
utils/
types/
```

여러 단어가 필요한 경우 `kebab-case`를 사용합니다.

```text
action-plan/
policy-result/
```

### React Component

컴포넌트 파일은 `PascalCase`를 사용합니다.

```text
DiagnosisCard.tsx
ActionPlanCard.tsx
PolicyCard.tsx
SurveyForm.tsx
```

### TypeScript

컴포넌트가 아닌 일반 TypeScript 파일은 `camelCase`를 사용합니다.

```text
apiClient.ts
calculateReadiness.ts
formatCurrency.ts
diagnosisTypes.ts
```

### Python

Python 파일과 모듈은 `snake_case`를 사용합니다.

```text
rule_engine.py
policy_matcher.py
action_plan.py
```

---

## 5. API & Data Contract

Frontend / Backend / Policy / AI 사이에서 전달되는 데이터 구조는 **공통 Contract**로 취급합니다.

특히 다음 데이터 구조는 임의로 변경하지 않습니다.

```text
Frontend
    ↓
사용자 입력 JSON
    ↓
Backend
    ↓
Diagnosis + Policy Result
    ↓
AI
    ↓
Action Plan JSON
    ↓
Backend
    ↓
Frontend
```

필드명, 타입, Enum, nullable 여부, JSON 구조를 변경해야 하는 경우 관련 담당자에게 공유한 뒤 수정합니다.

예:

```json
{
  "readiness_score": 68,
  "estimated_independence_date": "2027-03"
}
```

위 구조를 임의로 다음처럼 변경하지 않습니다.

```json
{
  "score": 68,
  "date": "2027-03"
}
```

### Contract 변경 시

1. 변경이 필요한 이유 확인
2. 영향받는 파트 담당자에게 공유
3. `docs/`의 Contract 수정
4. `mock/` 데이터 수정
5. 실제 구현 수정

가능하면 **문서 → Mock → 구현** 순서로 맞춥니다.

---

## 6. Mock Data

`mock/`은 Frontend / Backend / Policy / AI가 공통으로 참조하는 테스트 데이터입니다.

### 원칙

* 실제 API와 동일한 구조를 사용합니다.
* API Contract가 변경되면 Mock도 함께 변경합니다.
* 실제 개인정보를 사용하지 않습니다.
* Demo Persona 및 Sample Data는 팀에서 합의한 값을 사용합니다.

Mock 데이터와 실제 API 응답의 구조가 달라지지 않도록 유지합니다.

---

## 7. Environment Variables

API Key, Secret 등의 민감정보는 Git에 올리지 않습니다.

```text
.env
.env.local
```

등은 `.gitignore`에 포함합니다.

공유가 필요한 환경변수 이름은 `.env.example`에 작성합니다.

예:

```env
VITE_API_BASE_URL=
LLM_API_KEY=
```

실제 값은 작성하지 않습니다.

---

## 8. Pull Request & Merge

PR 제목은 Commit Convention과 동일한 형태를 권장합니다.

```text
feat: 독립 정보 입력 화면 구현
fix: 정책 결과 렌더링 오류 수정
docs: API contract 수정
```

PR에는 최소한 다음 내용을 작성합니다.

```text
## 작업 내용
- 구현하거나 수정한 내용

## 영향 범위
- 영향을 받는 디렉토리 / API / Contract

## 확인 사항
- 추가로 확인이 필요한 내용
```

공통 Contract를 변경한 PR이라면 반드시 영향 범위를 작성합니다.

---

## 9. Conflict Prevention

작업 시작 전:

```bash
git switch main
git pull origin main
git switch <branch>
git merge main
```

또는 현재 브랜치에서 최신 `main`을 반영합니다.

장시간 작업 후 한 번에 큰 PR을 만들기보다 기능 단위로 커밋하고 가능한 작은 단위로 merge합니다.

특히 다음 파일은 충돌 가능성이 높으므로 수정 시 공유합니다.

```text
README.md
docs/*
mock/*
.env.example
package.json
requirements.txt
```

---

## 10. Definition of Done

기능 완료 기준은 단순히 코드 작성 완료가 아니라 다음 조건을 만족하는 상태입니다.

* 기능이 정상적으로 실행된다.
* Mock 또는 실제 API 구조와 일치한다.
* 오류가 발생해도 핵심 흐름이 중단되지 않는다.
* 다른 파트와 연결되는 데이터 Contract를 준수한다.
* API Key 등 민감정보가 포함되지 않았다.
* 필요한 변경사항이 `docs/` 또는 `mock/`에 반영되었다.
* Demo Persona 기준으로 핵심 시나리오가 동작한다.

---

## 핵심 원칙

> **빠르게 개발하되, Contract는 임의로 변경하지 않는다.**

이번 프로젝트에서는 코드 스타일의 완벽한 통일보다
**Frontend ↔ Backend ↔ Policy ↔ AI 사이의 데이터 구조를 안정적으로 유지하는 것**을 우선합니다.
