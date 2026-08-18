export type EmploymentStatus = 'JOB_SEEKER' | 'EMPLOYED' | 'STUDENT' | 'OTHER'
export type HousingType = 'MONTHLY_RENT' | 'JEONSE'
export type HousingStatus = 'NO_HOME' | 'HAS_HOME'
export type MaritalStatus = 'UNMARRIED' | 'MARRIED'
export type Region =
  | 'NATIONAL'
  | 'SEOUL'
  | 'BUSAN'
  | 'DAEGU'
  | 'INCHEON'
  | 'GWANGJU'
  | 'DAEJEON'
  | 'ULSAN'
  | 'SEJONG'
  | 'GYEONGGI'
  | 'GANGWON'
  | 'CHUNGBUK'
  | 'CHUNGNAM'
  | 'JEONBUK'
  | 'JEONNAM'
  | 'GYEONGBUK'
  | 'GYEONGNAM'
  | 'JEJU'
export type EligibilityStatus = 'AVAILABLE' | 'CONDITIONAL' | 'NEED_MORE_INFO' | 'NOT_ELIGIBLE'
export type ActionType = 'SAVING' | 'POLICY' | 'HOUSING' | 'CONTRACT'
export type Timing = 'NOW' | 'PREPARE' | 'SEARCH_HOUSE' | 'BEFORE_CONTRACT'
export type ActionStatus = 'TODO' | 'IN_PROGRESS' | 'DONE'
export type PolicyCategory = 'LOAN' | 'RENT_SUPPORT' | 'PUBLIC_RENTAL'
export type SupportAmountUnit = 'MONTH' | 'YEAR' | 'TOTAL' | 'OTHER'
export type ApplicationPeriodType = 'FIXED' | 'ALWAYS_OPEN' | 'NOTICE_BASED' | 'UNKNOWN'
export type ScenarioPriority = 'FAST_MOVE' | 'LOW_MONTHLY_BURDEN' | 'POLICY_BENEFIT'
export type ScenarioId = 'LOWER_DEPOSIT' | 'DELAY_MOVE_IN' | 'INCREASE_SAVINGS'

export interface PlanRequest {
  user: {
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
  }
  target: {
    planned_move_in_date: string
    desired_region: Region
    desired_deposit: number
    desired_monthly_rent: number
    desired_housing_type: HousingType
  }
}

export type TargetResponse = PlanRequest['target'] & {
  target_id: number
  user_id: number
}

export interface Diagnosis {
  diagnosis_id: number
  user_id: number
  target_id: number
  readiness_score: number
  fund_score: number
  saving_score: number
  required_initial_fund: number
  initial_fund_gap: number
  required_monthly_saving: number
  estimated_months: number | null
  calculated_at: string
}

export interface PolicyConditionDetail {
  condition: string
  result: string
  current_value: unknown
  required_min: number | null
  required_max: number | null
  required_values: string[] | null
  message: string
}

export interface PolicyMatch {
  match_id: number | null
  user_id: number | null
  diagnosis_id: number | null
  policy_id: number
  title: string
  description: string
  policy_category: PolicyCategory
  policy_region: string
  policy_provider: string | null
  eligibility_status: EligibilityStatus
  matched_conditions: string[]
  failed_conditions: string[]
  missing_conditions: string[]
  condition_details: PolicyConditionDetail[]
  rank: number | null
  support_amount: number | null
  support_amount_unit: SupportAmountUnit
  support_amount_text: string
  eligibility_text: string
  application_start: string | null
  application_end: string | null
  application_period_type: ApplicationPeriodType
  source_url: string
  checked_at: string | null
  matched_at: string | null
}

export interface Action {
  action_id: number
  plan_id: number
  user_id: number
  diagnosis_id: number
  phase?: 1 | 2 | 3 | 4
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

export type ReplanChanges = Partial<PlanRequest['user'] & PlanRequest['target']>

export interface ReplanRequest {
  user_id: number
  target_id: number
  previous_diagnosis_id: number
  previous_plan_id: number
  changes: ReplanChanges
}

export interface ReplanResponse {
  user_id: number
  target_id: number
  previous: PlanSnapshot
  current: PlanSnapshot
  changed_fields: Record<string, { before: unknown; after: unknown }>
}

export interface ScenarioConstraints {
  minimum_desired_deposit?: number | null
  max_additional_monthly_savings?: number
  max_move_delay_months?: number
}

export interface ScenarioRequest {
  user_id: number
  target_id: number
  previous_diagnosis_id: number
  previous_plan_id: number
  priority: ScenarioPriority
  constraints?: ScenarioConstraints
}

export type ScenarioDiagnosis = Pick<
  Diagnosis,
  | 'readiness_score'
  | 'fund_score'
  | 'saving_score'
  | 'required_initial_fund'
  | 'initial_fund_gap'
  | 'required_monthly_saving'
  | 'estimated_months'
>

export interface PolicyStatusChange {
  policy_id: number
  title: string
  before_status: EligibilityStatus
  after_status: EligibilityStatus
}

export interface ScenarioOption {
  scenario_id: ScenarioId
  title: string
  changes: ReplanChanges
  diagnosis: ScenarioDiagnosis
  policy_changes: PolicyStatusChange[]
  recommendation_score: number
  ai_reason: string
  tradeoff: string
}

export interface ScenarioResponse {
  recommended_scenario_id: ScenarioId
  summary: string
  scenarios: ScenarioOption[]
}

export interface ApiErrorResponse {
  error: {
    code: string
    message: string
    details?: Array<{ field: string; reason: string }>
  }
}
