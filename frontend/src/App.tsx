import { useMemo, useState, type ReactNode } from 'react'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { compareScenarios, createPlan, replan } from './api/plan.api'
import { ActionItem, AiScenarioCard, Button, GlobalNav, MetricCard, PolicyCard, StatusBadge } from './components'
import UiPreview from './previews/UiPreview'
import { toPlanRequest, usePlanStore } from './stores/plan-store'
import type { PlanDraft } from './stores/plan-store'
import type { StatusBadgeProps } from './components'
import type {
  Action,
  EligibilityStatus,
  EmploymentStatus,
  HousingStatus,
  HousingType,
  MaritalStatus,
  PlanResponse,
  PlanSnapshot,
  Region,
  ReplanChanges,
  ReplanResponse,
  ScenarioOption,
  ScenarioPriority,
  ScenarioResponse,
} from './types/api'
import phase1Image from './assets/1__.png.webp'
import phase2Image from './assets/2__.png.webp'
import phase3Image from './assets/3__.png.webp'
import phase4Image from './assets/4__.png.webp'

type NumericField = Extract<
  keyof PlanDraft,
  | 'age'
  | 'youth_household_monthly_income'
  | 'youth_household_size'
  | 'personal_monthly_income'
  | 'total_assets'
  | 'monthly_savings'
  | 'desired_deposit'
  | 'desired_monthly_rent'
>

type SelectOption<T extends string> = {
  value: T
  label: string
}

type Phase = 1 | 2 | 3 | 4

const FORM_CONTROL_CLASS =
  'box-border h-12 min-h-12 w-full rounded-subtle border border-border-default bg-background-control px-3 py-0 type-body leading-5 text-text-primary'

const REGION_OPTIONS: Array<SelectOption<Region>> = [
  { value: 'SEOUL', label: '서울' },
  { value: 'BUSAN', label: '부산' },
  { value: 'DAEGU', label: '대구' },
  { value: 'INCHEON', label: '인천' },
  { value: 'GWANGJU', label: '광주' },
  { value: 'DAEJEON', label: '대전' },
  { value: 'ULSAN', label: '울산' },
  { value: 'SEJONG', label: '세종' },
  { value: 'GYEONGGI', label: '경기' },
  { value: 'GANGWON', label: '강원' },
  { value: 'CHUNGBUK', label: '충북' },
  { value: 'CHUNGNAM', label: '충남' },
  { value: 'JEONBUK', label: '전북' },
  { value: 'JEONNAM', label: '전남' },
  { value: 'GYEONGBUK', label: '경북' },
  { value: 'GYEONGNAM', label: '경남' },
  { value: 'JEJU', label: '제주' },
]

const EMPLOYMENT_OPTIONS: Array<SelectOption<EmploymentStatus>> = [
  { value: 'EMPLOYED', label: '재직 중' },
  { value: 'JOB_SEEKER', label: '취업 준비 중' },
  { value: 'STUDENT', label: '학생' },
  { value: 'OTHER', label: '기타' },
]

const MARITAL_OPTIONS: Array<SelectOption<MaritalStatus>> = [
  { value: 'UNMARRIED', label: '미혼' },
  { value: 'MARRIED', label: '기혼' },
]

const HOUSING_STATUS_OPTIONS: Array<SelectOption<HousingStatus>> = [
  { value: 'NO_HOME', label: '무주택' },
  { value: 'HAS_HOME', label: '주택 보유' },
]

const HOUSING_TYPE_OPTIONS: Array<SelectOption<HousingType>> = [
  { value: 'MONTHLY_RENT', label: '월세' },
  { value: 'JEONSE', label: '전세' },
]

const SCENARIO_PRIORITY_LABELS: Record<ScenarioPriority, string> = {
  FAST_MOVE: '빠른 독립',
  LOW_MONTHLY_BURDEN: '월 부담 최소화',
  POLICY_BENEFIT: '정책 활용 우선',
}

const STATUS_LABELS: Record<EligibilityStatus, string> = {
  AVAILABLE: '신청 가능',
  CONDITIONAL: '조건 조정 필요',
  NEED_MORE_INFO: '추가 확인 필요',
  NOT_ELIGIBLE: '현재 대상 아님',
}

const POLICY_BADGE_STATUS: Record<EligibilityStatus, StatusBadgeProps['status']> = {
  AVAILABLE: 'available',
  CONDITIONAL: 'conditional',
  NEED_MORE_INFO: 'review',
  NOT_ELIGIBLE: 'unavailable',
}

const phaseImages: Record<Phase, string> = {
  1: phase1Image,
  2: phase2Image,
  3: phase3Image,
  4: phase4Image,
}

const phaseMessages: Record<Phase, { label: string; message: string }> = {
  1: { label: '1단계 · 0~25점', message: '이제 첫걸음을 시작해볼까요?' },
  2: { label: '2단계 · 26~50점', message: '조금씩 기반을 만들고 있어요!' },
  3: { label: '3단계 · 51~75점', message: '독립이 눈앞에 보여요!' },
  4: { label: '4단계 · 76~100점', message: '독립할 준비가 되었어요!' },
}

function formatWon(value: number) {
  return value.toLocaleString('ko-KR') + '원'
}

function formatCompactWon(value: number) {
  if (value >= 10000) return `${Math.round(value / 10000).toLocaleString('ko-KR')}만원`
  return formatWon(value)
}

function formatMonth(value: string) {
  return value.slice(0, 7).replace('-', '.')
}

function formatDate(value: string) {
  return value.replace(/-/g, '.')
}

function getOptionLabel<T extends string>(options: Array<SelectOption<T>>, value: T) {
  return options.find((option) => option.value === value)?.label ?? value
}

function getReadinessPhase(score: number): Phase {
  if (score <= 25) return 1
  if (score <= 50) return 2
  if (score <= 75) return 3
  return 4
}

function getDday(date: string) {
  const today = new Date()
  const target = new Date(`${date}T00:00:00`)
  return Math.max(Math.ceil((target.getTime() - today.getTime()) / 86400000), 0)
}

function addDays(date: Date, days: number) {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

function toIsoDate(date: Date) {
  return date.toISOString().slice(0, 10)
}

function getPhaseEndDates(plannedMoveInDate: string) {
  const start = new Date()
  const end = new Date(`${plannedMoveInDate}T00:00:00`)
  const totalDays = Math.max(Math.ceil((end.getTime() - start.getTime()) / 86400000), 4)

  return [1, 2, 3, 4].reduce((dates, phase) => {
    dates[phase as Phase] = toIsoDate(addDays(start, Math.ceil((totalDays * phase) / 4)))
    return dates
  }, {} as Record<Phase, string>)
}

function getActionPhase(action: Action, index: number): Phase {
  if (action.phase && action.phase >= 1 && action.phase <= 4) return action.phase
  return (Math.min(Math.floor(index / 2) + 1, 4) as Phase)
}

function getActionDueDate(action: Action, phase: Phase, phaseEndDates: Record<Phase, string>) {
  return action.due_date ?? phaseEndDates[phase]
}

function getPolicyDescription(policy: PlanSnapshot['matched_policies'][number]) {
  if (policy.eligibility_status === 'AVAILABLE') {
    return policy.support_amount_text || policy.description || '받을 수 있는 지원을 확인해보세요.'
  }
  if (policy.eligibility_status === 'CONDITIONAL') return policy.eligibility_text || '충족해야 하는 조건을 확인해보세요.'
  if (policy.eligibility_status === 'NOT_ELIGIBLE') return '조건 미충족'
  return policy.eligibility_text || '추가 확인이 필요합니다.'
}

function PageShell({ children }: { children: ReactNode }) {
  return (
    <>
      <GlobalNav />
      <main className="min-h-screen bg-background-page text-text-primary">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
          {children}
        </div>
      </main>
    </>
  )
}

function PageHeader({ eyebrow, title, description, meta }: { eyebrow?: string; title: string; description: string; meta?: string }) {
  return (
    <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="space-y-2">
        {eyebrow && <p className="type-caption text-action-primary">{eyebrow}</p>}
        <h1 className="type-display text-text-primary">{title}</h1>
        <p className="type-body text-text-secondary">{description}</p>
      </div>
      {meta && (
        <span className="w-fit rounded-pill bg-background-surface-subtle px-3 py-2 type-caption text-text-secondary">
          {meta}
        </span>
      )}
    </header>
  )
}

function StepPills({ activeStep }: { activeStep: 1 | 2 }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex gap-3">
        {[1, 2].map((step) => (
          <span
            key={step}
            className={`rounded-pill border px-3 py-2 type-label ${
              activeStep === step
                ? 'border-action-primary bg-action-subtle text-action-primary'
                : 'border-border-subtle bg-background-control text-text-secondary'
            }`}
          >
            {step}. {step === 1 ? '내 정보 입력' : '목표 설정'}
          </span>
        ))}
      </div>
      <p className="type-label text-text-secondary">{activeStep} / 2</p>
    </div>
  )
}

function TextInputField({
  label,
  helper,
  type = 'text',
  value,
  placeholder,
  min,
  onChange,
}: {
  label: string
  helper: string
  type?: 'text' | 'number' | 'date'
  value: string | number
  placeholder?: string
  min?: number
  onChange: (value: string) => void
}) {
  return (
    <label className="grid min-w-0 gap-2">
      <span className="type-label text-text-primary">{label}</span>
      <input
        className={FORM_CONTROL_CLASS}
        type={type}
        min={min}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
      <span className="type-caption text-text-secondary">{helper}</span>
    </label>
  )
}

function SelectInputField<T extends string>({
  label,
  helper,
  value,
  options,
  onChange,
  placeholder,
}: {
  label: string
  helper: string
  value: T | ''
  options: Array<SelectOption<T>>
  onChange: (value: T) => void
  placeholder?: string
}) {
  return (
    <label className="grid min-w-0 gap-2">
      <span className="type-label text-text-primary">{label}</span>
      <select
        className={FORM_CONTROL_CLASS}
        value={value}
        onChange={(event) => onChange(event.target.value as T)}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <span className="type-caption text-text-secondary">{helper}</span>
    </label>
  )
}

function FormCard({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <section className="rounded-card border border-border-subtle bg-background-surface p-6">
      <div className="mb-5 space-y-2">
        <h2 className="type-heading text-text-primary">{title}</h2>
        <p className="type-caption text-text-secondary">{description}</p>
      </div>
      {children}
    </section>
  )
}

function InputStepOne({ onNext }: { onNext: () => void }) {
  const { draft, setDraft } = usePlanStore()
  const updateNumber = (field: NumericField, value: string) => setDraft({ [field]: Number(value) } as Partial<PlanDraft>)

  return (
    <PageShell>
      <PageHeader
        eyebrow="독립 플랜 만들기"
        title="내 정보를 입력해주세요"
        description="기본 정보와 경제 정보를 바탕으로 현실적인 독립 계획을 계산합니다."
      />
      <StepPills activeStep={1} />
      <FormCard title="기본 정보" description="현재 상태를 확인해 정책 자격과 독립 준비 기준을 계산합니다.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <TextInputField label="나이" helper="만 나이를 입력해주세요." type="number" min={0} value={draft.age} placeholder="예: 24세" onChange={(value) => updateNumber('age', value)} />
          <SelectInputField label="취업상태" helper="현재 상태와 가장 가까운 항목을 선택해주세요." value={draft.employment_status} options={EMPLOYMENT_OPTIONS} onChange={(value) => setDraft({ employment_status: value })} />
          <SelectInputField label="현재 거주 지역" helper="시·도 기준으로 선택해주세요." value={draft.current_region} options={REGION_OPTIONS} onChange={(value) => setDraft({ current_region: value })} />
          <SelectInputField label="주택 소유 여부" helper="본인 명의 주택 보유 여부를 선택해주세요." value={draft.housing_status} options={HOUSING_STATUS_OPTIONS} onChange={(value) => setDraft({ housing_status: value })} />
          <SelectInputField label="혼인 여부" helper="현재 혼인 상태를 선택해주세요." value={draft.marital_status} options={MARITAL_OPTIONS} onChange={(value) => setDraft({ marital_status: value })} />
        </div>
      </FormCard>
      <FormCard title="경제 정보" description="현재 자금과 저축 여력을 바탕으로 독립 목표의 현실성을 계산합니다.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <TextInputField label="본인 월 소득" helper="세전 월 소득을 입력해주세요." type="number" min={0} value={draft.personal_monthly_income} placeholder="예: 2,500,000원" onChange={(value) => updateNumber('personal_monthly_income', value)} />
          <TextInputField label="청년가구 월 소득" helper="청년가구원의 월 소득 합계를 입력해주세요." type="number" min={0} value={draft.youth_household_monthly_income} placeholder="예: 4,000,000원" onChange={(value) => updateNumber('youth_household_monthly_income', value)} />
          <TextInputField label="청년가구 수" helper="본인을 포함한 청년가구원 수를 입력해주세요." type="number" min={1} value={draft.youth_household_size} placeholder="예: 2명" onChange={(value) => updateNumber('youth_household_size', value)} />
          <TextInputField label="총 보유자금" helper="예금·적금 등 활용 가능한 자금을 입력해주세요." type="number" min={0} value={draft.total_assets} placeholder="예: 60,000,000원" onChange={(value) => updateNumber('total_assets', value)} />
          <TextInputField label="월 저축액" helper="매달 독립 준비에 사용할 금액을 입력해주세요." type="number" min={0} value={draft.monthly_savings} placeholder="예: 500,000원" onChange={(value) => updateNumber('monthly_savings', value)} />
        </div>
      </FormCard>
      <div className="flex items-center justify-between">
        <p className="type-caption text-text-secondary">입력한 정보는 독립 계획 계산과 정책 추천에만 사용됩니다.</p>
        <Button className="w-60" onClick={onNext}>다음: 목표 설정</Button>
      </div>
    </PageShell>
  )
}

function InputStepTwo({
  onBack,
  onCreate,
  isPending,
  error,
}: {
  onBack: () => void
  onCreate: () => void
  isPending: boolean
  error?: Error | null
}) {
  const { draft, setDraft } = usePlanStore()
  const updateNumber = (field: NumericField, value: string) => setDraft({ [field]: Number(value) } as Partial<PlanDraft>)

  return (
    <PageShell>
      <PageHeader
        eyebrow="독립 플랜 만들기"
        title="독립 목표를 설정해주세요"
        description="희망하는 독립 시점과 주거 조건을 입력하면 필요한 준비 계획을 계산합니다."
      />
      <StepPills activeStep={2} />
      <FormCard title="독립 희망 조건" description="목표 조건을 입력하면 필요한 자금과 월 주거비 부담을 함께 계산합니다.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <TextInputField label="독립 예정일" helper="목표 입주 시점을 선택해주세요." type="date" value={draft.planned_move_in_date} onChange={(value) => setDraft({ planned_move_in_date: value })} />
          <SelectInputField label="희망 거주 지역" helper="시·도 기준으로 선택해주세요." value={draft.desired_region} options={REGION_OPTIONS} onChange={(value) => setDraft({ desired_region: value })} />
          <TextInputField label="희망 보증금" helper="감당 가능한 보증금 범위를 입력해주세요." type="number" min={0} value={draft.desired_deposit} placeholder="예: 10,000,000원" onChange={(value) => updateNumber('desired_deposit', value)} />
          <TextInputField label="희망 월세" helper="관리비를 제외한 월세를 입력해주세요." type="number" min={0} value={draft.desired_monthly_rent} placeholder="예: 600,000원" onChange={(value) => updateNumber('desired_monthly_rent', value)} />
          <SelectInputField label="희망 주거 형태" helper="월세·전세를 선택해주세요." value={draft.desired_housing_type} options={HOUSING_TYPE_OPTIONS} onChange={(value) => setDraft({ desired_housing_type: value })} />
        </div>
      </FormCard>
      <section className="rounded-control bg-background-surface-subtle px-5 py-4">
        <h2 className="type-label text-text-primary">목표는 나중에 다시 조정할 수 있어요</h2>
        <p className="mt-1 type-body text-text-secondary">계획 생성 후 보증금·월세·입주 시점 등을 바꾸면 진단과 액션 플랜이 다시 계산됩니다.</p>
      </section>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" className="w-40" onClick={onBack}>이전</Button>
        <Button className="w-60" disabled={isPending} onClick={onCreate}>내 독립 플랜 만들기</Button>
      </div>
      {error && <p className="rounded-control bg-status-danger-background p-4 type-body text-status-danger">{error.message}</p>}
    </PageShell>
  )
}

function PlanGuard() {
  return (
    <PageShell>
      <section className="grid min-h-[420px] place-items-center rounded-card border border-border-subtle bg-background-surface p-8 text-center shadow-card">
        <div className="max-w-md">
          <p className="type-title text-text-primary">먼저 내 독립 플랜을 만들어주세요</p>
          <p className="mt-3 type-body text-text-secondary">AI 시뮬레이터와 플랜 수정은 생성된 독립 플랜을 기준으로 작동합니다.</p>
          <Link className="mt-6 inline-flex min-h-12 items-center justify-center rounded-control bg-action-primary px-5 type-label text-text-inverse" to="/">
            내 독립 플랜 만들기
          </Link>
        </div>
      </section>
    </PageShell>
  )
}

function ReadinessHero({ snapshot }: { snapshot: PlanSnapshot }) {
  const score = snapshot.diagnosis.readiness_score
  const phase = getReadinessPhase(score)
  const phaseMessage = phaseMessages[phase]
  const progress = Math.min(Math.max(score, 0), 100)

  return (
    <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_160px]">
      <div className="relative min-h-[260px] overflow-hidden rounded-card bg-action-subtle p-8">
        <div className="relative z-10 flex h-full max-w-[68%] flex-col gap-5">
          <p className="type-label text-action-primary">현재 독립 준비도</p>
          <p className="type-display text-text-primary">{score}점</p>
          <div className="h-3 overflow-hidden rounded-pill bg-background-control">
            <div className="h-full rounded-pill bg-action-primary" style={{ width: `${progress}%` }} />
          </div>
          <div className="flex flex-wrap justify-between gap-3 type-label text-text-primary">
            <span>입주까지 D-{getDday(snapshot.target.planned_move_in_date)}</span>
            <span className="type-caption text-text-secondary">목표 입주일 {formatDate(snapshot.target.planned_move_in_date)}</span>
          </div>
        </div>
        <div className="absolute right-6 top-6 z-10 rounded-subtle bg-background-control px-4 py-2 type-body text-text-secondary shadow-sm">
          <strong className="mr-2 text-action-primary">{phaseMessage.label}</strong>
          {phaseMessage.message}
        </div>
        <img src={phaseImages[phase]} alt="" className="absolute bottom-0 right-0 h-[260px] w-[260px] object-contain" />
      </div>
      <MetricCard label="월 저축 목표" value={formatCompactWon(snapshot.diagnosis.required_monthly_saving)} supportingText="현재 계획 기준" className="items-center justify-center text-center" />
    </section>
  )
}

function PlanDashboard({ plan }: { plan: PlanResponse }) {
  const phaseEndDates = useMemo(() => getPhaseEndDates(plan.target.planned_move_in_date), [plan.target.planned_move_in_date])
  const actions = plan.action_plan.actions.map((action, index) => {
    const phase = getActionPhase(action, index)
    return { action, phase, dueDate: getActionDueDate(action, phase, phaseEndDates) }
  })
  const [selectedPhase, setSelectedPhase] = useState<Phase>(getReadinessPhase(plan.diagnosis.readiness_score))
  const [completedIds, setCompletedIds] = useState<Set<number>>(
    () => new Set(plan.action_plan.actions.filter((a) => a.status === 'DONE').map((a) => a.action_id))
  )

  const visibleActions = actions.filter((item) => item.phase === selectedPhase)
  const fallbackActions = visibleActions.length > 0 ? visibleActions : actions.slice(0, 2)

  const baseScore = plan.diagnosis.readiness_score
  const totalActions = actions.length
  const scorePerAction = totalActions > 0 ? Math.round((100 - baseScore) / totalActions) : 0
  const simulatedScore = Math.min(baseScore + completedIds.size * scorePerAction, 100)

  const simulatedSnapshot = useMemo(
    () => ({ ...plan, diagnosis: { ...plan.diagnosis, readiness_score: simulatedScore } }),
    [plan, simulatedScore]
  )

  const handleStatusChange = (actionId: number, status: 'complete' | 'incomplete') => {
    setCompletedIds((prev) => {
      const next = new Set(prev)
      if (status === 'complete') next.add(actionId)
      else next.delete(actionId)
      return next
    })
  }

  return (
    <PageShell>
      <PageHeader
        title="내 독립 플랜"
        description="현재 준비 상태와 다음 행동을 한눈에 확인하세요."
        meta="계획 기준 · 2026.08.18"
      />
      <ReadinessHero snapshot={simulatedSnapshot} />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_416px]">
        <section className="min-w-0 rounded-card border border-border-subtle bg-background-surface p-6">
          <h2 className="type-title text-text-primary">독립 준비 로드맵</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {[1, 2, 3, 4].map((phase) => (
              <button
                key={phase}
                type="button"
                className={`rounded-pill px-3 py-2 type-caption ${selectedPhase === phase ? 'bg-action-subtle text-action-primary' : 'bg-background-surface-subtle text-text-secondary'}`}
                onClick={() => setSelectedPhase(phase as Phase)}
              >
                Phase {phase}
              </button>
            ))}
          </div>
          <p className="mt-4 type-caption text-text-secondary">~ {formatDate(phaseEndDates[selectedPhase])}</p>
          <div className="mt-4 grid gap-4">
            {fallbackActions.map(({ action, dueDate }) => (
              <ActionItem
                key={action.action_id}
                status={completedIds.has(action.action_id) ? 'complete' : 'incomplete'}
                actionName={action.title}
                description={`${action.description}${dueDate ? ` · 기한 ${formatDate(dueDate)}` : ''}`}
                reason={action.reason}
                aria-label={`${action.title} 완료 상태 변경`}
                onStatusChange={(status) => handleStatusChange(action.action_id, status)}
              />
            ))}
          </div>
        </section>
        <section className="min-w-0 overflow-hidden rounded-card border border-border-subtle bg-background-surface p-6">
          <h2 className="type-title text-text-primary">나에게 맞는 지원</h2>
          <div className="mt-4 grid gap-4">
            {plan.matched_policies.slice(0, 4).map((policy) => (
              <PolicyCard
                key={policy.policy_id}
                title={policy.title}
                status={POLICY_BADGE_STATUS[policy.eligibility_status]}
                statusLabel={STATUS_LABELS[policy.eligibility_status]}
                description={getPolicyDescription(policy)}
                href={policy.source_url}
              />
            ))}
          </div>
        </section>
      </div>
    </PageShell>
  )
}

function getChangeSummary(scenario: ScenarioOption, snapshot: PlanSnapshot) {
  if (typeof scenario.changes.desired_deposit === 'number') return { label: '보증금', beforeValue: formatCompactWon(snapshot.target.desired_deposit), afterValue: formatCompactWon(scenario.changes.desired_deposit) }
  if (typeof scenario.changes.desired_monthly_rent === 'number') return { label: '월세', beforeValue: formatCompactWon(snapshot.target.desired_monthly_rent), afterValue: formatCompactWon(scenario.changes.desired_monthly_rent) }
  if (typeof scenario.changes.monthly_savings === 'number') {
    const cfBefore = scenario.changed_fields?.monthly_savings?.before
    return { label: '월 저축액', beforeValue: typeof cfBefore === 'number' ? formatCompactWon(cfBefore) : '-', afterValue: formatCompactWon(scenario.changes.monthly_savings) }
  }
  if (scenario.changes.planned_move_in_date) return { label: '독립 시점', beforeValue: formatMonth(snapshot.target.planned_move_in_date), afterValue: formatMonth(scenario.changes.planned_move_in_date) }
  return { label: '변경 조건', beforeValue: '현재 조건', afterValue: scenario.title }
}

function buildScenarioRequest(plan: PlanSnapshot, priority: ScenarioPriority) {
  return {
    user_id: plan.user_id,
    target_id: plan.target_id,
    previous_diagnosis_id: plan.diagnosis_id,
    previous_plan_id: plan.plan_id,
    priority,
    constraints: {
      minimum_desired_deposit: Math.max(plan.target.desired_deposit - 20000000, 0),
      max_additional_monthly_savings: 500000,
      max_move_delay_months: 6,
    },
  }
}

function ChangedFieldsSummary({ replanResult, showDetails = true }: { replanResult: ReplanResponse; showDetails?: boolean }) {
  const changedEntries = Object.entries(replanResult.changed_fields)

  return (
    <section className="rounded-card border border-border-subtle bg-background-surface p-6">
      <p className="type-label text-action-primary">요약</p>
      <p className="mt-2 type-heading text-text-primary">{replanResult.current.action_plan.summary}</p>
      {showDetails && (
        <div className="mt-5 grid gap-3">
          <div className="rounded-card bg-background-surface p-5 shadow-card">
            <p className="type-caption text-text-secondary">변경 조건</p>
            <ul className="mt-2 grid gap-1 type-body text-text-primary">
              {changedEntries.length === 0 ? <li>변경 없음</li> : changedEntries.map(([field, change]) => (
                <li key={field}>{field}: {String(change.before)} → {String(change.after)}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  )
}

function AiSimulatorPage({
  plan,
  scenarioResult,
  latestReplan,
  isPending,
  onCompare,
  onApply,
}: {
  plan: PlanResponse | null
  scenarioResult: ScenarioResponse | null
  latestReplan: ReplanResponse | null
  isPending: boolean
  onCompare: () => void
  onApply: (scenario: ScenarioOption) => void
}) {
  if (!plan) return <PlanGuard />

  return (
    <PageShell>
      <PageHeader title="AI 독립 조건 시뮬레이터" description="현재 계획을 바탕으로 현실적인 대안을 비교해보세요." />
      {latestReplan ? (
        <ChangedFieldsSummary replanResult={latestReplan} showDetails={false} />
      ) : (
        <section className="rounded-card border border-border-subtle bg-background-surface p-6">
          <p className="type-label text-action-primary">요약</p>
          <p className="mt-2 type-heading text-text-primary">{plan.action_plan.summary}</p>
        </section>
      )}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="type-title text-text-primary">추천 시나리오</h2>
          <p className="mt-2 type-body text-text-secondary">카드를 선택하면 계획 수정 단계로 이어져요.</p>
        </div>
        <Button disabled={isPending} onClick={onCompare}>
          {scenarioResult ? '시나리오 다시 비교' : 'AI 대안 비교하기'}
        </Button>
      </div>
      {scenarioResult && (
        <div className="grid gap-5 lg:grid-cols-3">
          {scenarioResult.scenarios.map((scenario) => {
            const change = getChangeSummary(scenario, plan)
            return (
              <AiScenarioCard
                key={scenario.scenario_id}
                title={scenario.title}
                changedConditionLabel={change.label}
                beforeValue={change.beforeValue}
                afterValue={change.afterValue}
                metrics={[
                  { label: '준비도', value: `${plan.diagnosis.readiness_score} → ${scenario.diagnosis.readiness_score}` },
                  { label: '독립 시점', value: scenario.changes.planned_move_in_date ? `${formatMonth(plan.target.planned_move_in_date)} → ${formatMonth(scenario.changes.planned_move_in_date)}` : `${scenario.diagnosis.estimated_months ?? '-'}개월` },
                ]}
                details={[
                  { label: '필요 월 저축액', value: formatCompactWon(scenario.diagnosis.required_monthly_saving) },
                  ...(scenario.policy_changes[0] ? [{ label: '지원정책', value: `${STATUS_LABELS[scenario.policy_changes[0].after_status]} 유지` }] : []),
                ]}
                aiReason={scenario.ai_reason}
                tradeoff={scenario.tradeoff}
                ctaProps={{ disabled: isPending, onClick: () => onApply(scenario) }}
              />
            )
          })}
        </div>
      )}
    </PageShell>
  )
}

function ReplanPage({
  plan,
  latestReplan,
  isPending,
  error,
  onSubmit,
}: {
  plan: PlanResponse | null
  latestReplan: ReplanResponse | null
  isPending: boolean
  error?: Error | null
  onSubmit: (changes: ReplanChanges) => void
}) {
  const [draft, setDraft] = useState<Record<string, string>>({})
  if (!plan) return <PlanGuard />

  const update = (field: string, value: string) => setDraft((state) => ({ ...state, [field]: value }))
  const handleSubmit = () => {
    const changes: ReplanChanges = {}
    if (draft.planned_move_in_date) changes.planned_move_in_date = draft.planned_move_in_date
    if (draft.desired_region) changes.desired_region = draft.desired_region as Region
    if (draft.desired_deposit) changes.desired_deposit = Number(draft.desired_deposit)
    if (draft.desired_monthly_rent) changes.desired_monthly_rent = Number(draft.desired_monthly_rent)
    if (draft.desired_housing_type) changes.desired_housing_type = draft.desired_housing_type as HousingType
    if (draft.monthly_savings) changes.monthly_savings = Number(draft.monthly_savings)
    onSubmit(changes)
  }

  return (
    <PageShell>
      <PageHeader eyebrow="Re-Plan" title="독립 목표를 수정해주세요" description="조건을 수정하면 필요한 준비 계획을 다시 계산합니다." />
      <FormCard title="독립 희망 조건" description="수정하지 않은 값은 기존 설정값으로 반영됩니다.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <TextInputField label="독립 예정일" helper={`현재: ${plan.target.planned_move_in_date}`} type="date" value={draft.planned_move_in_date ?? ''} placeholder={plan.target.planned_move_in_date} onChange={(value) => update('planned_move_in_date', value)} />
          <SelectInputField label="희망 거주 지역" helper="시·도 기준으로 선택해주세요." value={(draft.desired_region as Region) ?? ''} placeholder={`현재: ${getOptionLabel(REGION_OPTIONS, plan.target.desired_region)}`} options={REGION_OPTIONS} onChange={(value) => update('desired_region', value)} />
          <TextInputField label="희망 보증금" helper="감당 가능한 보증금 범위를 입력해주세요." type="number" min={0} value={draft.desired_deposit ?? ''} placeholder={formatWon(plan.target.desired_deposit)} onChange={(value) => update('desired_deposit', value)} />
          <TextInputField label="희망 월세" helper="관리비를 제외한 월세를 입력해주세요." type="number" min={0} value={draft.desired_monthly_rent ?? ''} placeholder={formatWon(plan.target.desired_monthly_rent)} onChange={(value) => update('desired_monthly_rent', value)} />
          <SelectInputField label="희망 주거 형태" helper="월세·전세를 선택해주세요." value={(draft.desired_housing_type as HousingType) ?? ''} placeholder={`현재: ${getOptionLabel(HOUSING_TYPE_OPTIONS, plan.target.desired_housing_type)}`} options={HOUSING_TYPE_OPTIONS} onChange={(value) => update('desired_housing_type', value)} />
          <TextInputField label="월 저축액" helper="수정하지 않으면 기존 월 저축액을 유지합니다." type="number" min={0} value={draft.monthly_savings ?? ''} placeholder={formatWon(plan.diagnosis.required_monthly_saving)} onChange={(value) => update('monthly_savings', value)} />
        </div>
      </FormCard>
      <div className="flex justify-end">
        <Button className="w-60" disabled={isPending} onClick={handleSubmit}>내 독립 플랜 다시 만들기</Button>
      </div>
      {error && <p className="rounded-control bg-status-danger-background p-4 type-body text-status-danger">{error.message}</p>}
      {latestReplan && <ChangedFieldsSummary replanResult={latestReplan} />}
    </PageShell>
  )
}

function AppRoutes() {
  const navigate = useNavigate()
  const { draft } = usePlanStore()
  const [inputStep, setInputStep] = useState<1 | 2>(1)
  const [currentPlan, setCurrentPlan] = useState<PlanResponse | null>(null)
  const [scenarioResult, setScenarioResult] = useState<ScenarioResponse | null>(null)
  const [latestAiReplan, setLatestAiReplan] = useState<ReplanResponse | null>(null)
  const [latestManualReplan, setLatestManualReplan] = useState<ReplanResponse | null>(null)
  const [goalPriority] = useState<ScenarioPriority>('LOW_MONTHLY_BURDEN')

  const createMutation = useMutation({
    mutationFn: createPlan,
    onSuccess: (plan) => {
      setCurrentPlan(plan)
      setLatestAiReplan(null)
      setLatestManualReplan(null)
      navigate('/')
    },
  })

  const scenarioMutation = useMutation({
    mutationFn: compareScenarios,
    onSuccess: setScenarioResult,
  })

  const aiReplanMutation = useMutation({
    mutationFn: replan,
    onSuccess: (result) => {
      setLatestAiReplan(result)
      setCurrentPlan(result.current)
    },
  })

  const manualReplanMutation = useMutation({
    mutationFn: replan,
    onSuccess: (result) => {
      setLatestManualReplan(result)
      setCurrentPlan(result.current)
    },
  })

  const handleCreatePlan = () => createMutation.mutate(toPlanRequest(draft))
  const handleCompare = () => {
    if (!currentPlan) return
    scenarioMutation.mutate(buildScenarioRequest(currentPlan, goalPriority))
  }
  const handleApplyScenario = (scenario: ScenarioOption) => {
    if (!currentPlan) return
    aiReplanMutation.mutate({
      user_id: currentPlan.user_id,
      target_id: currentPlan.target_id,
      previous_diagnosis_id: currentPlan.diagnosis_id,
      previous_plan_id: currentPlan.plan_id,
      changes: scenario.changes,
    })
  }
  const handleReplanSubmit = (changes: ReplanChanges) => {
    if (!currentPlan) return
    manualReplanMutation.mutate({
      user_id: currentPlan.user_id,
      target_id: currentPlan.target_id,
      previous_diagnosis_id: currentPlan.diagnosis_id,
      previous_plan_id: currentPlan.plan_id,
      changes,
    })
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          currentPlan ? (
            <PlanDashboard plan={currentPlan} />
          ) : inputStep === 1 ? (
            <InputStepOne onNext={() => setInputStep(2)} />
          ) : (
            <InputStepTwo
              onBack={() => setInputStep(1)}
              onCreate={handleCreatePlan}
              isPending={createMutation.isPending}
              error={createMutation.error}
            />
          )
        }
      />
      <Route
        path="/simulator"
        element={
          <AiSimulatorPage
            plan={currentPlan}
            scenarioResult={scenarioResult}
            latestReplan={latestAiReplan}
            isPending={scenarioMutation.isPending || aiReplanMutation.isPending}
            onCompare={handleCompare}
            onApply={handleApplyScenario}
          />
        }
      />
      <Route
        path="/replan"
        element={
          <ReplanPage
            plan={currentPlan}
            latestReplan={latestManualReplan}
            isPending={manualReplanMutation.isPending}
            error={manualReplanMutation.error}
            onSubmit={handleReplanSubmit}
          />
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  const isUiPreview = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('preview') === 'ui'
  return isUiPreview ? <UiPreview /> : <AppRoutes />
}
