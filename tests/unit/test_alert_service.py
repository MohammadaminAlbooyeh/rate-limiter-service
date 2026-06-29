import pytest
from backend.services.alert_service import AlertService


@pytest.mark.asyncio
async def test_alert_triggered_at_90_percent():
    service = AlertService()
    triggered = await service.check_threshold("test_user", 90, 100)
    assert triggered is True


@pytest.mark.asyncio
async def test_alert_not_triggered_below_90_percent():
    service = AlertService()
    triggered = await service.check_threshold("test_user", 50, 100)
    assert triggered is False


@pytest.mark.asyncio
async def test_get_alerts_returns_accumulated():
    service = AlertService()
    await service.check_threshold("user_a", 95, 100)
    await service.check_threshold("user_b", 99, 100)
    alerts = await service.get_alerts()
    assert len(alerts) == 2
    assert alerts[0]["identity"] == "user_a"
    assert alerts[1]["identity"] == "user_b"
