from typing import List, Dict
from sqlalchemy.future import select
from backend.models.database import async_session
from backend.models.models import AlertDB


class AlertService:
    async def check_threshold(self, identity: str, current: int, limit: int) -> bool:
        if current >= limit * 0.9:
            async with async_session() as session:
                alert = AlertDB(
                    identity=identity,
                    current=current,
                    limit=limit,
                    threshold="90%",
                )
                session.add(alert)
                await session.commit()
            return True
        return False

    async def get_alerts(self) -> List[Dict]:
        async with async_session() as session:
            result = await session.execute(
                select(AlertDB).order_by(AlertDB.created_at.desc()).limit(100)
            )
            rows = result.scalars().all()
            return [
                {
                    "identity": r.identity,
                    "current": r.current,
                    "limit": r.limit,
                    "threshold": r.threshold,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
