from backend.middleware.response_handler import rate_limit_response


def test_rate_limit_response_structure():
    response = rate_limit_response(retry_after=30, limit=100, window="60", algorithm="fixed_window")
    assert response.status_code == 429
    body = response.body
    assert b"rate_limit_exceeded" in body
    assert b"Too many requests" in body
    assert b"30" in body
    assert b"100" in body


def test_rate_limit_response_headers():
    response = rate_limit_response(retry_after=15, limit=50, window="30", algorithm="token_bucket")
    headers = response.headers
    assert headers["Retry-After"] == "15"
    assert headers["X-RateLimit-Limit"] == "50"
    assert headers["X-RateLimit-Remaining"] == "0"
    assert headers["X-RateLimit-Reset"] == "15"
    assert headers["X-RateLimit-Algorithm"] == "token_bucket"


def test_rate_limit_response_default_algorithm():
    response = rate_limit_response(retry_after=10, limit=20, window="10")
    assert response.headers["X-RateLimit-Algorithm"] == ""
