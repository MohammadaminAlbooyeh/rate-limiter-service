from typing import List, Optional
from sqlalchemy.future import select
from backend.models.database import async_session
from backend.models.models import RuleDB
from backend.models.rule import Rule


class RuleService:
    async def get_rules(self) -> List[Rule]:
        async with async_session() as session:
            result = await session.execute(select(RuleDB))
            rules = result.scalars().all()
            return [r.to_domain() for r in rules]

    async def get_rule(self, rule_id: str) -> Optional[Rule]:
        async with async_session() as session:
            result = await session.execute(select(RuleDB).where(RuleDB.id == rule_id))
            rule_db = result.scalar_one_or_none()
            return rule_db.to_domain() if rule_db else None

    async def create_rule(self, rule: Rule) -> Rule:
        db_rule = RuleDB.from_domain(rule)
        async with async_session() as session:
            session.add(db_rule)
            await session.commit()
            return db_rule.to_domain()

    async def update_rule(self, rule_id: str, rule: Rule) -> Optional[Rule]:
        async with async_session() as session:
            result = await session.execute(select(RuleDB).where(RuleDB.id == rule_id))
            rule_db = result.scalar_one_or_none()
            if rule_db:
                rule_db.name = rule.name
                rule_db.identity = rule.identity
                rule_db.algorithm = rule.algorithm
                rule_db.limit = rule.limit
                rule_db.window = rule.window
                rule_db.endpoint = rule.endpoint
                rule_db.tier = rule.tier
                await session.commit()
                return rule_db.to_domain()
        return None

    async def delete_rule(self, rule_id: str) -> bool:
        async with async_session() as session:
            result = await session.execute(select(RuleDB).where(RuleDB.id == rule_id))
            rule_db = result.scalar_one_or_none()
            if rule_db:
                await session.delete(rule_db)
                await session.commit()
                return True
        return False
