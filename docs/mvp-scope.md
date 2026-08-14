# MVP Scope & Priority

> 목표: **한 개의 완성된 E2E + Re-planning**을 먼저 만든 뒤 입력값과 부가기능을 확장한다.

## 1. P0 기능 — 먼저 끝내야 하는 것

1. 회원가입 없이 시작
2. P0 사용자 입력
3. `POST /api/v1/plan`
4. Diagnosis 계산
5. Policy Rule Matching
6. AI Action Plan
7. Frontend 결과 화면
8. `deposit_budget` 변경 Re-planning
9. Loading / Error
10. 최소 Demo 정책 데이터

## 2. 입력 Field Priority

### P0 — 첫 E2E와 Re-planning에 필요한 입력

| 필드 | 사용 이유 |
|---|---|
| `age` | 정책 연령 판정 |
| `employment_status` | 핵심 정책 조건 후보 |
| `region` | 현재 거주지역 기반 정책 판정 |
| `monthly_income` | 정책 소득 판정 |
| `current_savings` | 초기자금 계산 |
| `current_emergency_fund` | 실제 사용 가능자금 / 비상자금 점수 |
| `monthly_saving` | 저축계획 점수 / 예상 준비기간 |
| `target_date` | 목표일까지 필요한 월 저축액 |
| `deposit_budget` | 초기자금 / 정책 Rule / Re-planning 핵심 변수 |
| `monthly_rent_budget` | 주거비 목표 / 정책 조건 후보 |
| `housing_type` | 정책 주거형태 Rule |

### P1 — 정책별 추가 질문 / 핵심 E2E 이후

| 논리 필드 | 현재 상태 |
|---|---|
| 가구원 수 | **v1 데이터 스키마에 없음. API key TBD** |
| 가구원/부모 합산소득 | **v1 데이터 스키마에 없음. API key TBD** |
| `current_housing_type` | 기존 스키마 존재, P1 |

P1은 모든 사용자에게 처음부터 묻기보다 `NEED_MORE_INFO` 정책에 필요한 경우 추가 질문하는 방향이 목표다. 단, 이를 위한 Request/endpoint는 아직 v1에 없다.

### P2 — 정밀화/확장

```text
debt
monthly_living_expense
monthly_fixed_expense
current_housing_cost
housing_preference
```

현재 Demo Diagnosis 계산식에는 위 값이 직접 사용되지 않으므로 P0에서 제외한다.

### 고정값

서울 한정 MVP라면:

```text
target_region = "서울"
```

Frontend에서 별도 입력받지 않는다.

## 3. P0/P1/P2의 의미

- **P0**: 없으면 첫 E2E 또는 Demo Re-planning이 깨짐
- **P1**: 핵심 E2E가 된 뒤 정책 판정 정확도를 늘리는 확장
- **P2**: 정밀 진단/개인화/UX 고도화용

데이터베이스 컬럼 존재 여부와 UI 우선순위는 별개다.

## 4. Re-planning Scope

P0 Demo에서 보장:

```text
deposit_budget 변경
→ Diagnosis 변화
→ PolicyMatch 변화
→ ActionPlan 변화
```

다른 P0 필드도 장기적으로 변경 가능하게 설계할 수 있으나, MVP Contract상 필수 시연 범위는 `deposit_budget` 하나다.

## 5. Policy Scope

- MVP는 서울 중심의 제한된 정책 데이터로 시연
- 정책 자격 판정은 `eligibility_rules` 기반
- 실제 정책명/URL/checked_at은 Demo 전 실데이터로 교체
- 전국 실시간 수집/RAG/Agent는 범위 밖

정책 개수는 구현 안정성이 우선이며, 기존 논의의 `5~10개` 또는 그보다 작은 확정 Demo subset을 사용할 수 있다. 숫자보다 Rule이 실제 동작하는지가 우선이다.

## 6. Gamification Priority

### P0 Visual

- 준비율
- D-Day
- 집 4단계 이미지
- 단계 전환 animation

### P1

- Action 체크에 따른 로컬 UI 피드백
- 가벼운 축하 효과

### P2 / 제외

- Streak
- Badge collection
- 자재 획득
- 자재함
- 랜덤 보상

## 7. Out-of-Scope

- 회원가입/로그인/소셜 로그인
- 실제 정책 신청
- 실제 주거 매물 중개
- 복잡한 계정/프로필
- 알림 persistence
- Calendar integration
- 전국 실시간 정책 데이터 자동 수집
- Action status DB mutation API(현재 v1 미정)
- 서류 보관/파일 업로드