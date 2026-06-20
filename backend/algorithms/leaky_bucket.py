import time
from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class LeakyBucketAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore, leak_rate: int = 10):
        self.store = store
        self.leak_rate = leak_rate

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        data = await self.store.get_bucket(key)
        now = time.time()

        if data is None:
            await self.store.set_bucket(key, 1, now)
            return True

        water, last_leak = data["tokens"], data["last_refill"]
        leaked = (now - last_leak) * self.leak_rate
        water = max(0, water - leaked)

        if water < limit:
            await self.store.set_bucket(key, water + 1, now)
            return True

        return False

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return limit

        water, last_leak = data["tokens"], data["last_refill"]
        leaked = (time.time() - last_leak) * self.leak_rate
        water = max(0, water - leaked)

        return int(limit - water)

    async def get_reset_time(self, key: str, window: int) -> int:
        data = await self.store.get_bucket(key)
        if data is None:
            return 0

        water, last_leak = data["tokens"], data["last_refill"]
        return int(water / self.leak_rate)
