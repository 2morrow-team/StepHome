# MVP User Flow Contract

## 1. 제품 핵심 메시지

Figma 시작 화면의 현재 구조:

```text
첫 독립, 어디서부터 시작할까요?
정책 · 예산 · 일정을 한 번에 안내

맞춤 정책 확인
주거 예산 계산
독립 일정 만들기
```

이 세 축을 MVP에서도 유지한다.

## 2. MVP 전체 흐름

```text
Landing
→ P0 입력
→ 분석 Loading
→ Diagnosis + Policy + Action Plan 결과
→ 독립 준비 로드맵 / 오늘 할 일
→ 조건 변경
→ Re-planning Loading
→ 변경 전/후 결과
→ 새 Action Plan
```

### 중요한 원칙

P0 입력 UX는 여러 화면/step으로 나눌 수 있지만 **MVP에서 분석 API는 마지막에 한 번만 호출**한다.

즉 현재 MVP에서는 아래와 같은 별도 1차 분석 API를 추가하지 않는다.

```text
빠른 분석 API → 추가 입력 → 정밀 분석 API   (MVP 제외)
```

입력 부담은 **API 단계를 늘리는 것이 아니라 P0 필드 자체를 줄이고 UI step을 나누는 방식**으로 해결한다.

## 3. 권장 Setup Step

P0는 11개다.

### Step A — 현재 상태

- `age` — 만 나이, 정확한 INT
- `employment_status`
- `region`
- `monthly_income`

### Step B — 독립 목표

- `housing_type` — `MONTHLY_RENT / JEONSE`
- `target_date`
- `deposit_budget`
- `monthly_rent_budget`

`target_region`은 서울 한정 MVP 동안 `서울` 고정.

### Step C — 현재 준비 자금

- `current_savings`
- `current_emergency_fund`
- `monthly_saving`

### Submit

```text
[내 독립 계획 만들기]
→ POST /api/v1/plan
```

## 4. 입력 UI 계약

- `age`: 연령 구간이 아니라 **만 나이 정확한 숫자 입력**
- 금액: Slider가 아니라 **정확한 숫자 입력**이 기본. Quick chip은 UI 보조로 허용
- `housing_type`: 선택형
- 지역: 자유 텍스트보다 정규화된 선택형 권장. 정확한 지역 단위는 `open-decisions.md`
- `target_date`: Date Picker

## 5. Figma와 현재 Contract의 차이

Figma `3:2`의 정보 입력 프레임에는 현재 다음이 보인다.

```text
취업 상태
나이
예상 월 소득
보증금
월세
독립 예정일
```

그러나 P0에는 추가로 다음이 필요하다.

```text
region
housing_type
current_savings
current_emergency_fund
monthly_saving
```

따라서 실제 구현 전에 Figma setup flow를 P0에 맞게 보완한다.

Figma의 `아직 정하지 못했어요`는 이번 MVP에서 사용하지 않는다. `target_date`는 필수 `DATE`로 유지하고 해당 UI 선택지는 비활성화한다.

## 6. 분석 결과

최초 결과에서 최소 표시:

- `readiness_score`
- `estimated_months`
- `initial_fund_gap`
- `required_monthly_saving`
- matched policy 목록 / `eligibility_status`
- 각 정책의 판정 근거
- Action Plan summary
- 우선순위 Action 목록

Figma의 `AVAILABLE` / `추가 확인 필요` 카드 구조는 사용할 수 있다. 단, P1 추가 입력 기능이 아직 API에 없으면 `NEED_MORE_INFO`의 CTA를 실제 동작하는 것처럼 만들지 않는다.

## 7. Roadmap / Action Plan

로드맵의 기본 시간축:

```text
D-90 이전
D-60
D-30
계약 전
```

Action은 `timing` 기준으로 배치 가능하다.

```text
NOW
PREPARE
SEARCH_HOUSE
BEFORE_CONTRACT
```

정확한 D-Day ↔ timing 매핑은 Backend 계약이 아니라 UI grouping 규칙이며, 필요한 경우 Frontend에서 명시적으로 매핑한다.

## 8. Gamification — P0에서 유지할 것

핵심은 게임 기능 자체가 아니라 **독립 준비의 진행감을 시각화**하는 것이다.

유지:

- D-Day / 준비율
- Action 완료 피드백
- 집 진행 그래픽: `맨땅 → 텐트 → 골조 → 집 완성`
- 단계 변경 시 가벼운 Frontend transition

후순위/제외:

- 자재함
- 랜덤 자재 보상
- Streak
- 단계별 Badge 수집
- 대규모 아이템 인벤토리

현재 API에는 Action 상태를 저장하는 mutation endpoint가 없다. 따라서 체크 완료/집 변화가 P0 Demo에 필요하면 **Frontend 로컬 상태로 시연 가능**하되, 영구 저장 기능이라고 설명하지 않는다. API persistence가 필요하면 별도 Contract를 추가한다.

## 9. Re-planning UX

대표 Demo:

```text
희망 보증금 5,000,000원
→ 4,000,000원
```

화면에서 변경 전/후 최소 비교:

```text
준비도          77 → 83
필요 초기자금   600만 → 500만
부족 초기자금   200만 → 100만
필요 월 저축액   50만 → 30만
예상 준비기간     5개월 → 3개월
Policy 102      CONDITIONAL → AVAILABLE
```

이후 새 Action Plan을 보여준다.

## 10. MVP 화면 범위

### P0

- Landing
- Setup(P0 입력)
- Loading
- Result/Plan Dashboard
- Policy card/detail
- Action Plan / Roadmap
- Re-plan edit
- Re-plan before/after
- Error

### P1/P2 또는 Out-of-Scope

- 회원가입/로그인
- 계정/프로필 관리
- 알림 설정
- 스크랩/보관함 persistence
- 독립 서류 보관함
- 자재함/아이템 수집
- Streak/Badge
- 독립 주거 매물 검색
- 실제 정책 신청
