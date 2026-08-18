import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { compareScenarios, createPlan, replan } from './api/plan.api'
import UiPreview from './previews/UiPreview'
import { toPlanRequest, usePlanStore } from './stores/plan-store'
import type { PlanDraft } from './stores/plan-store'
import type {
  EmploymentStatus,
  EligibilityStatus,
  HousingStatus,
  HousingType,
  MaritalStatus,
  PlanSnapshot,
  Region,
  ScenarioOption,
  ScenarioPriority,
  ScenarioResponse,
} from './types/api'

const REGION_OPTIONS: Array<{ value: Region; label: string }> = [
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

const STATUS_LABELS: Record<EligibilityStatus, string> = {
  AVAILABLE: '신청 가능',
  CONDITIONAL: '조건 조정 필요',
  NEED_MORE_INFO: '추가 확인 필요',
  NOT_ELIGIBLE: '현재 대상 아님',
}

const SCENARIO_PRIORITY_LABELS: Record<ScenarioPriority, string> = {
  FAST_MOVE: '빠른 독립',
  LOW_MONTHLY_BURDEN: '월 부담 최소화',
  POLICY_BENEFIT: '정책 활용 우선',
}

function formatWon(value: number) {
  return value.toLocaleString('ko-KR') + '원'
}

function PlanSummary({ snapshot }: { snapshot: PlanSnapshot }) {
  return (
    <section className="space-y-4 rounded-2xl border border-border-default bg-background-surface p-6">
      <div>
        <p className="text-sm text-text-secondary">독립 준비도</p>
        <p className="text-4xl font-bold text-text-primary">{snapshot.diagnosis.readiness_score}점</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-background-surface-subtle p-4">
          <p className="text-xs text-text-secondary">부족 초기자금</p>
          <p className="font-semibold">{formatWon(snapshot.diagnosis.initial_fund_gap)}</p>
        </div>
        <div className="rounded-xl bg-background-surface-subtle p-4">
          <p className="text-xs text-text-secondary">필요 월 저축액</p>
          <p className="font-semibold">{formatWon(snapshot.diagnosis.required_monthly_saving)}</p>
        </div>
        <div className="rounded-xl bg-background-surface-subtle p-4">
          <p className="text-xs text-text-secondary">예상 준비기간</p>
          <p className="font-semibold">
            {snapshot.diagnosis.estimated_months === null
              ? '현재 저축액으로 계산 불가'
              : `${snapshot.diagnosis.estimated_months}개월`}
          </p>
        </div>
      </div>
      <div>
        <h2 className="mb-2 text-lg font-semibold">맞춤 정책</h2>
        <ul className="space-y-2">
          {snapshot.matched_policies.map((policy) => (
            <li key={policy.policy_id} className="rounded-xl border border-border-default bg-background-control p-3">
              <div className="flex min-w-0 items-center justify-between gap-3">
                <span className="min-w-0 break-words font-medium">{policy.title}</span>
                <span className="shrink-0 text-sm font-semibold text-action-primary">
                  {STATUS_LABELS[policy.eligibility_status]}
                </span>
              </div>
              <p className="mt-1 text-xs text-text-secondary">{policy.eligibility_text}</p>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h2 className="mb-2 text-lg font-semibold">AI Action Plan</h2>
        <p className="mb-3 text-sm text-text-secondary">{snapshot.action_plan.summary}</p>
        <ol className="space-y-2">
          {snapshot.action_plan.actions.map((action) => (
            <li key={action.action_id} className="rounded-xl bg-background-surface-subtle p-3">
              <p className="font-medium">{action.priority}. {action.title}</p>
              <p className="mt-1 text-sm text-text-secondary">{action.description}</p>
              <p className="mt-1 text-xs text-text-secondary">추천 이유: {action.reason}</p>
              {action.due_date && <p className="mt-1 text-xs font-semibold text-action-primary">기한: {action.due_date}</p>}
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}

function ScenarioComparison({
  result,
  isPending,
  onApply,
}: {
  result: ScenarioResponse
  isPending: boolean
  onApply: (scenario: ScenarioOption) => void
}) {
  return (
    <section className="space-y-4 rounded-2xl border border-border-default bg-background-surface p-6">
      <div>
        <p className="text-sm font-semibold text-action-primary">AI 조건 시뮬레이터</p>
        <h2 className="mt-1 text-xl font-bold">독립 조건 대안 비교</h2>
        <p className="mt-2 text-sm text-text-secondary">{result.summary}</p>
      </div>
      <div className="grid gap-3">
        {result.scenarios.map((scenario) => {
          const isRecommended = scenario.scenario_id === result.recommended_scenario_id
          return (
            <article
              key={scenario.scenario_id}
              className={`rounded-xl border p-4 ${isRecommended ? 'border-action-primary bg-action-subtle' : 'border-border-default bg-background-control'}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  {isRecommended && <p className="text-xs font-bold text-action-primary">AI 추천</p>}
                  <h3 className="font-semibold">{scenario.title}</h3>
                </div>
                <span className="rounded-full bg-background-surface px-3 py-1 text-sm font-bold text-action-primary">
                  {scenario.recommendation_score}점
                </span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                <p>준비도 <strong>{scenario.diagnosis.readiness_score}점</strong></p>
                <p>필요 월 저축 <strong>{formatWon(scenario.diagnosis.required_monthly_saving)}</strong></p>
              </div>
              {scenario.policy_changes.length > 0 && (
                <ul className="mt-3 space-y-1 text-xs text-action-primary">
                  {scenario.policy_changes.map((change) => (
                    <li key={change.policy_id}>
                      {change.title}: {STATUS_LABELS[change.before_status]} → {STATUS_LABELS[change.after_status]}
                    </li>
                  ))}
                </ul>
              )}
              <p className="mt-3 text-sm text-text-secondary">{scenario.ai_reason}</p>
              <p className="mt-2 text-xs text-text-secondary">고려할 점: {scenario.tradeoff}</p>
              <button
                className="mt-3 w-full rounded-lg border border-action-primary px-3 py-2 text-sm font-semibold text-action-primary hover:bg-background-surface disabled:border-disabled-border disabled:text-disabled-text"
                disabled={isPending}
                onClick={() => onApply(scenario)}
              >
                이 조건으로 재계획
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function PlanDemo() {
  const { draft, setDraft } = usePlanStore()
  const [goalPriority, setGoalPriority] = useState<ScenarioPriority>('LOW_MONTHLY_BURDEN')
  const planMutation = useMutation({ mutationFn: createPlan })
  const replanMutation = useMutation({ mutationFn: replan })
  const scenarioMutation = useMutation({ mutationFn: compareScenarios })
  const snapshot = replanMutation.data?.current ?? planMutation.data
  const latestPlan = replanMutation.data
    ? {
        user_id: replanMutation.data.user_id,
        target_id: replanMutation.data.target_id,
        diagnosis_id: replanMutation.data.current.diagnosis_id,
        plan_id: replanMutation.data.current.plan_id,
      }
    : planMutation.data
  const isPending = planMutation.isPending || replanMutation.isPending || scenarioMutation.isPending
  const error = planMutation.error ?? replanMutation.error ?? scenarioMutation.error

  const updateNumber = (
    field:
      | 'age'
      | 'youth_household_monthly_income'
      | 'youth_household_size'
      | 'personal_monthly_income'
      | 'total_assets'
      | 'monthly_savings'
      | 'desired_deposit'
      | 'desired_monthly_rent',
    value: string,
  ) => {
    setDraft({ [field]: Number(value) } as Partial<PlanDraft>)
  }

  const handleCreatePlan = () => {
    replanMutation.reset()
    scenarioMutation.reset()
    planMutation.mutate(toPlanRequest(draft))
  }

  const handleCompareScenarios = () => {
    if (!latestPlan) return
    const currentDeposit = snapshot?.target.desired_deposit ?? draft.desired_deposit
    scenarioMutation.mutate({
      user_id: latestPlan.user_id,
      target_id: latestPlan.target_id,
      previous_diagnosis_id: latestPlan.diagnosis_id,
      previous_plan_id: latestPlan.plan_id,
      priority: goalPriority,
      constraints: {
        minimum_desired_deposit: Math.max(currentDeposit - 20000000, 0),
        max_additional_monthly_savings: 500000,
        max_move_delay_months: 6,
      },
    })
  }

  const handleApplyScenario = (scenario: ScenarioOption) => {
    if (!latestPlan) return
    replanMutation.mutate({
      user_id: latestPlan.user_id,
      target_id: latestPlan.target_id,
      previous_diagnosis_id: latestPlan.diagnosis_id,
      previous_plan_id: latestPlan.plan_id,
      changes: scenario.changes,
    }, {
      onSuccess: () => scenarioMutation.reset(),
    })
  }

  return (
    <main className="min-h-screen bg-background-page px-4 py-10 text-text-primary">
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[360px_1fr]">
        <section className="rounded-2xl bg-background-surface p-6 shadow-sm">
          <p className="text-sm font-semibold text-action-primary">StepHome · 2morrow</p>
          <h1 className="mt-2 text-2xl font-bold">첫 독립 계획 만들기</h1>
          <p className="mt-2 text-sm text-text-secondary">현재 상황을 진단하고 이용 가능한 정책과 실행 순서를 안내합니다.</p>
          <div className="mt-6 space-y-3">
            <label className="block text-sm">나이<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.age} onChange={(event) => updateNumber('age', event.target.value)} /></label>
            <label className="block text-sm">취업 상태<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.employment_status} onChange={(event) => setDraft({ employment_status: event.target.value as EmploymentStatus })}><option value="JOB_SEEKER">취업 준비 중</option><option value="EMPLOYED">재직 중</option><option value="STUDENT">학생</option><option value="OTHER">기타</option></select></label>
            <label className="block text-sm">혼인 상태<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.marital_status} onChange={(event) => setDraft({ marital_status: event.target.value as MaritalStatus })}><option value="UNMARRIED">미혼</option><option value="MARRIED">기혼</option></select></label>
            <label className="block text-sm">현재 지역<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.current_region} onChange={(event) => setDraft({ current_region: event.target.value as Region })}>{REGION_OPTIONS.map((region) => <option key={region.value} value={region.value}>{region.label}</option>)}</select></label>
            <label className="block text-sm">개인 월 소득<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.personal_monthly_income} onChange={(event) => updateNumber('personal_monthly_income', event.target.value)} /></label>
            <label className="block text-sm">청년가구 월 소득<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.youth_household_monthly_income} onChange={(event) => updateNumber('youth_household_monthly_income', event.target.value)} /></label>
            <label className="block text-sm">청년가구원 수<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="1" value={draft.youth_household_size} onChange={(event) => updateNumber('youth_household_size', event.target.value)} /></label>
            <label className="block text-sm">총자산<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.total_assets} onChange={(event) => updateNumber('total_assets', event.target.value)} /></label>
            <label className="block text-sm">월 저축액<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.monthly_savings} onChange={(event) => updateNumber('monthly_savings', event.target.value)} /></label>
            <label className="block text-sm">주택 보유 여부<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.housing_status} onChange={(event) => setDraft({ housing_status: event.target.value as HousingStatus })}><option value="NO_HOME">무주택</option><option value="HAS_HOME">주택 보유</option></select></label>
            <label className="block text-sm">독립 예정일<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="date" value={draft.planned_move_in_date} onChange={(event) => setDraft({ planned_move_in_date: event.target.value })} /></label>
            <label className="block text-sm">희망 지역<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.desired_region} onChange={(event) => setDraft({ desired_region: event.target.value as Region })}>{REGION_OPTIONS.map((region) => <option key={region.value} value={region.value}>{region.label}</option>)}</select></label>
            <label className="block text-sm">희망 보증금<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.desired_deposit} onChange={(event) => updateNumber('desired_deposit', event.target.value)} /></label>
            <label className="block text-sm">희망 월세<input className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" type="number" min="0" value={draft.desired_monthly_rent} onChange={(event) => updateNumber('desired_monthly_rent', event.target.value)} /></label>
            <label className="block text-sm">희망 주거 형태<select className="mt-1 w-full rounded-lg border border-border-interactive bg-background-control p-2" value={draft.desired_housing_type} onChange={(event) => setDraft({ desired_housing_type: event.target.value as HousingType })}><option value="MONTHLY_RENT">월세</option><option value="JEONSE">전세</option></select></label>
          </div>
          <div className="mt-5 grid gap-2">
            <button className="rounded-lg border border-transparent bg-action-primary px-4 py-3 font-semibold text-action-on-primary hover:bg-action-hover disabled:bg-disabled-background" disabled={isPending} onClick={handleCreatePlan}>내 독립 계획 만들기</button>
            {latestPlan && (
              <div className="grid gap-2 rounded-xl border border-border-default bg-background-control p-3">
                <label className="text-sm font-medium">
                  시나리오 추천 기준
                  <select
                    className="mt-1 w-full rounded-lg border border-border-interactive bg-background-surface p-2"
                    value={goalPriority}
                    onChange={(event) => setGoalPriority(event.target.value as ScenarioPriority)}
                  >
                    {Object.entries(SCENARIO_PRIORITY_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </label>
                <button
                  className="rounded-lg border border-action-subtle bg-background-surface px-4 py-3 font-semibold text-action-primary hover:bg-action-subtle disabled:bg-disabled-background"
                  disabled={isPending}
                  onClick={handleCompareScenarios}
                >
                  AI 대안 3개 비교
                </button>
              </div>
            )}
          </div>
          {isPending && <p className="mt-3 text-sm text-text-secondary">맞춤 계획을 생성하고 있습니다...</p>}
          {error && <p className="mt-3 rounded-lg bg-status-danger-background p-3 text-sm text-status-danger">{error.message}</p>}
        </section>
        {snapshot ? (
          <div className="space-y-6">
            <PlanSummary snapshot={snapshot} />
            {scenarioMutation.data && (
              <ScenarioComparison
                result={scenarioMutation.data}
                isPending={isPending}
                onApply={handleApplyScenario}
              />
            )}
          </div>
        ) : <section className="flex min-h-96 items-center justify-center rounded-2xl border border-dashed border-border-interactive bg-background-surface p-6 text-center text-text-secondary">입력 후 StepHome 계획을 생성하세요.</section>}
      </div>
    </main>
  )
}

export default function App() {
  const isUiPreview = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('preview') === 'ui'

  return isUiPreview ? <UiPreview /> : <PlanDemo />
}
