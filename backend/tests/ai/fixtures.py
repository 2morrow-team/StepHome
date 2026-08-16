"""공통 테스트 픽스처 — 노션 Demo Persona 기준 (새 P0 필드 구조)"""

DIAGNOSIS = {
    "diagnosis_id": 1,
    "user_id": 1,
    "target_id": 1,
    "readiness_score": 77,
    "fund_score": 33.33,
    "saving_score": 30.0,
    "required_initial_fund": 6000000,
    "initial_fund_gap": 2000000,
    "required_monthly_saving": 500000,
    "estimated_months": 5,
}

POLICY_AVAILABLE = {
    "policy_id": 1,
    "title": "청년월세 지원사업",
    "eligibility_status": "AVAILABLE",
    "matched_conditions": ["AGE", "INCOME", "HOUSING_TYPE"],
    "failed_conditions": [],
    "missing_conditions": [],
    "rank": 1,
    "support_amount": 200000,
    "support_amount_text": "월 최대 20만원, 최대 24개월 지원",
    "application_start": "2026-03-30",
    "application_end": "2026-05-29",
    "application_period_type": "FIXED",
}

POLICY_CONDITIONAL = {
    "policy_id": 2,
    "title": "청년전세임대",
    "eligibility_status": "CONDITIONAL",
    "matched_conditions": ["AGE"],
    "failed_conditions": ["DEPOSIT_LIMIT"],
    "missing_conditions": [],
    "rank": 2,
    "support_amount": None,
    "support_amount_text": "조건 충족 시 지원",
    "application_start": None,
    "application_end": None,
    "application_period_type": "NOTICE_BASED",
}

POLICY_NEED_MORE_INFO = {
    "policy_id": 3,
    "title": "제주 청년 희망충전 월세 지원",
    "eligibility_status": "NEED_MORE_INFO",
    "matched_conditions": [],
    "failed_conditions": [],
    "missing_conditions": ["HOUSEHOLD_INCOME"],
    "rank": 3,
    "support_amount": 200000,
    "support_amount_text": "월 최대 20만원, 최대 12개월 지원",
    "application_start": None,
    "application_end": None,
    "application_period_type": "NOTICE_BASED",
}

POLICY_NOT_ELIGIBLE = {
    "policy_id": 4,
    "title": "청년전용 버팀목 전세자금대출",
    "eligibility_status": "NOT_ELIGIBLE",
    "matched_conditions": [],
    "failed_conditions": ["HOUSING_TYPE", "AGE"],
    "missing_conditions": [],
    "rank": 4,
    "support_amount": None,
    "support_amount_text": "전세자금 최대 1억 5천만원 대출",
    "application_start": None,
    "application_end": None,
    "application_period_type": "ALWAYS_OPEN",
}

AI_INPUT = {
    "user_id": 1,
    "target_id": 1,
    "diagnosis_id": 1,
    "user": {
        "age": 24,
        "current_region": "GYEONGGI",
        "employment_status": "EMPLOYED",
        "marital_status": "UNMARRIED",
        "youth_household_monthly_income": 3000000,
        "youth_household_size": 1,
        "personal_monthly_income": 2500000,
        "total_assets": 5000000,
        "monthly_savings": 500000,
        "housing_status": "NO_HOME",
    },
    "target": {
        "planned_move_in_date": "2027-01-12",
        "desired_region": "SEOUL",
        "desired_deposit": 5000000,
        "desired_monthly_rent": 500000,
        "desired_housing_type": "MONTHLY_RENT",
    },
    "diagnosis": DIAGNOSIS,
    "matched_policies": [POLICY_AVAILABLE, POLICY_CONDITIONAL],
}

VALID_ACTION_PLAN = {
    "summary": "현재 저축 계획을 유지하면서 이용 가능한 정책을 활용하세요.",
    "actions": [
        {
            "priority": 1,
            "action_type": "SAVING",
            "timing": "NOW",
            "title": "월 저축계획 유지",
            "description": "현재 월 500,000원 저축을 유지합니다.",
            "reason": "목표 저축액을 충족하고 있습니다.",
            "policy_id": None,
            "due_date": None,
        },
        {
            "priority": 2,
            "action_type": "POLICY",
            "timing": "NOW",
            "title": "청년월세 지원사업 신청 준비",
            "description": "신청기간과 필요서류를 확인합니다.",
            "reason": "현재 이용 가능한 정책입니다.",
            "policy_id": 1,
            "due_date": "2026-05-29",
        },
    ],
}
