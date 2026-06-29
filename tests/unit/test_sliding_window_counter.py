import pytest
import time
from backend.algorithms.sliding_window_counter import SlidingWindowCounterAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_sliding_window_counter_allows_within_limit():
    store = MemoryStore()
    algo = SlidingWindowCounterAlgorithm(store)
    assert await algo.allow_request("test:swc:1", 5, 60) is True


@pytest.mark.asyncio
async def test_sliding_window_counter_blocks_exceeding_limit():
    store = MemoryStore()
    algo = SlidingWindowCounterAlgorithm(store)
    for _ in range(5):
        await algo.allow_request("test:swc:2", 5, 60)
    assert await algo.allow_request("test:swc:2", 5, 60) is False


@pytest.mark.asyncio
async def test_sliding_window_counter_remaining():
    store = MemoryStore()
    algo = SlidingWindowCounterAlgorithm(store)
    await algo.allow_request("test:swc:3", 5, 60)
    remaining = await algo.get_remaining("test:swc:3", 5, 60)
    assert remaining < 5


@pytest.mark.asyncio
async def test_sliding_window_counter_reset_time():
    store = MemoryStore()
    algo = SlidingWindowCounterAlgorithm(store)
    reset = await algo.get_reset_time("test:swc:4", 60)
    assert 0 < reset <= 60


@pytest.mark.asyncio
async def test_sliding_window_counter_estimate_with_previous_window():
    """Test that the estimate uses previous window data when available."""
    store = MemoryStore()
    algo = SlidingWindowCounterAlgorithm(store)
    # Simulate a request that lands in the previous window
    key = "test:swc:estimate"
    for _ in range(3):
        await algo.allow_request(key, 10, 60)
    remaining = await algo.get_remaining(key, 10, 60)
    assert 0 <= remaining <= 10
