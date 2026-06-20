import pytest
import redis.asyncio as redis
from backend.storage.redis_store import RedisStore


@pytest.mark.asyncio
async def test_redis_increment():
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
