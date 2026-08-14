# Open Decisions

> 아래 항목은 현재 소스만으로 완전히 확정되지 않았다. 담당자가 임의로 다른 값을 만들지 말고 구현 전에 짧게 합의한다.

## P0 결정 완료

### 1. `employment_status` 전체 Enum

이번 MVP에서 다음과 같이 확정한다.

| Figma label | Backend Enum |
|---|---|
| 취업 준비 중 | `JOB_SEEKER` |
| 재직 중 | `EMPLOYED` |
| 대학생 | `STUDENT` |
| 기타 | `OTHER` |

> 위 매핑은 기존 Notion에 없던 내용을 이번 MVP Contract에 추가한 것이다.

### 2. P0 Request와 `target_region`

- Request는 P0 11개 입력값만 받는다.
- `target_region`은 Frontend가 보내지 않는다.
- Backend가 MVP 기본값 `"서울"`을 부여한다.
- Backend/Rule Engine/Response에는 `target_region`을 유지한다.

### 3. `target_date` required 유지

이번 MVP에서는 `target_date`를 필수 `DATE`로 유지한다. Figma의 `아직 정하지 못했어요` 선택지는 MVP 입력에서 비활성화한다.

## P0 Blocker

### 4. `region` 정규화 단위

현재 예시:

```text
region = "경기도"
target_region = "서울"
```

필요 결정:

- 시/도 단위만 사용할지
- 정책 데이터가 요구하면 시·군·구까지 확장할지
- Frontend dropdown 목록과 Policy data의 canonical string을 어떻게 맞출지

MVP 서울 한정일 때 `target_region`은 Backend에서 `서울`로 고정한다.

### 5. Policy Rule의 `region` 비교 대상

현재 Policy Rule 예시의 `"region": ["서울"]`이 어떤 사용자 필드와 비교되는지 아직 정의되지 않았다.

```text
user.region          = 현재 거주 지역
target.target_region = 독립 희망 지역
policy.region        = 정책 지원 지역
```

추후 다음 중 하나를 확정한다.

- 주거 정책은 `target.target_region`과 비교
- 거주 요건 정책은 `user.region`과 비교
- Policy별 Rule에 비교 대상을 명시

현재 Demo 구현은 `target.target_region`을 비교 대상으로 임시 사용해 `서울` Demo를 재현하되, 최종 정책 Contract 확정 전까지는 추후 논의사항으로 유지한다.

### 6. P0-only Request schema 반영

기존 API/PDF는 Full User/Target Request다. MVP는 P0 입력으로 축소하기로 했다.

반영 상태:

- Backend Pydantic은 P0 Request를 기준으로 구현한다.
- `/mock/request-user-target.json`은 P0 계약으로 갱신 완료했다.
- `api.md`와 Swagger를 P0 Request 기준으로 동기화한다.

## P1

### 7. 가구원 수 / 가구소득 API field name

기획/Figma에는 가구소득 추가 확인 흐름이 있으나 현재 데이터 스키마에는 필드가 없다.

필요:

- 필드명
- 타입
- 월/연 소득 기준
- 본인 포함 여부
- 정책 Rule과의 연결

### 8. `NEED_MORE_INFO` 추가 입력 API

현재 v1 endpoint는 `/plan`, `/replan`뿐이다.

결정:

- P1에서 `/replan`의 `changes`로 추가정보를 받을지
- 별도 정책 추가확인 API를 만들지

P0에서는 미구현 가능.

## Diagnosis Edge Case

### 9. `monthly_saving = 0`

현재:

```text
estimated_months = ceil(total_gap / monthly_saving)
```

0 division 처리 규칙 필요.

이번 MVP에서는 `monthly_saving`을 0보다 크게 validation하고, 0 입력은 `INVALID_INPUT`으로 처리한다. 0 저축 상태를 지원하는 계산 규칙은 후속 Contract에서 결정한다.

### 10. target date month 계산

Demo는 정확히 5개월 차이를 사용한다.

필요 결정:

- 일자가 다를 때 ceil/floor/달력 월 차이 중 무엇을 사용할지
- 과거 날짜 validation

### 11. Demo 상수의 일반화

현재 Demo:

```text
moving_initial_cost = 1,000,000
target_emergency_fund = 1,500,000
```

현재 근거/일반화 공식 없음. MVP 상수로 유지할지 추후 입력/계산으로 바꿀지 결정.

## Frontend / UX

### 12. `target_date`의 "아직 정하지 못했어요"

이번 MVP에서는 `target_date` required 유지와 Figma 선택지 비활성화로 결정 완료했다. 향후 nullable 또는 추천 날짜가 필요하면 별도 Contract 변경으로 다룬다.

### 13. Action 완료 persistence

현재 Action에는 `status`가 있지만 status 변경 API가 없다.

- P0: 화면 내 로컬 체크만 시연 가능
- DB 저장이 필요하면 mutation endpoint Contract 추가

## Infra

### 14. Production Base URL / 배포 플랫폼

현재 Local:

```text
http://localhost:8000
```

Production URL과 Render/Railway/Fly.io 중 실제 배포 선택은 TBD.
