import time
import json
from typing import Optional
from backend.storage.base_store import BaseStore


class MemoryStore(BaseStore):
    def __init__(self):
        self._data: dict = {}
        self._expiry: dict = {}

    async def get(self, key: str) -> int:
        self._evict(key)
        return self._data.get(key, 0)

    async def increment(self, key: str, ttl: int) -> int:
        self._evict(key)
        val = self._data.get(key, 0) + 1
        self._data[key] = val
        if val == 1:
            self._expiry[key] = time.time() + ttl
        return val

    async def ttl(self, key: str) -> int:
        self._evict(key)
        if key in self._expiry:
            return int(self._expiry[key] - time.time())
        return -1

    async def remove_range_by_score(self, key: str, min: float, max: float) -> None:
        if key not in self._data:
            return
        self._data[key] = [t for t in self._data[key] if not (min <= t <= max)]

    async def count(self, key: str) -> int:
        return len(self._data.get(key, []))

    async def count_range_by_score(self, key: str, min: float, max: float) -> int:
        return sum(1 for t in self._data.get(key, []) if min <= t <= max)

    async def add_timestamp(self, key: str, timestamp: float, ttl: int) -> None:
        if key not in self._data:
            self._data[key] = []
        self._data[key].append(timestamp)
        self._expiry[key] = time.time() + ttl

    async def get_bucket(self, key: str) -> Optional[dict]:
        self._evict(key)
        if key in self._data:
            return json.loads(self._data[key])
        return None

    async def set_bucket(self, key: str, tokens: float, timestamp: float) -> None:
        self._data[key] = json.dumps({"tokens": tokens, "last_refill": timestamp})

    def _evict(self, key: str):
        if key in self._expiry and time.time() > self._expiry[key]:
            del self._data[key]
            del self._expiry[key]
