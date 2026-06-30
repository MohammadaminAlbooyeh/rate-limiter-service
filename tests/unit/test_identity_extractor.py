import pytest
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_extract_ip():
    from backend.middleware.identity_extractor import extract_identity
    request = Mock()
    request.client.host = "10.0.0.1"
    request.headers.get = lambda h, d="": {"X-API-Key": "", "X-User-ID": ""}.get(h, d)
    request.url.path = "/api/test"
    request.method = "POST"

    identity = await extract_identity(request)
    assert identity["ip"] == "10.0.0.1"
    assert identity["api_key"] == ""
    assert identity["user_id"] == ""
    assert identity["endpoint"] == "/api/test"
    assert identity["method"] == "POST"


@pytest.mark.asyncio
async def test_extract_no_client():
    from backend.middleware.identity_extractor import extract_identity
    request = Mock()
    request.client = None
    request.headers.get = lambda h, d="": {"X-API-Key": "key-123", "X-User-ID": "user-abc"}.get(h, d)
    request.url.path = "/"
    request.method = "GET"

    identity = await extract_identity(request)
    assert identity["ip"] == "unknown"
    assert identity["api_key"] == "key-123"
    assert identity["user_id"] == "user-abc"


@pytest.mark.asyncio
async def test_extract_headers_present():
    from backend.middleware.identity_extractor import extract_identity
    request = Mock()
    request.client.host = "10.0.0.2"
    request.headers.get = lambda h, d="": {"X-API-Key": "admin-key", "X-User-ID": "42"}.get(h, d)
    request.url.path = "/secure"
    request.method = "DELETE"

    identity = await extract_identity(request)
    assert identity["api_key"] == "admin-key"
    assert identity["user_id"] == "42"
