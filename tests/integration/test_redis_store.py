import pytest


@pytest.mark.skip(reason="Requires Redis")
@pytest.mark.asyncio
async def test_redis_increment():
    pass
