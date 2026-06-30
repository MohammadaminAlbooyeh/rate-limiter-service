"""
Unit tests for RedisClusterStore.

These tests use a mock approach to avoid requiring a real Redis cluster.
They verify that the store correctly delegates operations to the underlying
RedisCluster client.
"""
import pytest
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

from backend.storage.redis_cluster import RedisClusterStore


@pytest.fixture
def mock_cluster_client():
    """Create a mock RedisCluster client."""
    mock = MagicMock()
    # Make async methods return awaitable values
    mock.get = AsyncMock(return_value=None)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.ttl = AsyncMock(return_value=55)
    mock.zremrangebyscore = AsyncMock(return_value=1)
    mock.zcard = AsyncMock(return_value=2)
    mock.zcount = AsyncMock(return_value=2)
    mock.zadd = AsyncMock(return_value=1)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.scan = AsyncMock(side_effect=[(0, ["key1", "key2"])])
    return mock


@pytest.fixture
def store(mock_cluster_client):
    """Create a RedisClusterStore with mocked client."""
    with patch("backend.storage.redis_cluster.RedisClusterClient", return_value=mock_cluster_client):
        s = RedisClusterStore(startup_nodes=[("localhost", 7000)])
        s.client = mock_cluster_client
        return s


@pytest.mark.asyncio
async def test_get_returns_zero_for_missing_key(store):
    store.client.get = AsyncMock(return_value=None)
    val = await store.get("nonexistent")
    assert val == 0


@pytest.mark.asyncio
async def test_get_parses_int_value(store):
    store.client.get = AsyncMock(return_value="42")
    val = await store.get("counter")
    assert val == 42


@pytest.mark.asyncio
async def test_increment_and_set_expiry(store):
    store.client.incr = AsyncMock(return_value=1)
    val = await store.increment("test:incr", 60)
    assert val == 1
    store.client.expire.assert_awaited_once_with("test:incr", 60)


@pytest.mark.asyncio
async def test_increment_does_not_set_expiry_again(store):
    store.client.incr = AsyncMock(return_value=2)
    val = await store.increment("test:incr2", 60)
    assert val == 2
    # expire should not be called when val > 1 (already had TTL set)
    store.client.expire.assert_not_called()


@pytest.mark.asyncio
async def test_ttl(store):
    ttl = await store.ttl("test:ttl")
    assert ttl == 55


@pytest.mark.asyncio
async def test_remove_range_by_score(store):
    await store.remove_range_by_score("test:zset", 0, 100)
    store.client.zremrangebyscore.assert_awaited_once_with("test:zset", 0, 100)


@pytest.mark.asyncio
async def test_count(store):
    count = await store.count("test:zset")
    assert count == 2


@pytest.mark.asyncio
async def test_count_range_by_score(store):
    count = await store.count_range_by_score("test:zset", 100, 200)
    assert count == 2


@pytest.mark.asyncio
async def test_add_timestamp(store):
    await store.add_timestamp("test:log", 1234567890.0, 60)
    store.client.zadd.assert_awaited_once()
    store.client.expire.assert_awaited_once_with("test:log", 60)


@pytest.mark.asyncio
async def test_get_bucket_nonexistent(store):
    store.client.get = AsyncMock(return_value=None)
    data = await store.get_bucket("test:bucket")
    assert data is None


@pytest.mark.asyncio
async def test_get_bucket_parses_json(store):
    now = time.time()
    store.client.get = AsyncMock(return_value=json.dumps({"tokens": 5.0, "last_refill": now}))
    data = await store.get_bucket("test:bucket")
    assert data is not None
    assert data["tokens"] == 5.0
    assert data["last_refill"] == now


@pytest.mark.asyncio
async def test_set_bucket(store):
    now = time.time()
    await store.set_bucket("test:bucket", 3.0, now)
    store.client.set.assert_awaited_once()
    call_args = store.client.set.call_args[0]
    assert call_args[0] == "test:bucket"
    parsed = json.loads(call_args[1])
    assert parsed["tokens"] == 3.0
    assert parsed["last_refill"] == now


@pytest.mark.asyncio
async def test_delete(store):
    await store.delete("test:key")
    store.client.delete.assert_awaited_once_with("test:key")


@pytest.mark.asyncio
async def test_delete_by_pattern(store):
    store.client.scan = AsyncMock(side_effect=[(0, ["rate_limit:user1:*", "rate_limit:user2:*"])])
    await store.delete_by_pattern("rate_limit:*")
    store.client.delete.assert_awaited_once_with("rate_limit:user1:*", "rate_limit:user2:*")
