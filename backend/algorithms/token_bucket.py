import time
from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class TokenBucketAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    @staticmethod
    def _refill_rate(limit: int, window: int) -> float:
        return limit / max(window, 1)

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        data = await self.store.get_bucket(key)
        now = time.time()
        rate = self._refill_rate(limit, window)

        if data is None:
            await self.store.set_bucket(key, limit - 1, now)
            return True

        tokens, last_refill = data["tokens"], data["last_refill"]
        elapsed = now - last_refill
        tokens = min(limit, tokens + elapsed * rate)

        if tokens >= 1:
            await self.store.set_bucket(key, tokens - 1, now)
            return True

        return False

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return limit

        rate = self._refill_rate(limit, window)
        tokens, last_refill = data["tokens"], data["last_refill"]
        elapsed = time.time() - last_refill
        tokens = min(limit, tokens + elapsed * rate)

        return max(0, int(tokens))

    async def get_reset_time(self, key: str, limit: int, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return 0

        rate = self._refill_rate(limit, window)
        tokens, last_refill = data["tokens"], data["last_refill"]
        deficit = 1 - tokens
        if deficit <= 0:
            return 0

        return int(deficit / rate) if rate > 0 else window
