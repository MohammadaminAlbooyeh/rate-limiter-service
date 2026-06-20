import pytest
from backend.algorithms.sliding_window_log import SlidingWindowLogAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_sliding_window_log_allows():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    assert await algo.allow_request("test:1", 5, 60) is True
