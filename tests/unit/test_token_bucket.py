import pytest
from backend.algorithms.token_bucket import TokenBucketAlgorithm
from backend.storage.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_token_bucket_allows():
    store = MemoryStore()
    algo = TokenBucketAlgorithm(store)
    assert await algo.allow_request("test:1", 100, 3600) is True


@pytest.mark.asyncio
async def test_token_bucket_blocks_when_empty():
    store = MemoryStore()
    algo = TokenBucketAlgorithm(store)
    await algo.allow_request("test:1", 1, 3600)
    assert await algo.allow_request("test:1", 1, 3600) is False
