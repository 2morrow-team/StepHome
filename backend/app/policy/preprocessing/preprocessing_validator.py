import json
from pathlib import Path

from pydantic import ValidationError

from app.policy.preprocessing.preprocessing_schema import PolicyData


POLICY_DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "policies.json"
)


def validate_policy(policy: dict) -> PolicyData:
    """
    정책 하나를 PolicyData Schema로 검증한다.
    """
    return PolicyData.model_validate(policy)


def validate_policies(
    policies: list[dict],
) -> list[PolicyData]:
    """
    정책 목록 전체를 검증한다.
    """
    validated_policies: list[PolicyData] = []

    for policy in policies:
        validated_policy = validate_policy(policy)
        validated_policies.append(validated_policy)

    return validated_policies


def validate_policy_file(
    path: Path = POLICY_DATA_PATH,
) -> list[PolicyData]:
    """
    JSON 파일을 읽고 모든 정책을 검증한다.
    """
    policies = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(policies, list):
        raise ValueError(
            "정책 데이터의 최상위 구조는 list여야 합니다."
        )

    return validate_policies(policies)


if __name__ == "__main__":
    try:
        validated = validate_policy_file()

        print(
            f"[SUCCESS] {len(validated)}개 정책 validation 완료"
        )

        for policy in validated:
            print(
                f"- {policy.policy_id}: {policy.title}"
            )

    except ValidationError as exc:
        print("[VALIDATION ERROR]")
        print(exc)

    except Exception as exc:
        print("[ERROR]")
        print(exc)