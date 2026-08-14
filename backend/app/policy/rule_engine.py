# 정책 규칙을 실행하는 엔진
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.schemas.schemas import EligibilityStatus


KST = timezone(timedelta(hours=9))
POLICY_DATA_PATH = Path(__file__).parent / "data" / "policies.json"


def _load_policies() -> list[dict[str, Any]]:
    return json.loads(POLICY_DATA_PATH.read_text(encoding="utf-8"))


def _policy_result(policy: dict[str, Any], user: dict[str, Any], target: dict[str, Any]) -> tuple[EligibilityStatus, list[str], list[str]]:
    rules = policy["eligibility_rules"]
    matched: list[str] = []
    failed: list[str] = []

    age_rule = rules["age"]
    if age_rule["min"] <= user["age"] <= age_rule["max"]:
        matched.append("AGE")
    else:
        failed.append("AGE")

    if user["monthly_income"] <= rules["income"]["max"]:
        matched.append("INCOME")
    else:
        failed.append("INCOME")

    if target["housing_type"] in rules["housing_type"]:
        matched.append("HOUSING_TYPE")
    else:
        failed.append("HOUSING_TYPE")

    if target["target_region"] in rules["region"]:
        matched.append("REGION")
    else:
        failed.append("REGION")

    if "deposit" in rules:
        if target["deposit_budget"] <= rules["deposit"]["max"]:
            matched.append("DEPOSIT_LIMIT")
        else:
            failed.append("DEPOSIT_LIMIT")

    if failed and failed == ["DEPOSIT_LIMIT"]:
        return EligibilityStatus.CONDITIONAL, matched, failed
    if failed:
        return EligibilityStatus.NOT_ELIGIBLE, matched, failed
    return EligibilityStatus.AVAILABLE, matched, failed


def match_policies(user: dict[str, Any], target: dict[str, Any], diagnosis_id: int, first_match_id: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    matched_at = datetime.now(KST)
    for offset, policy in enumerate(_load_policies()):
        status, matched, failed = _policy_result(policy, user, target)
        matches.append(
            {
                "match_id": first_match_id + offset,
                "user_id": user["user_id"],
                "diagnosis_id": diagnosis_id,
                "policy_id": policy["policy_id"],
                "title": policy["title"],
                "eligibility_status": status,
                "matched_conditions": matched,
                "failed_conditions": failed,
                "missing_conditions": [],
                "rank": offset + 1,
                "support_amount": policy["support_amount"],
                "support_amount_text": policy["support_amount_text"],
                "eligibility_text": policy["eligibility_text"],
                "description": policy["description"],
                "application_start": policy["application_start"],
                "application_end": policy["application_end"],
                "region": policy["region"],
                "provider": policy["provider"],
                "category": policy["category"],
                "source_url": policy["source_url"],
                "checked_at": policy["checked_at"],
                "matched_at": matched_at,
            }
        )
    return matches
