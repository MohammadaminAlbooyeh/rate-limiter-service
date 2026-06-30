import pytest
import sqlalchemy
from backend.models.database import engine, Base
import backend.models.models


@pytest.fixture(autouse=True)
def setup_db():
    sync_engine = sqlalchemy.create_engine("sqlite:///./test_ratelimit.db")
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest.mark.asyncio
async def test_add_and_check_whitelist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_whitelist("192.168.1.1", "VIP user")
    assert await service.is_whitelisted("192.168.1.1") is True
    assert await service.is_whitelisted("unknown") is False


@pytest.mark.asyncio
async def test_add_and_check_blacklist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_blacklist("10.0.0.5", "Abusive IP")
    assert await service.is_blacklisted("10.0.0.5") is True
    assert await service.is_blacklisted("safe_ip") is False


@pytest.mark.asyncio
async def test_remove_whitelist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_whitelist("remove_me", "test")
    assert await service.remove_whitelist("remove_me") is True
    assert await service.is_whitelisted("remove_me") is False
    assert await service.remove_whitelist("nonexistent") is False


@pytest.mark.asyncio
async def test_remove_blacklist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_blacklist("remove_me_bl", "test")
    assert await service.remove_blacklist("remove_me_bl") is True
    assert await service.is_blacklisted("remove_me_bl") is False


@pytest.mark.asyncio
async def test_get_all_whitelist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_whitelist("ip1", "user 1")
    await service.add_whitelist("ip2", "user 2")
    entries = await service.get_all_whitelist()
    assert len(entries) >= 2
    identities = [e["identity"] for e in entries]
    assert "ip1" in identities
    assert "ip2" in identities


@pytest.mark.asyncio
async def test_get_all_blacklist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_blacklist("bad1", "abuse")
    await service.add_blacklist("bad2", "spam")
    entries = await service.get_all_blacklist()
    assert len(entries) >= 2
    identities = [e["identity"] for e in entries]
    assert "bad1" in identities
    assert "bad2" in identities
