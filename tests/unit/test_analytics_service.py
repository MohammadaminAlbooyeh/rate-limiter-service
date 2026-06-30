import pytest
from backend.models.database import engine, Base
import backend.models.models


@pytest.fixture(autouse=True)
def setup_db():
    import sqlalchemy
    sync_engine = sqlalchemy.create_engine("sqlite:///./test_ratelimit.db")
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest.mark.asyncio
async def test_log_and_get_usage():
    from backend.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    await service.log_request(identity="user_1", endpoint="/test", method="GET", allowed=True)
    await service.log_request(identity="user_1", endpoint="/test", method="GET", allowed=False)
    usage = await service.get_usage("user_1")
    assert usage["total_requests"] == 2
    assert usage["allowed_requests"] == 1
    assert usage["blocked_requests"] == 1


@pytest.mark.asyncio
async def test_get_blocked():
    from backend.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    await service.log_request(identity="user_2", endpoint="/api", method="POST", allowed=False)
    blocked = await service.get_blocked()
    assert len(blocked) >= 1
    assert any(b["identity"] == "user_2" for b in blocked)


@pytest.mark.asyncio
async def test_get_top_consumers():
    from backend.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    for i in range(5):
        await service.log_request(identity="heavy_user", endpoint="/", method="GET", allowed=True)
    await service.log_request(identity="light_user", endpoint="/", method="GET", allowed=True)
    top = await service.get_top_consumers(limit=5)
    assert len(top) >= 2
    heavy = next(t for t in top if t["identity"] == "heavy_user")
    assert heavy["total_requests"] >= 5


@pytest.mark.asyncio
async def test_get_timeline():
    from backend.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    await service.log_request(identity="user_3", endpoint="/test", method="GET", allowed=True)
    await service.log_request(identity="user_3", endpoint="/test", method="GET", allowed=False)
    timeline = await service.get_timeline(minutes=60)
    assert len(timeline) >= 1
    assert timeline[0]["total"] >= 2
