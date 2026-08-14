export type EmploymentStatus = 'JOB_SEEKER' | 'EMPLOYED' | 'STUDENT' | 'OTHER'
export type HousingType = 'MONTHLY_RENT' | 'JEONSE'
export type EligibilityStatus = 'AVAILABLE' | 'CONDITIONAL' | 'NEED_MORE_INFO' | 'NOT_ELIGIBLE'
export type ActionType = 'SAVING' | 'POLICY' | 'HOUSING' | 'CONTRACT'
export type Timing = 'NOW' | 'PREPARE' | 'SEARCH_HOUSE' | 'BEFORE_CONTRACT'
export type ActionStatus = 'TODO' | 'IN_PROGRESS' | 'DONE'

export interface PlanRequest {
  user: {
    age: number
    employment_status: EmploymentStatus
    region: string
    monthly_income: number
    current_savings: number
    current_emergency_fund: number
    monthly_saving: number
  }
  target: {
    target_date: string
    monthly_rent_budget: number
    deposit_budget: number
    housing_type: HousingType
  }
}

export type TargetResponse = PlanRequest['target'] & {
  target_region: string
}

export interface Diagnosis {
  diagnosis_id: number
  user_id: number
  target_id: number
  readiness_score: number
  fund_score: number
  saving_score: number
  emergency_score: number
  required_initial_fund: number
  initial_fund_gap: number
  target_emergency_fund: number
  emergency_fund_gap: number
  required_monthly_saving: number
  estimated_months: number
  calculated_at: string
}

export interface PolicyMatch {
  match_id: number
  user_id: number
  diagnosis_id: number
  policy_id: number
  title: string
  eligibility_status: EligibilityStatus
  matched_conditions: string[]
  failed_conditions: string[]
  missing_conditions: string[]
  rank: number
  support_amount: number | null
  support_amount_text: string
  eligibility_text: string
  description: string
  application_start: string
  application_end: string
  region: string
  provider: string
  category: string
  source_url: string
  checked_at: string
  matched_at: string
}

export interface Action {
  action_id: number
  plan_id: number
  user_id: number
  diagnosis_id: number
  priority: number
  action_type: ActionType
  timing: Timing
  title: string
  description: string
  reason: string
  status: ActionStatus
  policy_id: number | null
  due_date: string | null
  created_at: string
}

export interface ActionPlan {
  summary: string
  actions: Action[]
}

export interface PlanSnapshot {
  user_id: number
  target_id: number
  diagnosis_id: number
  plan_id: number
  target: TargetResponse
  diagnosis: Diagnosis
  matched_policies: PolicyMatch[]
  action_plan: ActionPlan
}

export type PlanResponse = PlanSnapshot

export interface ReplanRequest {
  user_id: number
  target_id: number
  previous_diagnosis_id: number
  previous_plan_id: number
  changes: {
    deposit_budget?: number
  }
}

export interface ReplanResponse {
  user_id: number
  target_id: number
  previous: PlanSnapshot
  current: PlanSnapshot
  changed_fields: Record<string, { before: number; after: number }>
}

export interface ApiErrorResponse {
  error: {
    code: string
    message: string
    details?: Array<{ field: string; reason: string }>
  }
}
