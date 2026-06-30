import pytest
from unittest.mock import Mock, patch
from backend.models.rule import Rule


@pytest.mark.asyncio
async def test_match_rule_by_ip():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="ip_rule", identity="ip", algorithm="fixed_window", limit=10, window=60)
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/api"}
    assert _matches(rule, identity) is True


@pytest.mark.asyncio
async def test_match_rule_by_api_key():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="key_rule", identity="api_key", algorithm="fixed_window", limit=10, window=60)
    identity = {"ip": "10.0.0.1", "api_key": "abc", "user_id": "", "endpoint": "/api"}
    assert _matches(rule, identity) is True


@pytest.mark.asyncio
async def test_match_rule_by_user_id():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="user_rule", identity="user_id", algorithm="fixed_window", limit=10, window=60)
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "42", "endpoint": "/api"}
    assert _matches(rule, identity) is True


@pytest.mark.asyncio
async def test_no_match_wrong_endpoint():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="specific", identity="ip", algorithm="fixed_window", limit=10, window=60, endpoint="/admin")
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/api"}
    assert _matches(rule, identity) is False


@pytest.mark.asyncio
async def test_no_match_wrong_identity_type():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="key_rule", identity="api_key", algorithm="fixed_window", limit=10, window=60)
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/api"}
    assert _matches(rule, identity) is False


@pytest.mark.asyncio
async def test_match_any_endpoint():
    from backend.middleware.rule_matcher import _matches
    rule = Rule(name="catch_all", identity="ip", algorithm="fixed_window", limit=10, window=60, endpoint="*")
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/anything"}
    assert _matches(rule, identity) is True


@pytest.mark.asyncio
@patch("backend.services.rule_service.RuleService.get_rules")
async def test_match_rule_returns_rule(mock_get_rules):
    from backend.middleware.rule_matcher import match_rule
    from unittest.mock import Mock
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=5, window=60, endpoint="*")
    mock_get_rules.return_value = [rule]

    request = Mock()
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/test"}

    result = await match_rule(request, identity)
    assert result is not None
    assert result.name == "test"


@pytest.mark.asyncio
@patch("backend.services.rule_service.RuleService.get_rules")
async def test_match_rule_no_match_returns_none(mock_get_rules):
    from backend.middleware.rule_matcher import match_rule
    from unittest.mock import Mock
    mock_get_rules.return_value = []

    request = Mock()
    identity = {"ip": "10.0.0.1", "api_key": "", "user_id": "", "endpoint": "/test"}

    result = await match_rule(request, identity)
    assert result is None
