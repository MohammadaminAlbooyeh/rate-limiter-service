import time
import pytest
from backend.storage.memory_store import MemoryStore


@pytest.fixture
def store():
    return MemoryStore()


@pytest.mark.asyncio
async def test_get_initial_zero(store):
    val = await store.get("nonexistent")
    assert val == 0


@pytest.mark.asyncio
async def test_increment_and_get(store):
    val = await store.increment("counter", ttl=60)
    assert val == 1
    val = await store.increment("counter", ttl=60)
    assert val == 2
    assert await store.get("counter") == 2


@pytest.mark.asyncio
async def test_ttl(store):
    await store.increment("temp", ttl=60)
    ttl = await store.ttl("temp")
    assert ttl > 0 and ttl <= 60
    assert await store.ttl("nonexistent") == -1


@pytest.mark.asyncio
async def test_delete(store):
    await store.increment("to_delete", ttl=60)
    assert await store.get("to_delete") == 1
    await store.delete("to_delete")
    assert await store.get("to_delete") == 0


@pytest.mark.asyncio
async def test_delete_by_pattern(store):
    for i in range(3):
        await store.increment(f"user:{i}:requests", ttl=60)
    await store.increment("other:key", ttl=60)
    await store.delete_by_pattern("user:*")
    assert await store.get("user:0:requests") == 0
    assert await store.get("user:1:requests") == 0
    assert await store.get("other:key") == 1


@pytest.mark.asyncio
async def test_add_timestamp_and_count(store):
    now = time.time()
    await store.add_timestamp("log", now - 5, ttl=60)
    await store.add_timestamp("log", now, ttl=60)
    assert await store.count("log") == 2
    count = await store.count_range_by_score("log", now - 10, now)
    assert count == 2


@pytest.mark.asyncio
async def test_remove_range_by_score(store):
    now = time.time()
    await store.add_timestamp("timed", now - 10, ttl=60)
    await store.add_timestamp("timed", now, ttl=60)
    await store.remove_range_by_score("timed", now - 5, now + 5)
    assert await store.count("timed") == 1


@pytest.mark.asyncio
async def test_bucket_operations(store):
    await store.set_bucket("bucket:test", 10, time.time())
    data = await store.get_bucket("bucket:test")
    assert data is not None
    assert data["tokens"] == 10
    assert "last_refill" in data


@pytest.mark.asyncio
async def test_get_bucket_nonexistent(store):
    data = await store.get_bucket("nothing")
    assert data is None


@pytest.mark.asyncio
async def test_eviction(store):
    await store.increment("expire_me", ttl=0)
    assert await store.get("expire_me") == 0
