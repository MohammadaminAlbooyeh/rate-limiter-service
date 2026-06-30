import pytest
import sqlalchemy
from backend.models.rule import Rule
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
async def test_create_and_get_rule():
    from backend.services.rule_service import RuleService
    service = RuleService()
    rule = Rule(name="test", identity="ip", algorithm="fixed_window", limit=10, window=60)
    created = await service.create_rule(rule)
    assert created.name == "test"
    assert created.limit == 10

    rules = await service.get_rules()
    assert len(rules) >= 1
    assert any(r.id == created.id for r in rules)


@pytest.mark.asyncio
async def test_get_rule_by_id():
    from backend.services.rule_service import RuleService
    service = RuleService()
    rule = Rule(name="by_id", identity="api_key", algorithm="token_bucket", limit=5, window=30)
    created = await service.create_rule(rule)
    fetched = await service.get_rule(created.id)
    assert fetched is not None
    assert fetched.name == "by_id"


@pytest.mark.asyncio
async def test_update_rule():
    from backend.services.rule_service import RuleService
    service = RuleService()
    rule = Rule(name="original", identity="ip", algorithm="fixed_window", limit=10, window=60)
    created = await service.create_rule(rule)
    updated = await service.update_rule(created.id, {"name": "updated", "limit": 20})
    assert updated is not None
    assert updated.name == "updated"
    assert updated.limit == 20
    assert updated.identity == "ip"
    assert updated.algorithm == "fixed_window"


@pytest.mark.asyncio
async def test_delete_rule():
    from backend.services.rule_service import RuleService
    service = RuleService()
    rule = Rule(name="delete_me", identity="user_id", algorithm="leaky_bucket", limit=3, window=10)
    created = await service.create_rule(rule)
    deleted = await service.delete_rule(created.id)
    assert deleted is True
    assert await service.get_rule(created.id) is None
    assert await service.delete_rule(created.id) is False
