import { afterEach, describe, expect, it } from 'vitest'
import { useRoadmapProgressStore } from './plan-store'
import type { Action } from '../types/api'

function action(action_id: number, status: Action['status'] = 'TODO'): Action {
  return {
    action_id,
    plan_id: 42,
    user_id: 1,
    diagnosis_id: 1,
    phase: 1,
    priority: action_id,
    action_type: 'SAVING',
    timing: 'NOW',
    title: `액션 ${action_id}`,
    description: '',
    reason: '',
    status,
    policy_id: null,
    due_date: null,
    created_at: '2026-08-19T00:00:00+09:00',
  }
}

afterEach(() => {
  useRoadmapProgressStore.setState({ completedActionIdsByPlan: {} })
  localStorage.clear()
})

describe('useRoadmapProgressStore', () => {
  it('stores completed roadmap actions by plan id', () => {
    const store = useRoadmapProgressStore.getState()

    store.ensurePlanProgress(42, [action(1), action(2, 'DONE')])
    store.setActionCompleted(42, 1, true)

    expect(useRoadmapProgressStore.getState().completedActionIdsByPlan['42']).toEqual([2, 1])
  })

  it('keeps user changes when the same plan is opened again', () => {
    const store = useRoadmapProgressStore.getState()

    store.ensurePlanProgress(42, [action(1, 'DONE')])
    store.setActionCompleted(42, 1, false)
    store.ensurePlanProgress(42, [action(1, 'DONE')])

    expect(useRoadmapProgressStore.getState().completedActionIdsByPlan['42']).toEqual([])
  })
})
