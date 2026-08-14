# 데이터베이스 연결 설정
from copy import deepcopy
from typing import Any


class InMemoryDatabase:
    def __init__(self):
        self._counters = {
            "user": 0,
            "target": 0,
            "diagnosis": 0,
            "match": 0,
            "plan": 0,
            "action": 0,
        }
        self._plans: dict[tuple[int, int, int], dict[str, Any]] = {}

    def next_id(self, entity: str) -> int:
        self._counters[entity] += 1
        return self._counters[entity]

    def reserve_ids(self, entity: str, count: int) -> list[int]:
        return [self.next_id(entity) for _ in range(count)]

    def save_plan(self, record: dict[str, Any]) -> None:
        key = (record["user_id"], record["target_id"], record["plan_id"])
        self._plans[key] = deepcopy(record)

    def get_plan(self, user_id: int, target_id: int, plan_id: int) -> dict[str, Any] | None:
        record = self._plans.get((user_id, target_id, plan_id))
        return deepcopy(record) if record else None
