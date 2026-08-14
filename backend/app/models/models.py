# 데이터 모델 정의
from typing import Any


class StoredPlan:
    def __init__(self, snapshot: dict[str, Any], user: dict[str, Any]):
        self.snapshot = snapshot
        self.user = user
