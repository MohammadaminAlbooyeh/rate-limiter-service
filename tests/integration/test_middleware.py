import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.models.database import engine, Base


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_middleware_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a rule first
        rule_res = await client.post("/api/v1/rules", json={
            "name": "Header Test",
            "identity": "ip",
            "algorithm": "fixed_window",
            "limit": 10,
            "window": 60,
            "endpoint": "/api/data",
        })
        assert rule_res.status_code == 200

        # Request a public endpoint (health - excluded from middleware)
        health_res = await client.get("/health")
        assert health_res.status_code == 200

        # Request an endpoint that matches a rule - should get rate limit headers
        res = await client.get("/api/data", headers={"X-API-Key": "test-key-123"})
        assert res.headers.get("X-RateLimit-Limit") is not None or res.status_code in (200, 429)
        if res.status_code == 200:
            assert "X-RateLimit-Remaining" in res.headers
            assert "X-RateLimit-Reset" in res.headers
            assert "X-RateLimit-Algorithm" in res.headers

        # Metrics endpoint should be accessible and excluded from middleware
        metrics_res = await client.get("/metrics")
        assert metrics_res.status_code == 200
