# MVP Scope & Priority

> 목표: 실제 Demo Policy를 이용한 **완성된 E2E + Re-planning**을 안정적으로 구현한다.

## 1. P0 기능

1. 회원가입 없이 시작
2. P0 15개 입력
3. `POST /api/v1/plan`
4. Diagnosis 계산
5. Policy Rule Matching
6. AI Action Plan 생성
7. Frontend 결과 화면
8. P0 조건 변경 Re-planning
9. `POST /api/v1/replan`
10. Loading / Error 처리
11. 실제 Demo Policy 1~6 사용

---

## 2. P0 입력

### User — 10개

| 필드 | 사용 이유 |
|---|---|
| `age` | 정책 연령 판정 |
| `employment_status` | 정책 취업 상태 판정 |
| `current_region` | 현재 거주지역 정책 판정 |
| `personal_monthly_income` | 개인 소득 정책 판정 |
| `total_assets` | 초기자금 Diagnosis 및 자산조건 판정 |
| `monthly_savings` | 저축계획 및 예상 준비기간 |
| `housing_status` | 무주택 조건 판정 |
| `youth_household_monthly_income` | 청년가구 소득 판정 |
| `youth_household_size` | 청년가구 소득기준 계산 |
| `marital_status` | 혼인 조건 판정 |

### Target — 5개

| 필드 | 사용 이유 |
|---|---|
| `planned_move_in_date` | 목표일까지 필요한 저축액 계산 |
| `desired_deposit` | 초기자금 / 정책 보증금 조건 / Re-planning |
| `desired_monthly_rent` | 월세 정책 조건 |
| `desired_housing_type` | 정책 주거형태 조건 |
| `desired_region` | 희망지역 정책 판정 |

---

## 3. 입력 원칙

지역은 전국 + 시·도 Enum을 사용한다.

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

시·군·구는 MVP에서 입력받지 않는다.

`desired_region`은 Backend 고정값이 아니라 사용자 입력이다.

---

## 4. P0에서 제거된 입력

```text
current_emergency_fund
```

비상자금 관련 Diagnosis도 MVP에서 제거한다.

원가구 소득 및 원가구 가구원 수는 P0에서 입력받지 않는다.

원가구 정보 등 추가 정보가 필요한 정책은 `NEED_MORE_INFO`로 처리할 수 있다.

---

## 5. Re-planning Scope

P0 입력은 전체 수정 가능한 범용 `changes` 구조를 사용한다.

대표 Demo는:

```text
desired_deposit
90,000,000 → 70,000,000
```

이다.

Demo 기대 흐름:

```text
Target 변경
→ Diagnosis 재계산
→ Policy Rule Engine 재실행
→ PolicyMatch 변화
→ AI Re-planning
→ 새로운 ActionPlan
```

Policy 6:

```text
Before
90,000,000 > deposit_max 80,000,000
→ CONDITIONAL

After
70,000,000 <= deposit_max 80,000,000
→ AVAILABLE
```

---

## 6. Policy Scope

MVP는 실제 Demo Policy 1~6을 사용한다.

```text
1 청년월세 지원사업
2 청년전세임대
3 제주 청년 희망충전 월세 지원
4 청년전용 버팀목 전세자금대출
5 청년 매입임대
6 서울시 청년월세지원
```

정책 판정은:

```text
Policy.eligibility_rules
→ Rule Engine
→ PolicyMatch
```

순서로 수행한다.

AI가 정책 자격을 직접 판단하지 않는다.

---

## 7. NEED_MORE_INFO

정책에 실제 조건이 존재하지만 현재 MVP 입력/Rule Engine으로 자동 판정할 수 없는 경우:

```text
additional_conditions
```

로 관리한다.

예:

```text
LIVE_SEPARATELY_FROM_PARENTS
ORIGINAL_HOUSEHOLD_INCOME_REQUIREMENT
ASSET_REQUIREMENT
PRIORITY_REQUIREMENTS
```

필요한 정보가 부족하면 `NEED_MORE_INFO`로 처리할 수 있다.

MVP에서는 2차 추가 입력 플로우를 구현하지 않는다.

---

## 8. Diagnosis Scope

Diagnosis는 다음 점수로 구성한다.

```text
fund_score   최대 70
saving_score 최대 30
-------------------
총점         최대 100
```

다음은 사용하지 않는다.

```text
emergency_score
current_emergency_fund
target_emergency_fund
emergency_fund_gap
```

근거가 확정되지 않은 별도의 고정 이사비/초기비용도 계산에 추가하지 않는다.

---

## 9. AI Action Scope

AI는 사용자의 독립 목표 달성을 중심으로 Diagnosis와 PolicyMatch를 활용한다.

```text
AVAILABLE
→ 신청/활용 Action 가능

CONDITIONAL
→ 사용자가 변경 가능한 조건이고
   정책 활용 가치가 있을 경우 조정 Action 후보

NEED_MORE_INFO
→ 부족 정보 안내 수준

NOT_ELIGIBLE
→ 해당 정책 관련 Action 생성하지 않음
```

Action Type:

```text
SAVING
POLICY
HOUSING
CONTRACT
```

---

## 10. Gamification Priority

### P0

- 준비율
- D-Day
- 집 진행 그래픽
- 단계 전환 animation
- Action 완료에 대한 Frontend 로컬 피드백

### P1/P2

- Streak
- Badge collection
- 자재 획득
- 자재함
- 랜덤 보상

---

## 11. Out-of-Scope

- 회원가입/로그인
- 실제 정책 신청
- 실제 주거 매물 중개
- 전국 정책 실시간 자동 수집
- RAG 기반 정책 자동 수집
- 복잡한 프로필
- 원가구 추가 입력 플로우
- NEED_MORE_INFO 2차 입력 API
- Action 상태 DB mutation API
- 서류 보관/파일 업로드
- 알림 persistence
- Calendar integration
