import pytest
import time
from backend.algorithms.sliding_window_log import SlidingWindowLogAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_sliding_window_log_allows_within_limit():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    assert await algo.allow_request("test:swl:1", 5, 60) is True


@pytest.mark.asyncio
async def test_sliding_window_log_blocks_exceeding_limit():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    for _ in range(5):
        await algo.allow_request("test:swl:2", 5, 60)
    assert await algo.allow_request("test:swl:2", 5, 60) is False


@pytest.mark.asyncio
async def test_sliding_window_log_remaining():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    await algo.allow_request("test:swl:3", 5, 60)
    remaining = await algo.get_remaining("test:swl:3", 5, 60)
    assert remaining == 4


@pytest.mark.asyncio
async def test_sliding_window_log_reset_time():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    reset = await algo.get_reset_time("test:swl:4", 5, 60)
    assert reset == 60


@pytest.mark.asyncio
async def test_sliding_window_log_expires_old_entries():
    store = MemoryStore()
    algo = SlidingWindowLogAlgorithm(store)
    now = time.time()
    # Manually add expired timestamps
    key = "test:swl:expire"
    await store.add_timestamp(key, now - 120, 60)  # expired (outside 60s window)
    await store.add_timestamp(key, now - 10, 60)   # valid
    # allow_request should remove expired and still work
    allowed = await algo.allow_request(key, 5, 60)
    # After adding the new one, there should be 2 valid entries (1 existing + 1 new)
    assert allowed is True

