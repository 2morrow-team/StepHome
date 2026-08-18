# AI Pipeline — StepHome

> Diagnosis + Policy Matching 결과를 받아 실행 가능한 Action Plan을 생성하는 AI 파이프라인

---

## 설계 원칙

- **AI는 계산·판정하지 않는다.** 자금 계산은 Diagnosis, 정책 자격은 Rule Engine이 담당한다. AI는 그 결과를 행동으로 연결하는 역할만 한다.
- **Hallucination 방지.** Candidate Generator가 AI에게 생성 가능한 Action 범위를 사전 제한하고, Validator가 출력값을 후처리 검증한다.
- **모델 교체 비용 최소화.** LLM API 호출은 `_call_llm()` 단 하나의 함수에만 존재한다. 모델 교체 시 이 함수만 수정한다.

---

## 파일 구조

```text
backend/app/ai/
├── schemas.py            # Candidate 타입 + LLM 구조화 출력 Pydantic 스키마
├── candidate_generator.py # Diagnosis + PolicyMatch → Action 후보 결정
├── prompts.py            # Prompt 빌더 및 AI Input 조립
├── validator.py          # AI 출력 검증 및 Hallucination 방지
└── planner.py            # 파이프라인 오케스트레이터 + _call_llm 격리
```

---

## 파이프라인 흐름

```text
AI Input (Diagnosis + PolicyMatch + User/Target)
        │
        ▼
Candidate Generator
  판정된 eligibility_status를 보고 AI가 생성해도 되는 Action 후보 결정
  Rule Engine: "이 정책 자격이 있는가?" ← 이미 판정 완료
  Candidate Generator: "그 판정 결과로 어떤 Action을 허용할 것인가?"
        │
        ▼
Prompt Builder (prompts.py)
  ai_input + candidates → (system_prompt, user_prompt) 반환
        │
        ▼
_call_llm() — LLM API 호출 격리 지점
  Pydantic 스키마 기반 Structured Outputs 사용
  모델 교체 시 이 함수만 수정
        │
        ▼
Validator
  - Structured Outputs 이후 도메인 규칙을 추가 검증
  - 구조 검증 (summary, actions)
  - Backend 생성 필드 거부 (plan_id, action_id, status, created_at)
  - action_type / timing Enum 검증
  - 필수 필드 확인 (title, description, reason)
  - priority >= 1 확인
  - policy_id Hallucination 방지 (valid_policy_ids 집합과 대조)
        │
        ▼
ActionPlan (AI 출력 확정)
```

---

## Candidate Generator 규칙

| eligibility_status | 생성되는 Action 후보 |
|---|---|
| `AVAILABLE` | `POLICY` (POLICY_APPLY) |
| `CONDITIONAL` | 주거 조건은 `HOUSING`, 그 외 조건은 `POLICY` (CONDITION_ADJUST) |
| `NEED_MORE_INFO` | `POLICY` (INFORMATION_NOTICE) |
| `NOT_ELIGIBLE` | 후보 없음 |

`SAVING` 후보는 항상 첫 번째로 추가됩니다.

- `monthly_saving >= required_monthly_saving` → `SAVING_MAINTAIN`
- `monthly_saving < required_monthly_saving` → `SAVING_ADJUST`
- `monthly_saving` 미입력 → `SAVING_MAINTAIN` (기본값)

`CONTRACT` 후보는 항상 마지막에 추가됩니다.

Policy Context에는 `condition_details`와 정책 분류·지역·제공기관·지원금 단위를 포함해,
AI가 판정 근거를 바꾸지 않고 구체적인 Action 설명에 활용하도록 합니다.

---

## AI가 출력하는 필드

AI 출력에 포함되어야 하는 필드:

```json
{
  "summary": "사용자 상황 요약 (1~2문장)",
  "actions": [
    {
      "priority": 1,
      "action_type": "SAVING | POLICY | HOUSING | CONTRACT",
      "timing": "NOW | PREPARE | SEARCH_HOUSE | BEFORE_CONTRACT",
      "title": "행동 제목 (15자 이내)",
      "description": "구체적인 행동 방법",
      "reason": "추천 이유",
      "policy_id": null,
      "due_date": null
    }
  ]
}
```

AI 출력에 포함되어서는 안 되는 필드 (Backend 생성):

```text
plan_id, action_id, user_id, diagnosis_id, status, created_at
```

---

## eligibility_status 4단계

| 상태 | 의미 |
|---|---|
| `AVAILABLE` | 현재 바로 신청 가능 |
| `CONDITIONAL` | 일부 조건 조정 시 신청 가능 |
| `NEED_MORE_INFO` | 판정에 필요한 정보 부족 |
| `NOT_ELIGIBLE` | 자격 미충족 |

---

## Re-planning

사용자가 P0 필드(보증금, 목표일, 지역 등)를 변경하면:

1. Backend가 변경된 조건으로 Diagnosis 재계산 + Policy 재판정
2. `changed_fields` + 이전/현재 Diagnosis·PolicyMatch·ActionPlan을 AI에 전달
3. AI가 변경 전후 차이를 반영한 Action Plan 재생성

---

## Mock 테스트

LLM API를 호출하지 않고 파이프라인의 나머지 모듈을 검증합니다.

```bash
cd backend
pytest tests/ai/ -v
```

테스트 대상:

| 파일 | 테스트 내용 |
|---|---|
| `test_candidate_generator.py` | SAVING/POLICY/HOUSING/CONTRACT 후보 생성 규칙 |
| `test_validator.py` | 구조·Enum·필수 필드·Hallucination 검증 |
| `test_prompts.py` | Prompt 빌더 출력 및 AI Input 조립 |

---

## 환경 변수

```bash
OPENAI_API_KEY=<OpenAI Project API Key>
OPENAI_MODEL=gpt-5.6-terra
OPENAI_REASONING_EFFORT=low
```

프로젝트 루트의 `.env`에 설정합니다. API Key는 Git에 커밋하지 않습니다.
`.env.example` 참고.
