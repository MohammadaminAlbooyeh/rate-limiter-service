import time
from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class SlidingWindowLogAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        cutoff = now - window
        await self.store.remove_range_by_score(key, 0, cutoff)
        count = await self.store.count(key)
        if count < limit:
            await self.store.add_timestamp(key, now, window)
            return True
        return False

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        now = time.time()
        cutoff = now - window
        count = await self.store.count_range_by_score(key, cutoff, now)
        return max(0, limit - count)

    async def get_reset_time(self, key: str, limit: int, window: int) -> int:
        return window
