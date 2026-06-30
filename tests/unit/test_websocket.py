"""
Tests for the WebSocket analytics endpoint.

Uses FastAPI's synchronous TestClient which properly supports WebSocket connections.
"""
import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import Base

from backend.utils.ws_manager import manager


@pytest.fixture(autouse=True)
def setup_db():
    """Set up a fresh SQLite database for each test."""
    sync_engine = sqlalchemy.create_engine("sqlite:///./test_ratelimit.db")
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


def test_websocket_connect_and_disconnect():
    """Test that a WebSocket can connect and disconnect properly."""
    client = TestClient(app)
    with client.websocket_connect("/ws/analytics") as ws:
        # Should be connected
        assert ws is not None
        # Connection should be tracked by manager
        assert len(manager.active_connections) >= 1


@pytest.mark.asyncio
async def test_websocket_receives_broadcast():
    """Test that analytics broadcasts are received over WebSocket (async log, sync WS)."""
    import asyncio

    client = TestClient(app)
    with client.websocket_connect("/ws/analytics") as ws:
        # Trigger a log via analytics service which broadcasts via WebSocket
        from backend.services.analytics_service import AnalyticsService
        svc = AnalyticsService()
        await svc.log_request(
            identity="test_ws_user",
            endpoint="/test",
            method="GET",
            allowed=True,
        )

        # Give the broadcast a moment to propagate
        await asyncio.sleep(0.1)

        # Should receive a broadcast message
        data = ws.receive_json()
        assert data["type"] == "log"
        assert data["data"]["identity"] == "test_ws_user"
        assert data["data"]["allowed"] is True


@pytest.mark.asyncio
async def test_websocket_multiple_clients():
    """Test that multiple WebSocket clients all receive broadcasts."""
    import asyncio

    client1 = TestClient(app)
    client2 = TestClient(app)

    with client1.websocket_connect("/ws/analytics") as ws1, \
         client2.websocket_connect("/ws/analytics") as ws2:

        from backend.services.analytics_service import AnalyticsService
        svc = AnalyticsService()
        await svc.log_request(
            identity="multi_client_test",
            endpoint="/api",
            method="POST",
            allowed=False,
        )

        await asyncio.sleep(0.1)

        msg1 = ws1.receive_json()
        msg2 = ws2.receive_json()

        assert msg1["data"]["identity"] == "multi_client_test"
        assert msg1["data"]["allowed"] is False
        assert msg2["data"]["identity"] == "multi_client_test"
        assert msg2["data"]["allowed"] is False

