import { create } from 'zustand'
import type { EmploymentStatus, HousingType, PlanRequest } from '../types/api'

export interface PlanDraft {
  age: number
  employment_status: EmploymentStatus
  region: string
  monthly_income: number
  current_savings: number
  current_emergency_fund: number
  monthly_saving: number
  target_date: string
  deposit_budget: number
  monthly_rent_budget: number
  housing_type: HousingType
}

const initialDraft: PlanDraft = {
  age: 24,
  employment_status: 'EMPLOYED',
  region: '경기도',
  monthly_income: 2500000,
  current_savings: 5000000,
  current_emergency_fund: 1000000,
  monthly_saving: 500000,
  target_date: '2027-01-12',
  deposit_budget: 5000000,
  monthly_rent_budget: 500000,
  housing_type: 'MONTHLY_RENT',
}

interface PlanStore {
  draft: PlanDraft
  setDraft: (draft: Partial<PlanDraft>) => void
}

export const usePlanStore = create<PlanStore>((set) => ({
  draft: initialDraft,
  setDraft: (draft) => set((state) => ({ draft: { ...state.draft, ...draft } })),
}))

export function toPlanRequest(draft: PlanDraft): PlanRequest {
  return {
    user: {
      age: draft.age,
      employment_status: draft.employment_status,
      region: draft.region,
      monthly_income: draft.monthly_income,
      current_savings: draft.current_savings,
      current_emergency_fund: draft.current_emergency_fund,
      monthly_saving: draft.monthly_saving,
    },
    target: {
      target_date: draft.target_date,
      monthly_rent_budget: draft.monthly_rent_budget,
      deposit_budget: draft.deposit_budget,
      housing_type: draft.housing_type,
    },
  }
}
