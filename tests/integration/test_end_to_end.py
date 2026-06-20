import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.models.database import init_db, engine
from backend.models.models import RuleDB, WhitelistDB, BlacklistDB, RequestLogDB
from backend.models.database import Base


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_full_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a rate limit rule
        rule_res = await client.post("/api/v1/rules", json={
            "name": "Test Rule",
            "identity": "ip",
            "algorithm": "fixed_window",
            "limit": 5,
            "window": 60,
            "endpoint": "/test",
        })
        assert rule_res.status_code == 200
        rule = rule_res.json()
        assert rule["name"] == "Test Rule"

        # Health check
        health_res = await client.get("/health")
        assert health_res.status_code == 200

        # Check if a request to /test is allowed (should be, under limit)
        check_res = await client.post("/api/v1/check", json={
            "endpoint": "/test",
            "method": "GET",
            "ip": "10.0.0.1",
            "api_key": "",
            "user_id": "",
        })
        assert check_res.status_code == 200
        assert check_res.json()["allowed"] is True

        # Whitelist an IP
        wl_res = await client.post("/api/v1/whitelist", json={
            "identity": "10.0.0.99",
            "reason": "test whitelist",
        })
        assert wl_res.status_code == 200

        # Blacklist an IP
        bl_res = await client.post("/api/v1/blacklist", json={
            "identity": "10.0.0.66",
            "reason": "test blacklist",
        })
        assert bl_res.status_code == 200

        # Analytics should be accessible
        analytics_res = await client.get("/api/v1/analytics/usage?identity=all")
        assert analytics_res.status_code == 200
        data = analytics_res.json()
        assert "total_requests" in data

        # Delete the rule
        del_res = await client.delete(f"/api/v1/rules/{rule['id']}")
        assert del_res.status_code == 200
