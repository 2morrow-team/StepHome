import json
from pathlib import Path
from typing import Any

from app.policy.preprocessing.preprocessing_extractor import (
    extract_policy,
)
from app.policy.preprocessing.preprocessing_normalizer import (
    normalize_policy_data,
)
from app.policy.preprocessing.preprocessing_validator import (
    validate_policy,
)


RAW_POLICY_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "raw_policies.json"
)

GENERATED_POLICY_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "policies_generated.json"
)


def load_raw_policies(
    path: Path = RAW_POLICY_PATH,
) -> list[dict[str, Any]]:
    """
    raw_policies.json을 읽는다.
    """
    raw_policies = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(raw_policies, list):
        raise ValueError(
            "raw policy 데이터의 최상위 구조는 list여야 합니다."
        )

    return raw_policies


def preprocess_policy(
    raw_policy: dict[str, Any],
) -> dict[str, Any]:
    """
    정책 하나에 대해 전체 preprocessing을 수행한다.

    Raw Text
    -> LLM Extraction
    -> Normalization
    -> Pydantic Validation
    """
    extracted = extract_policy(raw_policy)

    normalized = normalize_policy_data(
        extracted
    )

    validated = validate_policy(
        normalized
    )

    return validated.model_dump(
        mode="json"
    )


def preprocess_policies(
    raw_policies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    여러 정책을 순차적으로 전처리한다.
    """
    processed_policies: list[dict[str, Any]] = []

    for raw_policy in raw_policies:
        policy_id = raw_policy.get(
            "policy_id",
            "UNKNOWN",
        )

        print(
            f"[PROCESSING] policy_id={policy_id}"
        )

        try:
            processed = preprocess_policy(
                raw_policy
            )

            processed_policies.append(
                processed
            )

            print(
                f"[SUCCESS] policy_id={policy_id}"
            )

        except Exception as exc:
            print(
                f"[FAILED] policy_id={policy_id}"
            )
            print(
                f"  reason: {exc}"
            )

    return processed_policies


def save_generated_policies(
    policies: list[dict[str, Any]],
    path: Path = GENERATED_POLICY_PATH,
) -> None:
    """
    검증에 성공한 정책만 JSON 파일로 저장한다.
    """
    path.write_text(
        json.dumps(
            policies,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def run_pipeline() -> list[dict[str, Any]]:
    """
    전체 preprocessing pipeline 실행.
    """
    raw_policies = load_raw_policies()

    print(
        f"[START] raw policies: {len(raw_policies)}"
    )

    processed_policies = preprocess_policies(
        raw_policies
    )

    save_generated_policies(
        processed_policies
    )

    print(
        "[DONE] "
        f"{len(processed_policies)}/{len(raw_policies)} "
        "정책 preprocessing 성공"
    )

    print(
        f"[OUTPUT] {GENERATED_POLICY_PATH}"
    )

    return processed_policies


if __name__ == "__main__":
    run_pipeline()