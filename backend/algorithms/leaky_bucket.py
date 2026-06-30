import time
from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class LeakyBucketAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    @staticmethod
    def _leak_rate(limit: int, window: int) -> float:
        return limit / max(window, 1)

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        data = await self.store.get_bucket(key)
        now = time.time()
        rate = self._leak_rate(limit, window)

        if data is None:
            if limit >= 1:
                await self.store.set_bucket(key, 1, now)
                return True
            return False

        water, last_leak = data["tokens"], data["last_refill"]
        leaked = (now - last_leak) * rate
        water = max(0, water - leaked)

        if water + 1 <= limit:
            await self.store.set_bucket(key, water + 1, now)
            return True

        return False

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return limit

        rate = self._leak_rate(limit, window)
        water, last_leak = data["tokens"], data["last_refill"]
        leaked = (time.time() - last_leak) * rate
        water = max(0, water - leaked)

        return max(0, int(limit - water))

    async def get_reset_time(self, key: str, limit: int, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return 0

        rate = self._leak_rate(limit, window)
        water, last_leak = data["tokens"], data["last_refill"]
        return int(water / rate) if rate > 0 else window
