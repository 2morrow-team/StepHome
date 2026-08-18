"""공통 테스트 픽스처 — 노션 Demo Persona 기준 (새 P0 필드 구조)"""

DIAGNOSIS = {
    "diagnosis_id": 1,
    "user_id": 1,
    "target_id": 1,
    "readiness_score": 25,
    "fund_score": 23.33,
    "saving_score": 1.75,
    "required_initial_fund": 90000000,
    "initial_fund_gap": 60000000,
    "required_monthly_saving": 8571429,
    "estimated_months": 120,
}

POLICY_AVAILABLE = {
    "policy_id": 1,
    "title": "청년월세 지원사업",
    "policy_category": "RENT_SUPPORT",
    "policy_region": "NATIONAL",
    "policy_provider": "국토교통부",
    "eligibility_status": "AVAILABLE",
    "matched_conditions": ["AGE", "INCOME", "HOUSING_TYPE"],
    "failed_conditions": [],
    "missing_conditions": [],
    "condition_details": [
        {
            "condition": "AGE",
            "result": "MATCHED",
            "current_value": 25,
            "required_min": 19,
            "required_max": 34,
            "required_values": None,
            "message": "연령 조건을 충족합니다.",
        }
    ],
    "rank": 1,
    "support_amount": 200000,
    "support_amount_unit": "MONTH",
    "support_amount_text": "월 최대 20만원, 최대 24개월 지원",
    "application_start": "2026-03-30",
    "application_end": "2026-05-29",
    "application_period_type": "FIXED",
}

POLICY_CONDITIONAL = {
    "policy_id": 6,
    "title": "서울시 청년월세지원",
    "policy_category": "RENT_SUPPORT",
    "policy_region": "서울특별시",
    "policy_provider": "서울특별시",
    "eligibility_status": "CONDITIONAL",
    "matched_conditions": ["AGE"],
    "failed_conditions": ["DEPOSIT_LIMIT"],
    "missing_conditions": [],
    "condition_details": [
        {
            "condition": "DEPOSIT_LIMIT",
            "result": "FAILED",
            "current_value": 90000000,
            "required_min": None,
            "required_max": 80000000,
            "required_values": None,
            "message": "희망 보증금이 정책 기준을 초과합니다.",
        }
    ],
    "rank": 2,
    "support_amount": 200000,
    "support_amount_unit": "MONTH",
    "support_amount_text": "월 최대 20만원의 임차료를 최대 12개월 지원하며 생애 1회 지원",
    "application_start": "2026-05-06",
    "application_end": "2026-05-19",
    "application_period_type": "FIXED",
}

POLICY_NEED_MORE_INFO = {
    "policy_id": 3,
    "title": "제주 청년 희망충전 월세 지원",
    "policy_category": "RENT_SUPPORT",
    "policy_region": "JEJU",
    "policy_provider": "제주특별자치도",
    "eligibility_status": "NEED_MORE_INFO",
    "matched_conditions": [],
    "failed_conditions": [],
    "missing_conditions": ["HOUSEHOLD_INCOME"],
    "condition_details": [
        {
            "condition": "HOUSEHOLD_INCOME",
            "result": "MISSING",
            "current_value": None,
            "required_min": None,
            "required_max": None,
            "required_values": None,
            "message": "가구소득 정보가 필요합니다.",
        }
    ],
    "rank": 3,
    "support_amount": 200000,
    "support_amount_unit": "MONTH",
    "support_amount_text": "월 최대 20만원, 최대 12개월 지원",
    "application_start": None,
    "application_end": None,
    "application_period_type": "ALWAYS_OPEN",
}

POLICY_NOT_ELIGIBLE = {
    "policy_id": 4,
    "title": "청년전용 버팀목 전세자금대출",
    "policy_category": "LOAN",
    "policy_region": "NATIONAL",
    "policy_provider": "주택도시기금",
    "eligibility_status": "NOT_ELIGIBLE",
    "matched_conditions": [],
    "failed_conditions": ["HOUSING_TYPE", "AGE"],
    "missing_conditions": [],
    "condition_details": [],
    "rank": 4,
    "support_amount": 150000000,
    "support_amount_unit": "TOTAL",
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
        "age": 25,
        "current_region": "SEOUL",
        "employment_status": "EMPLOYED",
        "marital_status": "UNMARRIED",
        "youth_household_monthly_income": 2500000,
        "youth_household_size": 1,
        "personal_monthly_income": 2500000,
        "total_assets": 30000000,
        "monthly_savings": 500000,
        "housing_status": "NO_HOME",
    },
    "target": {
        "planned_move_in_date": "2027-03-01",
        "desired_region": "SEOUL",
        "desired_deposit": 90000000,
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
            "phase": 1,
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
            "phase": 1,
            "priority": 2,
            "action_type": "POLICY",
            "timing": "NOW",
            "title": "청년월세 지원사업 신청 준비",
            "description": "신청기간과 필요서류를 확인합니다.",
            "reason": "현재 이용 가능한 정책입니다.",
            "policy_id": 1,
            "due_date": None,
        },
    ],
}
