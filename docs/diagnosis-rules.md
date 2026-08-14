# Diagnosis Rules Contract

> 아래 수치는 **공통 Demo Persona를 재현하기 위한 현재 MVP 계산 계약**이다. 정책 데이터나 계산식 자체를 변경하려면 Mock/API/발표 수치까지 함께 갱신한다.

## 1. Demo Persona

기준일: `2026-08-12`

```text
current_savings         = 5,000,000
current_emergency_fund  = 1,000,000
monthly_saving          =   500,000

target_date             = 2027-01-12
monthly_rent_budget     =   500,000
deposit_budget          = 5,000,000
housing_type            = MONTHLY_RENT
```

Demo 가정:

```text
이사/초기비용 = 1,000,000
목표 비상자금 = 1,500,000
희망일까지 남은 기간 = 5개월
```

> 이사/초기비용 1,000,000원과 목표 비상자금 1,500,000원의 산정 근거/일반화 규칙은 현재 소스에 정의되어 있지 않다. MVP Demo 상수로 취급한다.

## 2. 실제 사용 가능한 초기자금

```text
usable_initial_fund
= current_savings - current_emergency_fund
= 5,000,000 - 1,000,000
= 4,000,000
```

## 3. 필요 초기자금

현재 Demo:

```text
required_initial_fund
= deposit_budget + moving_initial_cost
= 5,000,000 + 1,000,000
= 6,000,000
```

## 4. 초기자금 부족액

```text
initial_fund_gap
= max(required_initial_fund - usable_initial_fund, 0)
= max(6,000,000 - 4,000,000, 0)
= 2,000,000
```

## 5. 비상자금 부족액

```text
emergency_fund_gap
= max(target_emergency_fund - current_emergency_fund, 0)
= max(1,500,000 - 1,000,000, 0)
= 500,000
```

## 6. 목표일까지 필요한 월 저축액

```text
total_gap
= initial_fund_gap + emergency_fund_gap
= 2,500,000

required_monthly_saving
= total_gap / months_until_target
= 2,500,000 / 5
= 500,000
```

현재 문서에는 월수 계산의 반올림/일자 경계 규칙이 정의되어 있지 않다. Demo에서는 `2026-08-12 → 2027-01-12 = 5개월`로 고정 검증한다.

## 7. 준비도

### 초기자금 준비도 — 50점

```text
fund_score
= min(usable_initial_fund / required_initial_fund, 1) × 50
= 33.33
```

### 저축계획 달성도 — 30점

```text
saving_score
= min(monthly_saving / required_monthly_saving, 1) × 30
= 30
```

### 비상자금 준비도 — 20점

```text
emergency_score
= min(current_emergency_fund / target_emergency_fund, 1) × 20
= 13.33
```

### 최종 준비도

```text
readiness_score
= round(fund_score + saving_score + emergency_score)
= round(76.66)
= 77
```

## 8. 예상 준비기간

```text
estimated_months
= ceil((initial_fund_gap + emergency_fund_gap) / monthly_saving)
= ceil(2,500,000 / 500,000)
= 5
```

`monthly_saving = 0`일 때의 처리 규칙은 현재 미정 (`open-decisions.md`의 ### 6. `monthly_saving = 0`)


## 9. Re-planning Demo Contract

대표 Demo는 **희망 보증금 하나만 변경**한다.

```text
deposit_budget
5,000,000 → 4,000,000
```

그 외 User/Target 조건은 동일하다.

### 변경 후

```text
required_initial_fund     6,000,000 → 5,000,000
initial_fund_gap          2,000,000 → 1,000,000
required_monthly_saving     500,000 →   300,000
estimated_months                  5 →         3
readiness_score                  77 →        83
Policy 102              CONDITIONAL → AVAILABLE
```

계산:

```text
usable_initial_fund = 4,000,000
required_initial_fund = 4,000,000 + 1,000,000 = 5,000,000
initial_fund_gap = 1,000,000
emergency_fund_gap = 500,000
total_gap = 1,500,000
required_monthly_saving = 1,500,000 / 5 = 300,000
estimated_months = ceil(1,500,000 / 500,000) = 3

fund_score = 4,000,000 / 5,000,000 × 50 = 40
saving_score = min(500,000 / 300,000, 1) × 30 = 30
emergency_score = 13.33
readiness_score = round(83.33) = 83
```

Policy 102 상태 변화는 Demo Rule에서 `deposit_budget = 4,000,000`일 때 보증금 조건을 충족한다고 가정한 시나리오다. 실제 정책 적용 시 `eligibility_rules`가 우선한다.

## 10. AI에 넘기는 핵심 수치

AI는 아래 값을 설명/행동계획에 활용할 수 있지만 다시 계산하지 않는다.

- `required_monthly_saving`
- `estimated_months`
- `initial_fund_gap`
- `emergency_fund_gap`
- `readiness_score`
- 검증된 `PolicyMatch`
