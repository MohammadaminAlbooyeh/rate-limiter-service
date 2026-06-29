import pytest
from backend.models.database import init_db, engine, Base


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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
    # Removing non-existent returns False
    assert await service.remove_whitelist("nonexistent") is False


@pytest.mark.asyncio
async def test_remove_blacklist():
    from backend.services.whitelist_service import WhitelistService
    service = WhitelistService()
    await service.add_blacklist("remove_me_bl", "test")
    assert await service.remove_blacklist("remove_me_bl") is True
    assert await service.is_blacklisted("remove_me_bl") is False
