import pytest
import time
from backend.storage.redis_store import RedisStore
from backend.storage.redis_cluster import RedisClusterStore


@pytest.mark.asyncio
async def test_redis_increment():
    import redis.asyncio as redis
    client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
    try:
        await client.ping()
    except Exception:
        pytest.skip("Local Redis server is not running on localhost:6379")
    finally:
        await client.aclose()

    store = RedisStore()
    key = "test:incr_key"
    try:
        # Reset key
        await store.client.delete(key)

        val = await store.increment(key, 60)
        assert val == 1

        val = await store.increment(key, 60)
        assert val == 2

        ttl = await store.ttl(key)
        assert 0 < ttl <= 60
    finally:
        await store.client.delete(key)
        await store.client.aclose()


@pytest.mark.asyncio
async def test_redis_get_bucket():
    import redis.asyncio as redis
    client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
    try:
        await client.ping()
    except Exception:
        pytest.skip("Local Redis server is not running on localhost:6379")
    finally:
        await client.aclose()

    store = RedisStore()
    key = "test:bucket"
    try:
        await store.client.delete(key)
        # Non-existent bucket returns None
        assert await store.get_bucket(key) is None

        # Set and retrieve bucket
        now = time.time()
        await store.set_bucket(key, 10.0, now)
        data = await store.get_bucket(key)
        assert data is not None
        assert data["tokens"] == 10.0
        assert data["last_refill"] == now
    finally:
        await store.client.delete(key)
        await store.client.aclose()


@pytest.mark.asyncio
async def test_redis_delete_by_pattern():
    import redis.asyncio as redis
    client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
    try:
        await client.ping()
    except Exception:
        pytest.skip("Local Redis server is not running on localhost:6379")
    finally:
        await client.aclose()

    store = RedisStore()
    try:
        await store.client.set("test:pat:a", "1")
        await store.client.set("test:pat:b", "2")
        await store.client.set("other:key", "3")

        await store.delete_by_pattern("test:pat:*")

        assert await store.client.get("test:pat:a") is None
        assert await store.client.get("test:pat:b") is None
        assert await store.client.get("other:key") == "3"
    finally:
        await store.client.delete("test:pat:a")
        await store.client.delete("test:pat:b")
        await store.client.delete("other:key")
        await store.client.aclose()


@pytest.mark.asyncio
async def test_redis_sorted_set_operations():
    import redis.asyncio as redis
    client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
    try:
        await client.ping()
    except Exception:
        pytest.skip("Local Redis server is not running on localhost:6379")
    finally:
        await client.aclose()

    store = RedisStore()
    key = "test:zset"
    try:
        now = time.time()
        await store.add_timestamp(key, now - 5, 60)
        await store.add_timestamp(key, now, 60)

        count = await store.count(key)
        assert count == 2

        count_in_range = await store.count_range_by_score(key, now - 10, now)
        assert count_in_range == 2

        # Remove one timestamp
        await store.remove_range_by_score(key, now - 1, now + 1)
        assert await store.count(key) == 1
    finally:
        await store.client.delete(key)
        await store.client.aclose()

