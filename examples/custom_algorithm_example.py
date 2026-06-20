from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class CustomAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        return True

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        return limit

    async def get_reset_time(self, key: str, window: int) -> int:
        return 0
