import { create } from 'zustand'
import type {
  EmploymentStatus,
  HousingStatus,
  HousingType,
  MaritalStatus,
  PlanRequest,
  Region,
} from '../types/api'

export interface PlanDraft {
  age: number
  current_region: Region
  employment_status: EmploymentStatus
  marital_status: MaritalStatus
  youth_household_monthly_income: number
  youth_household_size: number
  personal_monthly_income: number
  total_assets: number
  monthly_savings: number
  housing_status: HousingStatus
  planned_move_in_date: string
  desired_region: Region
  desired_deposit: number
  desired_monthly_rent: number
  desired_housing_type: HousingType
}

const initialDraft: PlanDraft = {
  age: 25,
  current_region: 'SEOUL',
  employment_status: 'EMPLOYED',
  marital_status: 'UNMARRIED',
  youth_household_monthly_income: 2500000,
  youth_household_size: 1,
  personal_monthly_income: 2500000,
  total_assets: 30000000,
  monthly_savings: 500000,
  housing_status: 'NO_HOME',
  planned_move_in_date: '2027-03-01',
  desired_region: 'SEOUL',
  desired_deposit: 90000000,
  desired_monthly_rent: 500000,
  desired_housing_type: 'MONTHLY_RENT',
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
      current_region: draft.current_region,
      employment_status: draft.employment_status,
      marital_status: draft.marital_status,
      youth_household_monthly_income: draft.youth_household_monthly_income,
      youth_household_size: draft.youth_household_size,
      personal_monthly_income: draft.personal_monthly_income,
      total_assets: draft.total_assets,
      monthly_savings: draft.monthly_savings,
      housing_status: draft.housing_status,
    },
    target: {
      planned_move_in_date: draft.planned_move_in_date,
      desired_region: draft.desired_region,
      desired_deposit: draft.desired_deposit,
      desired_monthly_rent: draft.desired_monthly_rent,
      desired_housing_type: draft.desired_housing_type,
    },
  }
}
