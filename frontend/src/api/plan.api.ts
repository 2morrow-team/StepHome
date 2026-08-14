import { fetchJson } from './fetcher'
import type { PlanRequest, PlanResponse, ReplanRequest, ReplanResponse } from '../types/api'

export function createPlan(request: PlanRequest) {
  return fetchJson<PlanResponse>('/api/v1/plan', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export function replan(request: ReplanRequest) {
  return fetchJson<ReplanResponse>('/api/v1/replan', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export function getHealth() {
  return fetchJson<{ status: string }>('/api/v1/health')
}
