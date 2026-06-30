import pytest
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.models.database import Base


@pytest.fixture(autouse=True)
def setup_db():
    sync_engine = sqlalchemy.create_engine("sqlite:///./test_ratelimit.db")
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest.mark.asyncio
async def test_middleware_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        rule_res = await client.post("/api/v1/rules", json={
            "name": "Header Test",
            "identity": "ip",
            "algorithm": "fixed_window",
            "limit": 10,
            "window": 60,
            "endpoint": "/api/data",
        })
        assert rule_res.status_code == 200

        health_res = await client.get("/health")
        assert health_res.status_code == 200

        res = await client.get("/api/data", headers={"X-API-Key": "test-key-123"})
        assert res.headers.get("X-RateLimit-Limit") is not None or res.status_code in (200, 429)
        if res.status_code == 200:
            assert "X-RateLimit-Remaining" in res.headers
            assert "X-RateLimit-Reset" in res.headers
            assert "X-RateLimit-Algorithm" in res.headers

        metrics_res = await client.get("/metrics")
        assert metrics_res.status_code == 200


@pytest.mark.asyncio
async def test_middleware_blacklist_returns_403():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/v1/blacklist", json={
            "identity": "10.0.0.99",
            "reason": "test block",
        })

        res = await client.get("/api/test", headers={"X-API-Key": "10.0.0.99"})
        assert res.status_code == 403
        assert "Forbidden" in res.text


@pytest.mark.asyncio
async def test_middleware_rate_limit_returns_429():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/v1/rules", json={
            "name": "Strict Limit",
            "identity": "ip",
            "algorithm": "fixed_window",
            "limit": 2,
            "window": 60,
            "endpoint": "/api/strict",
        })

        for _ in range(2):
            res = await client.get("/api/strict")
            assert res.status_code == 200

        res = await client.get("/api/strict")
        assert res.status_code == 429
        assert "X-RateLimit-Limit" in res.headers
        assert res.headers["X-RateLimit-Limit"] == "2"
        assert res.headers["X-RateLimit-Remaining"] == "0"


@pytest.mark.asyncio
async def test_middleware_excluded_path_skips_rate_limit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert "X-RateLimit-Limit" not in res.headers
