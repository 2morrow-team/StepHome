# 2Morrow Frontend Guide

> 2Morrow의 Figma Design System과 프론트엔드 기술 스택을 한 문서에서 관리하기 위한 기준 문서입니다.  
> Design source: https://www.figma.com/design/KUoQiOLJ3HjBgFG0IBJ8Mh/2Morrow-Design-System-v1?node-id=0-1

---

## 1. Frontend Stack

| 영역 | 기술 | 이 프로젝트에서 역할 |
|---|---|---|
| 프레임워크 | **React** | 전체 UI |
| 언어 | **TypeScript** | API / 정책 / 설문 데이터 타입 안정성 |
| 빌드 | **Vite** | 개발 서버, 빌드 |
| 스타일 | **Tailwind CSS** | 빠른 UI 구현 |
| 서버 상태 | **TanStack Query** | API 요청, 로딩, 에러, 캐시 |
| 클라이언트 상태 | **Zustand** | 설문 draft, 데모 상태 |
| API Client | **native fetch wrapper** | 백엔드 REST API |
| 테스트 | **Vitest** | 비용 계산 / 변환 로직 테스트 |

### 기술 사용 원칙

- 화면과 컴포넌트는 **React + TypeScript** 기준으로 구현한다.
- 스타일은 **Tailwind CSS**를 사용하되, 색상과 타이포그래피는 아래 디자인 토큰을 기준으로 사용한다.
- 서버에서 가져오는 데이터와 요청 상태는 **TanStack Query**가 담당한다.
- 설문 작성 중 값, 화면 간 임시 입력값, 데모용 로컬 상태처럼 서버와 직접 동기화되지 않는 상태는 **Zustand**가 담당한다.
- API 호출은 UI 컴포넌트에서 `fetch`를 직접 반복 호출하지 않고 **native fetch wrapper**를 통해 일관되게 처리한다.
- 독립 비용 계산, 값 변환 등 순수 로직은 UI와 분리하고 **Vitest**로 검증한다.

---

## 2. Design Direction

Figma Design System의 기본 방향은 다음과 같다.

- **Mobile-first**
- 진단, 정책 매칭, Action Plan을 위한 차분하고 신뢰감 있는 UI
- 한 번에 하나의 결정을 유도하는 구조
- 모바일 인터랙션 요소는 **48px touch target**을 기본으로 사용
- 상태는 색상만으로 전달하지 않고 **텍스트 또는 아이콘과 함께 표현**
- `Danger`는 오류 또는 이용 불가 상태에만 사용
- `Caution`은 추가 확인이 필요한 상태에 사용

---

## 3. Color System

### 3.1 Core Colors

| Figma Token | Value | 역할 |
|---|---:|---|
| `Action/Primary` | `#1F4B6E` | Primary CTA, 주요 액션 |
| `Action/Hover` | `#173A56` | Primary CTA hover |
| `Action/Subtle` | `#E8F0F6` | 선택 상태, 낮은 강도의 강조 배경 |
| `Action/On Primary` | `#FFFFFF` | Primary 배경 위 텍스트 |
| `Background/Page` | `#EEF1F4` | 앱 전체 페이지 배경 |
| `Background/Surface` | `#F8F9FA` | 카드, 섹션 등 주요 surface |
| `Background/Surface Subtle` | `#F2F4F6` | Secondary button 등 낮은 강조 surface |
| `Background/Control` | `#FFFFFF` | 활성화된 Input / Control 배경 |
| `Text/Primary` | `#102A43` | 제목, 본문 핵심 텍스트 |
| `Text/Secondary` | `#667085` | 설명, 보조 텍스트 |
| `Border/Default` | `#E5E7EB` | 기본 경계선 |
| `Border/Interactive` | `#7A8495` | 기본 Input 등 인터랙티브 요소 경계선 |
| `Border/Focus` | `#1F4B6E` | Focus 상태 경계선 |

### 3.2 Status Colors

| 상태 | Foreground | Background | 사용 |
|---|---:|---:|---|
| Success / Available | `#4F6B59` | `#EDF3EF` | 이용 가능, 완료 |
| Caution / Review | `#9A5A16` | `#FBF2E6` | 추가 확인 필요 |
| Danger / Unavailable | `#B4493E` | `#FBEDEB` | 이용 불가, 오류 |

### 3.3 Disabled Colors

| Token | Value | 사용 |
|---|---:|---|
| `Disabled/Background` | `#F2F4F6` | 비활성 Button / Input 배경 |
| `Disabled/Text` | `#98A2B3` | 비활성 텍스트 |
| `Disabled/Border` | `#D0D5DD` | 비활성 경계선 |

### 3.4 Figma에 명시된 CSS 변수

```css
--background-page: #eef1f4;
--background-control: #ffffff;

--disabled-background: #f2f4f6;
--disabled-text: #98a2b3;
--disabled-border: #d0d5dd;

--action-on-primary: #ffffff;

--border-interactive: #7a8495;
--border-focus: #1f4b6e;

--status-success: #4f6b59;
--status-caution: #9a5a16;
--status-danger: #b4493e;

--radius-8: 8px;
--radius-12: 12px;
--radius-16: 16px;
--radius-full: 999px;
```

---

## 4. Typography

### 4.1 Font Family

- **SUIT Variable**
- Figma Text Style 전체가 SUIT Variable 기준
- Letter spacing: `0`

### 4.2 Text Styles

| Style | Weight | Size | Line Height | 주요 용도 |
|---|---:|---:|---:|---|
| `Display/28` | 700 Bold | 28px | 36px | 화면의 가장 큰 핵심 제목 |
| `Title/22` | 700 Bold | 22px | 섹션 제목 |
| `Heading/18` | 700 Bold | 18px | 카드 / 결과 영역 제목 |
| `Number/24` | 700 Bold | 24px | 준비도, 금액, 주요 수치 |
| `Body/16` | 400 Regular | 16px | 주요 본문 |
| `Body/14` | 400 Regular | 14px | 일반 설명문 |
| `Label/14` | 600 Medium | 14px | Input label, Button label |
| `Caption/12` | 500 Medium | 12px | 상태, 보조 설명, 메타 정보 |

---

## 5. Spacing, Radius & Elevation

### 5.1 Spacing

Figma Foundation에서 강조하는 기본 spacing 단위:

- `4px`
- `8px`
- `16px`

각 컴포넌트 내부에서는 해당 컴포넌트 스펙에 정의된 padding / gap 값을 따른다.

### 5.2 Radius

| Token | Value | 대표 사용 |
|---|---:|---|
| `radius/8` | 8px | 작은 내부 surface |
| `radius/12` | 12px | Button, Input, Action Item |
| `radius/16` | 16px | Card, Section |
| `radius/full` | 999px | Chip, Badge, 원형 Step |

### 5.3 Elevation

`Elevation/Card`

```css
box-shadow: 0 4px 12px rgba(16, 42, 67, 0.08);
```

---

## 6. Components

## 6.1 Button

### 역할

- Primary: 폼 진행과 핵심 CTA
- Secondary: 뒤로 가기 또는 낮은 우선순위의 대안 액션

### 기본 규격

- Figma specimen: `280 × 48`
- Height: `48px`
- Horizontal padding: `16px`
- Vertical padding: `12px`
- Radius: `12px`
- Label: `Label/14`

### Primary

| State | Background | Border | Text |
|---|---|---|---|
| Default | `#1F4B6E` | 없음 | `#FFFFFF` |
| Hover | `#173A56` | 없음 | `#FFFFFF` |
| Disabled | `#F2F4F6` | `#D0D5DD` | `#98A2B3` |

### Secondary

| State | Background | Border | Text |
|---|---|---|---|
| Default | `#F2F4F6` | `#E5E7EB` | `#102A43` |
| Hover | `#E8F0F6` | `#1F4B6E` | `#102A43` |
| Disabled | `#F2F4F6` | `#D0D5DD` | `#98A2B3` |

Keyboard focus는 Input과 동일한 primary outline treatment를 사용한다.

---

## 6.2 Input

### 역할

숫자 기반 사용자 입력을 위한 필드.

### States

- Default
- Focus
- Error
- Disabled

### 기본 규격

- Figma specimen 전체: `280 × 118`
- Control height: `48px`
- Control horizontal padding: `14px`
- Radius: `12px`
- Label: `Label/14`
- Input text: `Body/14`
- Helper / Error text: `Caption/12`
- Label → Control → Helper 간 gap: `8px`

### State Style

| State | Background | Border | Text |
|---|---|---|---|
| Default | `#FFFFFF` | `1px #7A8495` | Primary / Secondary |
| Focus | `#FFFFFF` | `2px #1F4B6E` | `#102A43` |
| Error | `#FFFFFF` | `1px #B4493E` | Error helper `#B4493E` |
| Disabled | `#F2F4F6` | `1px #D0D5DD` | `#98A2B3` |

Error는 잘못되거나 실제 계획상 불가능한 값에만 사용한다.

---

## 6.3 Select Chip

### 역할

- 단일 또는 다중 선택 옵션
- 현재 계획의 선호 상태 표시

### 기본 규격

- Height: `40px`
- Horizontal padding: `16px`
- Vertical padding: `10px`
- Radius: `999px`
- Label: `Label/14`

| State | Background | Border | Text |
|---|---|---|---|
| Selected | `#1F4B6E` | 없음 | `#FFFFFF` |
| Unselected | `#F8F9FA` | `#7A8495` | `#102A43` |

---

## 6.4 Status Badge

### 역할

정책 자격 상태를 빠르게 구분한다.

### 상태

- `Available`: 현재 이용 가능
- `Review`: 추가 확인 필요
- `Unavailable`: 현재 조건 미충족

### 기본 규격

- Height: `28px`
- Horizontal padding: `10px`
- Vertical padding: `6px`
- Radius: `999px`
- Label: `Caption/12`

| Status | Text | Background |
|---|---|---|
| Available | `#4F6B59` | `#EDF3EF` |
| Review | `#9A5A16` | `#FBF2E6` |
| Unavailable | `#B4493E` | `#FBEDEB` |

라벨은 판단을 과장하지 않고 사실 기반으로 작성한다.

---

## 6.5 Policy Card

### 역할

정책 추천 결과에서 다음 정보를 하나의 카드로 제공한다.

- 정책명
- 자격 상태
- 추천 / 설명
- 예상 지원 혜택
- 독립 계획에서 해당 정책이 갖는 의미

### Figma specimen

- Size: `584 × 252`
- Radius: `16px`
- Background: `#F8F9FA`
- Elevation: Card shadow
- Horizontal padding: `20px`
- Vertical padding: `35px`

### 내부 타이포

- Policy title: `Heading/18`
- Description: `Body/14`
- Benefit label: `Caption/12`
- Benefit value: `Number/24`

---

## 6.6 Action Item / Metric Card

### 역할

독립 진단 결과를 하나의 핵심 수치로 요약한다.

예:

- 현재 준비도
- 예상 독립 가능 시점
- 부족 자금
- 기타 단일 핵심 결과

### Figma specimen

- Size: `280 × 120`
- Padding: `20px`
- Gap: `8px`
- Radius: `16px`
- Background: `#F8F9FA`
- Elevation: Card shadow

### 정보 구조

1. Label — `Caption/12`
2. Value — `Number/24`
3. Supporting text — `Body/14`

한 카드에는 하나의 핵심 수치만 보여준다.

---

## 6.7 Action Item

### 역할

AI Action Plan의 우선순위 행동 하나를 표현한다.

### States

- `Pending`
- `Complete`

### Figma specimen

- Size: `584 × 88`
- Padding: `16px`
- Gap: `14px`
- Radius: `12px`
- Step circle: `32 × 32`, radius `999px`

### Pending

- Step background: `#E8F0F6`
- Step text: `#1F4B6E`
- Border: `#E5E7EB`

### Complete

- Step background: `#EDF3EF`
- Step text: `#4F6B59`
- Border: `#4F6B59`

### 정보 구조

- Step
- Action title — `Heading/18`
- Expected impact / detail — `Body/14`

Title은 반드시 행동 중심 문장으로 작성하고, Detail은 해당 행동의 예상 효과에 집중한다.

---

## 7. Frontend State Responsibility

### TanStack Query

다음처럼 **서버에서 받아오거나 서버로 전송하는 상태**를 담당한다.

- 진단 요청
- 정책 매칭 결과
- Action Plan 결과
- 재진단 결과
- API 요청의 loading / error / cache

### Zustand

다음처럼 **사용자 화면 흐름 안에서 유지되는 클라이언트 상태**를 담당한다.

- 설문 draft
- 아직 제출하지 않은 입력값
- 데모 시나리오 상태
- 화면 간 임시 선택값

서버 데이터 자체를 Zustand에 중복 저장하지 않는다.

---

## 8. API Client Convention

API 요청은 native `fetch`를 한 번 감싼 wrapper를 통해 사용한다.

목적:

- Base URL 처리
- 공통 Header 처리
- JSON serialization / parsing
- 공통 에러 처리
- TanStack Query의 `queryFn` / `mutationFn`에서 재사용

UI 컴포넌트 내부에 개별적인 `fetch(...)` 호출을 반복 작성하지 않는다.

---

## 9. Testing Scope

Vitest는 우선적으로 UI 표현보다 **순수 계산 / 변환 로직** 검증에 사용한다.

대상 예시:

- 독립 필요 자금 계산
- 현재 자금과 목표 자금의 gap 계산
- 월 저축 가능액에 따른 기간 변환
- 입력값 → API payload 변환
- API response → 화면 표시 데이터 변환

---

## 10. Implementation Checklist

- [ ] 모든 주요 UI 색상은 Figma semantic token 기준으로 사용한다.
- [ ] 활성 Input 배경은 `#FFFFFF`을 사용한다.
- [ ] 모든 비활성 Button / Input은 동일한 Disabled color system을 사용한다.
- [ ] 페이지 배경은 `#EEF1F4`을 사용한다.
- [ ] 주요 Surface는 `#F8F9FA`를 사용한다.
- [ ] 폰트는 SUIT Variable을 사용한다.
- [ ] Button / Input의 기본 touch target은 48px 높이를 유지한다.
- [ ] 상태 표현은 색상만으로 전달하지 않는다.
- [ ] `Danger`는 오류 / 이용 불가에 한정한다.
- [ ] `Caution`은 추가 확인 필요 상태에 사용한다.
- [ ] 서버 상태는 TanStack Query로 관리한다.
- [ ] 설문 draft 등 클라이언트 상태는 Zustand로 관리한다.
- [ ] API 요청은 native fetch wrapper를 통해 처리한다.
- [ ] 계산 / 변환 로직은 UI에서 분리하고 Vitest로 테스트한다.
