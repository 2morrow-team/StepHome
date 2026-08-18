# MVP User Flow Contract

## 1. 제품 핵심 메시지

```text
첫 독립, 어디서부터 시작할까요?

정책 · 예산 · 일정을 한 번에 안내

맞춤 정책 확인
주거 예산 계산
독립 일정 만들기
```

StepHome MVP에서도 이 세 축을 유지한다.

---

## 2. 전체 흐름

```text
Landing
→ P0 입력
→ 분석 Loading
→ Diagnosis + Policy + Action Plan
→ 독립 준비 로드맵
→ 조건 변경
→ Re-planning Loading
→ 변경 전/후 결과
→ 새로운 Action Plan
```

---

## 3. 입력 API 원칙

입력 UX는 여러 화면으로 나눌 수 있지만 분석 API는 마지막에 한 번 호출한다.

```text
P0 입력 완료
→ POST /api/v1/plan
```

MVP에서는 다음 구조를 사용하지 않는다.

```text
1차 입력
→ 1차 분석
→ 추가 질문
→ 2차 분석
```

정책 판정에 추가 정보가 필요한 경우 `NEED_MORE_INFO`로 표시한다.

---

## 4. P0 Setup

P0 입력은 총 15개다.

### Step A — 기본 정보

```text
age
employment_status
current_region
housing_status
marital_status
```

UI 예시:

```text
만 나이
취업 상태
현재 거주 지역
주택 소유 여부
혼인 여부
```

### Step B — 경제 정보

```text
personal_monthly_income
youth_household_monthly_income
youth_household_size
total_assets
monthly_savings
```

UI 예시:

```text
본인 월 소득
청년가구 월 소득
청년가구 수
총 보유자금
월 저축액
```

### Step C — 독립 희망 조건

```text
planned_move_in_date
desired_region
desired_deposit
desired_monthly_rent
desired_housing_type
```

UI 예시:

```text
독립 예정일
희망 거주 지역
희망 보증금
희망 월세
희망 주거 형태
```

### Submit

```text
[내 독립 계획 만들기]
→ POST /api/v1/plan
```

---

## 5. 입력 UI 계약

### 나이

정확한 만 나이 정수 입력.

### 지역

자유 텍스트보다 선택형을 사용한다.

```text
NATIONAL
SEOUL
BUSAN
DAEGU
INCHEON
GWANGJU
DAEJEON
ULSAN
SEJONG
GYEONGGI
GANGWON
CHUNGBUK
CHUNGNAM
JEONBUK
JEONNAM
GYEONGBUK
GYEONGNAM
JEJU
```

사용자 입력에서는 실제 거주/희망 시·도를 선택한다.

시·군·구는 받지 않는다.

### 주택 소유 여부

```text
NO_HOME
HAS_HOME
```

### 혼인 여부

```text
UNMARRIED
MARRIED
```

### 희망 주거 형태

```text
MONTHLY_RENT
JEONSE
```

### 금액

정확한 원 단위 숫자를 Backend에 전달한다.

### 독립 예정일

Date Picker를 사용하고 Backend에는 `YYYY-MM-DD` 형식으로 전달한다.

---

## 6. Demo Persona

```text
만 나이                  25
취업 상태                 EMPLOYED
현재 거주 지역             SEOUL
주택 소유 여부             NO_HOME
혼인 여부                 UNMARRIED

본인 월 소득              2,500,000
청년가구 월 소득           2,500,000
청년가구 수               1
총 보유자금               30,000,000
월 저축액                   500,000

독립 예정일               2027-03-01
희망 거주 지역             SEOUL
희망 보증금               90,000,000
희망 월세                   500,000
희망 주거 형태             MONTHLY_RENT
```

---

## 7. 분석 Loading

```text
POST /api/v1/plan
→ Frontend Loading
→ Backend Response
```

Backend는 중간 Loading Response를 반환하지 않는다.

---

## 8. 분석 결과

최초 결과에서 최소 표시:

- `readiness_score`
- `estimated_months`
- `initial_fund_gap`
- `required_monthly_saving`
- matched policy 목록
- 각 정책의 `eligibility_status`
- 정책 판정 근거
- Action Plan summary
- 우선순위 Action 목록

---

## 9. Policy UI

정책 상태:

```text
AVAILABLE
CONDITIONAL
NEED_MORE_INFO
NOT_ELIGIBLE
```

`NEED_MORE_INFO`는 추가 정보가 필요하다는 의미로 표시할 수 있지만 MVP에 실제 2차 입력 API가 없으면 동작하지 않는 CTA를 제공하지 않는다.

---

## 10. Roadmap / Action Plan

Action Type:

```text
SAVING
POLICY
HOUSING
CONTRACT
```

Timing:

```text
NOW
PREPARE
SEARCH_HOUSE
BEFORE_CONTRACT
```

AI가 생성한 Action을 timing 기준으로 Frontend Roadmap에 배치할 수 있다.

---

## 11. Re-planning UX

대표 Demo:

```text
희망 보증금
90,000,000
→ 70,000,000
```

### Before

```text
desired_deposit = 90,000,000

서울시 청년월세지원
deposit_max = 80,000,000

90,000,000 > 80,000,000
→ CONDITIONAL
```

### After

```text
desired_deposit = 70,000,000

70,000,000 <= 80,000,000
→ AVAILABLE
```

화면에서는 최소한 다음 변화를 보여준다.

```text
희망 보증금
90,000,000 → 70,000,000

Diagnosis
Before → After

서울시 청년월세지원
CONDITIONAL → AVAILABLE

Action Plan
Before → 새로운 Action Plan
```

Diagnosis의 정확한 점수/월수는 Backend Calculator 결과를 사용하고 UI에서 임의로 고정하지 않는다.

---

## 12. Re-planning API

```text
조건 변경
→ POST /api/v1/replan
→ Loading
→ Before / After
→ 새로운 Action Plan
```

대표 Demo에서는 `desired_deposit`만 수정하지만 Backend Re-planning 구조는 P0 입력 전체를 처리할 수 있는 범용 `changes` 구조를 사용한다.

---

## 13. Gamification

P0에서 유지:

- D-Day
- 준비율
- Action 완료 피드백
- 집 진행 그래픽
- 단계 변경 transition

집 진행 예시:

```text
맨땅
→ 텐트
→ 골조
→ 집 완성
```

Action 완료 상태를 Backend에 저장하는 별도 mutation API가 없는 동안에는 Frontend 로컬 상태로 시연할 수 있다.

---

## 14. MVP 화면 범위

### P0

- Landing
- Setup
- Loading
- Result / Plan Dashboard
- Policy Card / Detail
- Action Plan / Roadmap
- Re-plan Edit
- Re-plan Before / After
- Error

### P1/P2 또는 Out-of-Scope

- 회원가입/로그인
- 계정/프로필 관리
- 알림 설정
- 스크랩 persistence
- 서류 보관함
- Streak/Badge
- 실제 주거 매물 검색
- 실제 정책 신청
- NEED_MORE_INFO 추가 입력 Flow
