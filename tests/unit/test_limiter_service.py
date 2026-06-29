import pytest
from backend.services.limiter_service import LimiterService
from backend.storage.memory_store import MemoryStore
from backend.models.rule import Rule


@pytest.fixture
def limiter():
    store = MemoryStore()
    return LimiterService(store=store)


@pytest.mark.asyncio
async def test_limiter_check_allows(limiter):
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=5, window=60)
    identity = {"ip": "10.0.0.1", "endpoint": "/test"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True
    assert remaining == 4
    assert reset >= 0


@pytest.mark.asyncio
async def test_limiter_check_blocks_when_exceeded(limiter):
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=3, window=60)
    identity = {"ip": "10.0.0.2", "endpoint": "/test"}
    for _ in range(3):
        await limiter.check(identity, rule)
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_limiter_with_sliding_window_log(limiter):
    rule = Rule(name="test", identity="ip", algorithm="sliding_window_log", limit=5, window=60)
    identity = {"ip": "10.0.0.3", "endpoint": "/api"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True


@pytest.mark.asyncio
async def test_limiter_with_sliding_window_counter(limiter):
    rule = Rule(name="test", identity="ip", algorithm="sliding_window_counter", limit=10, window=60)
    identity = {"ip": "10.0.0.4", "endpoint": "/data"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True


@pytest.mark.asyncio
async def test_limiter_with_token_bucket(limiter):
    rule = Rule(name="test", identity="ip", algorithm="token_bucket", limit=100, window=3600)
    identity = {"ip": "10.0.0.5", "endpoint": "/events"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True


@pytest.mark.asyncio
async def test_limiter_with_leaky_bucket(limiter):
    rule = Rule(name="test", identity="ip", algorithm="leaky_bucket", limit=100, window=3600)
    identity = {"ip": "10.0.0.6", "endpoint": "/stream"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True


@pytest.mark.asyncio
async def test_limiter_reset_identity(limiter):
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=5, window=60)
    identity = {"ip": "10.0.0.7", "endpoint": "/test"}
    for _ in range(5):
        await limiter.check(identity, rule)
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is False
    # Reset and try again
    await limiter.reset_identity("10.0.0.7")
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True


@pytest.mark.asyncio
async def test_limiter_accepts_custom_store():
    store = MemoryStore()
    limiter = LimiterService(store=store)
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=5, window=60)
    identity = {"ip": "custom_store_test", "endpoint": "/test"}
    allowed, remaining, reset = await limiter.check(identity, rule)
    assert allowed is True
