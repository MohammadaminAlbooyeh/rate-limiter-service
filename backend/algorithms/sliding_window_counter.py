import time
import math
from backend.algorithms.base_algorithm import BaseAlgorithm
from backend.storage.base_store import BaseStore


class SlidingWindowCounterAlgorithm(BaseAlgorithm):
    def __init__(self, store: BaseStore):
        self.store = store

    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        current_window = math.floor(now / window)
        previous_window = current_window - 1

        current_key = f"{key}:{current_window}"
        previous_key = f"{key}:{previous_window}"

        current_count = await self.store.get(current_key)
        previous_count = await self.store.get(previous_key)

        overlap = (now - (current_window * window)) / window
        estimate = current_count + (previous_count * (1 - overlap))

        if estimate < limit:
            await self.store.increment(current_key, window)
            return True
        return False

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        now = time.time()
        current_window = math.floor(now / window)
        previous_window = current_window - 1

        current_count = await self.store.get(f"{key}:{current_window}")
        previous_count = await self.store.get(f"{key}:{previous_window}")

        overlap = (now - (current_window * window)) / window
        estimate = current_count + (previous_count * (1 - overlap))

        return max(0, limit - int(estimate))

    async def get_reset_time(self, key: str, window: int) -> int:
        now = time.time()
        current_window = math.floor(now / window)
        return int(((current_window + 1) * window) - now)
