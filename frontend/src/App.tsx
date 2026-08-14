import { useMutation } from '@tanstack/react-query'
import { createPlan, replan } from './api/plan.api'
import { toPlanRequest, usePlanStore } from './stores/plan-store'
import type { PlanDraft } from './stores/plan-store'
import type { EmploymentStatus, PlanSnapshot } from './types/api'

function formatWon(value: number) {
  return value.toLocaleString('ko-KR') + '원'
}

function PlanSummary({ snapshot }: { snapshot: PlanSnapshot }) {
  return (
    <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6">
      <div>
        <p className="text-sm text-slate-500">독립 준비도</p>
        <p className="text-4xl font-bold text-slate-900">{snapshot.diagnosis.readiness_score}점</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">부족 초기자금</p>
          <p className="font-semibold">{formatWon(snapshot.diagnosis.initial_fund_gap)}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">필요 월 저축액</p>
          <p className="font-semibold">{formatWon(snapshot.diagnosis.required_monthly_saving)}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">예상 준비기간</p>
          <p className="font-semibold">{snapshot.diagnosis.estimated_months}개월</p>
        </div>
      </div>
      <div>
        <h2 className="mb-2 text-lg font-semibold">정책</h2>
        <ul className="space-y-2">
          {snapshot.matched_policies.map((policy) => (
            <li key={policy.policy_id} className="flex items-center justify-between rounded-xl border p-3">
              <span>{policy.title}</span>
              <span className="text-sm font-semibold">{policy.eligibility_status}</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h2 className="mb-2 text-lg font-semibold">Action Plan</h2>
        <p className="mb-3 text-sm text-slate-600">{snapshot.action_plan.summary}</p>
        <ol className="space-y-2">
          {snapshot.action_plan.actions.map((action) => (
            <li key={action.action_id} className="rounded-xl bg-slate-50 p-3">
              <p className="font-medium">{action.title}</p>
              <p className="text-sm text-slate-600">{action.description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}

export default function App() {
  const { draft, setDraft } = usePlanStore()
  const planMutation = useMutation({ mutationFn: createPlan })
  const replanMutation = useMutation({ mutationFn: replan })
  const snapshot = replanMutation.data?.current ?? planMutation.data
  const isPending = planMutation.isPending || replanMutation.isPending
  const error = planMutation.error ?? replanMutation.error

  const updateNumber = (
    field:
      | 'age'
      | 'monthly_income'
      | 'current_savings'
      | 'current_emergency_fund'
      | 'monthly_saving'
      | 'deposit_budget'
      | 'monthly_rent_budget',
    value: string,
  ) => {
    setDraft({ [field]: Number(value) } as Partial<PlanDraft>)
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10 text-slate-900">
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[360px_1fr]">
        <section className="rounded-2xl bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold text-indigo-600">StepHome · 2morrow</p>
          <h1 className="mt-2 text-2xl font-bold">첫 독립 계획 만들기</h1>
          <p className="mt-2 text-sm text-slate-500">P0 입력값만 사용해 준비도와 정책을 확인합니다.</p>
          <div className="mt-6 space-y-3">
            <label className="block text-sm">나이<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.age} onChange={(event) => updateNumber('age', event.target.value)} /></label>
            <label className="block text-sm">취업 상태<select className="mt-1 w-full rounded-lg border p-2" value={draft.employment_status} onChange={(event) => setDraft({ employment_status: event.target.value as EmploymentStatus })}><option value="JOB_SEEKER">취업 준비 중</option><option value="EMPLOYED">재직 중</option><option value="STUDENT">대학생</option><option value="OTHER">기타</option></select></label>
            <label className="block text-sm">현재 지역<input className="mt-1 w-full rounded-lg border p-2" value={draft.region} onChange={(event) => setDraft({ region: event.target.value })} /></label>
            <label className="block text-sm">월 소득<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.monthly_income} onChange={(event) => updateNumber('monthly_income', event.target.value)} /></label>
            <label className="block text-sm">현재 보유자금<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.current_savings} onChange={(event) => updateNumber('current_savings', event.target.value)} /></label>
            <label className="block text-sm">현재 비상자금<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.current_emergency_fund} onChange={(event) => updateNumber('current_emergency_fund', event.target.value)} /></label>
            <label className="block text-sm">월 저축액<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.monthly_saving} onChange={(event) => updateNumber('monthly_saving', event.target.value)} /></label>
            <label className="block text-sm">독립 예정일<input className="mt-1 w-full rounded-lg border p-2" type="date" value={draft.target_date} onChange={(event) => setDraft({ target_date: event.target.value })} /></label>
            <label className="block text-sm">보증금<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.deposit_budget} onChange={(event) => updateNumber('deposit_budget', event.target.value)} /></label>
            <label className="block text-sm">월세 예산<input className="mt-1 w-full rounded-lg border p-2" type="number" value={draft.monthly_rent_budget} onChange={(event) => updateNumber('monthly_rent_budget', event.target.value)} /></label>
            <label className="block text-sm">주거 형태<select className="mt-1 w-full rounded-lg border p-2" value={draft.housing_type} onChange={(event) => setDraft({ housing_type: event.target.value as 'MONTHLY_RENT' | 'JEONSE' })}><option value="MONTHLY_RENT">월세</option><option value="JEONSE">전세</option></select></label>
          </div>
          <div className="mt-5 grid gap-2">
            <button className="rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white disabled:opacity-50" disabled={isPending} onClick={() => planMutation.mutate(toPlanRequest(draft))}>내 독립 계획 만들기</button>
            {snapshot && <button className="rounded-lg border border-indigo-200 px-4 py-3 font-semibold text-indigo-700 disabled:opacity-50" disabled={isPending} onClick={() => replanMutation.mutate({ user_id: snapshot.user_id, target_id: snapshot.target_id, previous_diagnosis_id: snapshot.diagnosis_id, previous_plan_id: snapshot.plan_id, changes: { deposit_budget: 4000000 } })}>보증금 400만원으로 재계획</button>}
          </div>
          {isPending && <p className="mt-3 text-sm text-slate-500">분석 중입니다...</p>}
          {error && <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error.message}</p>}
        </section>
        {snapshot ? <PlanSummary snapshot={snapshot} /> : <section className="flex min-h-96 items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-center text-slate-500">입력 후 StepHome 계획을 생성하세요.</section>}
      </div>
    </main>
  )
}
