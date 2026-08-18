# Diagnosis Rules Contract

> StepHome MVP의 독립 준비도 계산 계약이다.  
> 근거가 확정되지 않은 별도 비용을 임의로 추가하지 않는다.

## 1. 입력

Diagnosis가 사용하는 핵심 입력은 다음과 같다.

```text
total_assets
monthly_savings
planned_move_in_date
desired_deposit
```

Demo Persona:

```text
total_assets          = 30,000,000
monthly_savings       =    500,000

planned_move_in_date  = 2027-03-01
desired_deposit       = 90,000,000
```

Re-planning 후:

```text
desired_deposit
90,000,000 → 70,000,000
```

---

## 2. 제거된 기존 계산

최종 MVP에서는 다음을 사용하지 않는다.

```text
current_emergency_fund
target_emergency_fund
emergency_fund_gap
emergency_score
```

또한 근거가 확정되지 않은 다음과 같은 별도 상수를 사용하지 않는다.

```text
MOVING_INITIAL_COST
고정 이사비
고정 초기비용
```

즉, 정책/기획에서 별도로 확정되지 않은 금액을 Backend가 임의로 초기자금에 더하지 않는다.

---

## 3. 필요 초기자금

현재 MVP에서 필요한 초기자금은 희망 보증금을 기준으로 계산한다.

```text
required_initial_fund
= desired_deposit
```

Demo Before:

```text
required_initial_fund
= 90,000,000
```

Demo After:

```text
required_initial_fund
= 70,000,000
```

---

## 4. 초기자금 부족액

```text
initial_fund_gap
= max(required_initial_fund - total_assets, 0)
```

Before:

```text
max(90,000,000 - 30,000,000, 0)
= 60,000,000
```

After:

```text
max(70,000,000 - 30,000,000, 0)
= 40,000,000
```

---

## 5. 목표일까지 필요한 월 저축액

```text
required_monthly_saving
= ceil(initial_fund_gap / months_until_target)
```

`months_until_target`은 Backend 계산 시점부터 `planned_move_in_date`까지의 남은 기간을 기준으로 한다.

날짜가 실행 시점에 따라 달라질 수 있으므로 Demo Contract에서 임의의 고정 월수를 만들지 않는다.

---

## 6. 초기자금 준비도 — 최대 70점

```text
fund_score
= min(total_assets / required_initial_fund, 1) × 70
```

`required_initial_fund = 0`인 예외 상황은 Backend에서 별도 안전 처리한다.

---

## 7. 저축계획 준비도 — 최대 30점

```text
saving_score
= min(monthly_savings / required_monthly_saving, 1) × 30
```

이미 필요한 자금을 모두 확보하여:

```text
required_monthly_saving = 0
```

인 경우 `saving_score = 30`으로 처리한다.

---

## 8. 최종 준비도 — 100점 만점

```text
readiness_score
= round(fund_score + saving_score)
```

구성:

```text
fund_score   최대 70점
saving_score 최대 30점
----------------------
합계         최대 100점
```

Backend는 결과를 `0~100` 범위로 제한한다.

---

## 9. 예상 준비기간

현재 월 저축액이 0보다 큰 경우:

```text
estimated_months
= ceil(initial_fund_gap / monthly_savings)
```

이미 초기자금을 확보한 경우:

```text
initial_fund_gap = 0
→ estimated_months = 0
```

`monthly_savings = 0`이고 `initial_fund_gap > 0`인 경우 유한한 예상 준비기간을 계산할 수 없으므로:

```text
estimated_months = null
```

로 처리한다.

---

## 10. Re-planning Demo Contract

대표 Demo는 **희망 보증금 변경**이다.

```text
Before
desired_deposit = 90,000,000

After
desired_deposit = 70,000,000
```

이에 따라 Diagnosis는 새로운 Target 기준으로 다시 계산한다.

```text
required_initial_fund
90,000,000 → 70,000,000

initial_fund_gap
60,000,000 → 40,000,000
```

`required_monthly_saving`, `fund_score`, `saving_score`, `readiness_score`, `estimated_months`도 동일한 계산식으로 다시 계산한다.

---

## 11. Policy 변화와 Diagnosis의 관계

Policy 6인 `서울시 청년월세지원`은 희망 보증금 상한이:

```text
80,000,000
```

이다.

Demo:

```text
Before
desired_deposit = 90,000,000
→ deposit_max 초과
→ CONDITIONAL

After
desired_deposit = 70,000,000
→ deposit_max 충족
→ AVAILABLE
```

Policy 자격 변화 자체는 Diagnosis Calculator가 아니라 **Policy Rule Engine**이 판정한다.

---

## 12. AI에 전달하는 Diagnosis 값

AI는 다음 값을 행동계획 생성에 활용할 수 있다.

```text
readiness_score
fund_score
saving_score
required_initial_fund
initial_fund_gap
required_monthly_saving
estimated_months
```

AI는 이 값을 다시 계산하지 않는다.

```text
Backend Diagnosis
→ 계산 책임

AI
→ 계산 결과를 설명 및 Action 생성에 활용
```
