# Mock Contract

> `/mock`은 팀 공통 계약 샘플이다. 실제 구현이 완성될 때까지 각 파트가 같은 구조로 병렬 개발하기 위해 사용한다.

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

## 3. 담당자별 사용

| Mock | 주요 사용자 | 목적 |
|---|---|---|
| `request-user-target.json` | Frontend / Backend | 최초 입력 테스트 |
| `diagnosis.json` | Backend / Rule Engine | 진단 계산 테스트 |
| `policy-match.json` | Backend / Policy / AI | 정책 판정 테스트 |
| `ai-input.json` | Backend / AI | AI 입력 테스트 |
| `action-plan.json` | AI / Backend | Structured output 테스트 |
| `final-response.json` | Backend / Frontend | 최초 결과 UI |
| `replan-request.json` | Frontend / Backend | 조건 변경 요청 |
| `replan-final-response.json` | Backend / Frontend / AI | 최초 Response와 같은 Snapshot 구조의 Re-planning 비교 |
| `loading.json` | Frontend | Loading UI 상태 정의 |
| `error.json` | Frontend / Backend | 오류 UI/예외처리 |

## 4. Demo 숫자 Freeze

최초:

```text
deposit_budget          = 5,000,000
required_initial_fund   = 6,000,000
initial_fund_gap        = 2,000,000
required_monthly_saving =   500,000
estimated_months        = 5
readiness_score         = 77
Policy 102              = CONDITIONAL
```

Re-plan:

```text
deposit_budget          = 4,000,000
required_initial_fund   = 5,000,000
initial_fund_gap        = 1,000,000
required_monthly_saving =   300,000
estimated_months        = 3
readiness_score         = 83
Policy 102              = AVAILABLE
```

발표 Demo와 Mock 숫자는 다르게 만들지 않는다.

## 5. P0 Request 기준

`request-user-target.json`은 이번 MVP의 P0 Request 계약을 그대로 따른다. Frontend가 보내는 필드는 다음 11개다.

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

`target_region`은 Frontend Request에 포함하지 않으며, Backend가 MVP 기본값 `"서울"`을 부여한다.

P1/P2 필드는 이번 P0 Request와 Mock에 포함하지 않는다.

## 6. P0 전환 원칙

- Frontend와 Backend는 동일한 P0 Request Mock을 사용한다.
- Frontend에서 사용하지 않는 가짜 값을 채워 Full Request를 유지하지 않는다.
- P1/P2 필드는 별도 Contract 합의 후 추가한다.

## 7. Frontend Mock 사용 규칙

컴포넌트:

```text
Component → plan.api.ts → Mock adapter
```

실 API 전환:

```text
Component → plan.api.ts → fetcher → Backend
```

컴포넌트에서 JSON을 직접 import하는 구조는 피한다.

## 8. Loading Mock

```json
{
  "status": "PROCESSING",
  "message": "독립 준비 상태와 이용 가능한 정책을 분석하고 있습니다."
}
```

이는 Backend 중간 response가 아니라 Frontend UI 정의용이다.

## 9. 정책 Mock 주의

현재 Mock의 정책명/정책내용/URL은 형식 확인용 예시다.

- 실제 Demo 전 Policy 담당이 확보한 실제 정책 데이터로 교체한다.
- `source_url`, `checked_at`을 유지한다.
- 정책 자격은 AI가 아니라 `eligibility_rules` 기반 Rule Engine이 판정한다.
