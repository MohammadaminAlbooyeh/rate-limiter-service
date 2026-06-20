from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class FixedWindowAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        current = await self.store.increment(key, window)
        return current <= limit

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        current = await self.store.get(key)
        return max(0, limit - current)

    async def get_reset_time(self, key: str, window: int) -> int:
        return await self.store.ttl(key)
