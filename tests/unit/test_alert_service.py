import pytest
from backend.models.database import engine, Base
import backend.models.models  # noqa: F401 - registers tables on Base.metadata


@pytest.fixture(autouse=True)
def setup_db():
    import sqlalchemy
    sync_engine = sqlalchemy.create_engine("sqlite:///./test_ratelimit.db")
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest.mark.asyncio
async def test_alert_triggered_at_90_percent():
    from backend.services.alert_service import AlertService
    service = AlertService()
    triggered = await service.check_threshold("test_user", 90, 100)
    assert triggered is True


@pytest.mark.asyncio
async def test_alert_not_triggered_below_90_percent():
    from backend.services.alert_service import AlertService
    service = AlertService()
    triggered = await service.check_threshold("test_user", 50, 100)
    assert triggered is False


@pytest.mark.asyncio
async def test_get_alerts_returns_accumulated():
    from backend.services.alert_service import AlertService
    service = AlertService()
    await service.check_threshold("user_a", 95, 100)
    await service.check_threshold("user_b", 99, 100)
    alerts = await service.get_alerts()
    assert len(alerts) == 2
