import pytest
from backend.algorithms.fixed_window import FixedWindowAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_fixed_window_allows_within_limit():
    store = MemoryStore()
    algo = FixedWindowAlgorithm(store)
    assert await algo.allow_request("test:1", 5, 60) is True


@pytest.mark.asyncio
async def test_fixed_window_blocks_exceeding_limit():
    store = MemoryStore()
    algo = FixedWindowAlgorithm(store)
    for _ in range(5):
        await algo.allow_request("test:1", 5, 60)
    assert await algo.allow_request("test:1", 5, 60) is False


@pytest.mark.asyncio
async def test_fixed_window_remaining():
    store = MemoryStore()
    algo = FixedWindowAlgorithm(store)
    await algo.allow_request("test:1", 5, 60)
    remaining = await algo.get_remaining("test:1", 5, 60)
    assert remaining == 4
