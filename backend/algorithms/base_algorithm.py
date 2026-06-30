from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    @abstractmethod
    async def allow_request(self, key: str, limit: int, window: int) -> bool:
        ...

    @abstractmethod
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        ...

    @abstractmethod
    async def get_reset_time(self, key: str, limit: int, window: int) -> int:
        ...
