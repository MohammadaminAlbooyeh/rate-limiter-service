from abc import ABC, abstractmethod
from typing import Optional, Any


class BaseStore(ABC):
    @abstractmethod
    async def get(self, key: str) -> int:
        ...

    @abstractmethod
    async def increment(self, key: str, ttl: int) -> int:
        ...

    @abstractmethod
    async def ttl(self, key: str) -> int:
        ...

    @abstractmethod
    async def remove_range_by_score(self, key: str, min: float, max: float) -> None:
        ...

    @abstractmethod
    async def count(self, key: str) -> int:
        ...

    @abstractmethod
    async def count_range_by_score(self, key: str, min: float, max: float) -> int:
        ...

    @abstractmethod
    async def add_timestamp(self, key: str, timestamp: float, ttl: int) -> None:
        ...

    @abstractmethod
    async def get_bucket(self, key: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def set_bucket(self, key: str, tokens: float, timestamp: float) -> None:
        ...
