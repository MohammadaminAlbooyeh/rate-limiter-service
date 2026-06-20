from abc import ABC, abstractmethod
from typing import Optional


class BaseAlgorithm(ABC):
    @abstractmethod
    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        ...

    @abstractmethod
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        ...

    @abstractmethod
    async def get_reset_time(self, key: str, window: int) -> int:
        ...
        
    async def simulate(self, key: str, limit: int, window: int) -> tuple[bool, int, int]:
        allowed = await self.allow_request(key, limit, window)
        remaining = await self.get_remaining(key, limit, window)
        reset = await self.get_reset_time(key, window)
        return allowed, remaining, reset
