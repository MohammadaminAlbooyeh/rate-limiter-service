import pytest
from backend.algorithms.leaky_bucket import LeakyBucketAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_leaky_bucket_allows():
    store = MemoryStore()
    algo = LeakyBucketAlgorithm(store, leak_rate=10)
    assert await algo.allow_request("test:1", 100, 3600) is True


@pytest.mark.asyncio
async def test_leaky_bucket_blocks_when_full():
    store = MemoryStore()
    algo = LeakyBucketAlgorithm(store, leak_rate=1)
    for _ in range(10):
        await algo.allow_request("test:1", 10, 3600)
    assert await algo.allow_request("test:1", 10, 3600) is False
