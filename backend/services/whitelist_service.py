from sqlalchemy.future import select
from backend.models.database import async_session
from backend.models.models import WhitelistDB, BlacklistDB


class WhitelistService:
    async def is_whitelisted(self, identity: str) -> bool:
        async with async_session() as session:
            result = await session.execute(select(WhitelistDB).where(WhitelistDB.identity == identity))
            return result.scalar_one_or_none() is not None

    async def is_blacklisted(self, identity: str) -> bool:
        async with async_session() as session:
            result = await session.execute(select(BlacklistDB).where(BlacklistDB.identity == identity))
            return result.scalar_one_or_none() is not None

    async def add_whitelist(self, identity: str, reason: str = "") -> None:
        async with async_session() as session:
            db_item = WhitelistDB(identity=identity, reason=reason)
            await session.merge(db_item)
            await session.commit()

    async def add_blacklist(self, identity: str, reason: str = "") -> None:
        async with async_session() as session:
            db_item = BlacklistDB(identity=identity, reason=reason)
            await session.merge(db_item)
            await session.commit()

    async def remove_whitelist(self, identity: str) -> bool:
        async with async_session() as session:
            result = await session.execute(select(WhitelistDB).where(WhitelistDB.identity == identity))
            db_item = result.scalar_one_or_none()
            if db_item:
                await session.delete(db_item)
                await session.commit()
                return True
        return False

    async def remove_blacklist(self, identity: str) -> bool:
        async with async_session() as session:
            result = await session.execute(select(BlacklistDB).where(BlacklistDB.identity == identity))
            db_item = result.scalar_one_or_none()
            if db_item:
                await session.delete(db_item)
                await session.commit()
                return True
        return False

    async def get_all_whitelist(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(WhitelistDB).order_by(WhitelistDB.created_at.desc()))
            rows = result.scalars().all()
            return [
                {"identity": r.identity, "reason": r.reason or "", "created_at": r.created_at.isoformat()}
                for r in rows
            ]

    async def get_all_blacklist(self) -> list[dict]:
        async with async_session() as session:
            result = await session.execute(select(BlacklistDB).order_by(BlacklistDB.created_at.desc()))
            rows = result.scalars().all()
            return [
                {"identity": r.identity, "reason": r.reason or "", "created_at": r.created_at.isoformat()}
                for r in rows
            ]
