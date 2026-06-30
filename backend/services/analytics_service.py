from typing import List, Dict
from sqlalchemy import func, select
from backend.models.database import async_session
from backend.models.models import RequestLogDB


class AnalyticsService:
    async def log_request(self, identity: str, endpoint: str, method: str, allowed: bool) -> None:
        async with async_session() as session:
            log_entry = RequestLogDB(
                identity=identity,
                endpoint=endpoint,
                method=method,
                allowed=allowed
            )
            session.add(log_entry)
            await session.commit()

            try:
                from backend.utils.ws_manager import manager
                await manager.broadcast({
                    "type": "log",
                    "data": {
                        "identity": identity,
                        "endpoint": endpoint,
                        "method": method,
                        "allowed": allowed,
                        "timestamp": log_entry.timestamp.isoformat()
                    }
                })
            except Exception:
                pass

    async def get_usage(self, identity: str) -> Dict:
        from sqlalchemy import case
        async with async_session() as session:
            query = select(
                func.count(RequestLogDB.id).label("total"),
                func.sum(case((RequestLogDB.allowed == True, 1), else_=0)).label("allowed"),
                func.sum(case((RequestLogDB.allowed == False, 1), else_=0)).label("blocked"),
            )
            if identity and identity != "all":
                query = query.where(RequestLogDB.identity == identity)
            
            result = await session.execute(query)
            row = result.fetchone()
            total = row[0] if row and row[0] is not None else 0
            allowed = row[1] if row and row[1] is not None else 0
            blocked = row[2] if row and row[2] is not None else 0
            
            return {
                "identity": identity or "all",
                "total_requests": total,
                "allowed_requests": allowed,
                "blocked_requests": blocked
            }

    async def get_blocked(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        async with async_session() as session:
            result = await session.execute(
                select(RequestLogDB)
                .where(RequestLogDB.allowed == False)
                .order_by(RequestLogDB.timestamp.desc())
                .offset(offset)
                .limit(limit)
            )
            logs = result.scalars().all()
            return [
                {
                    "identity": log.identity,
                    "endpoint": log.endpoint,
                    "method": log.method,
                    "timestamp": log.timestamp.isoformat(),
                }
                for log in logs
            ]

    async def get_top_consumers(self, limit: int = 10) -> List[Dict]:
        async with async_session() as session:
            result = await session.execute(
                select(
                    RequestLogDB.identity,
                    func.count(RequestLogDB.id).label("total")
                )
                .group_by(RequestLogDB.identity)
                .order_by(func.count(RequestLogDB.id).desc())
                .limit(limit)
            )
            rows = result.all()
            return [{"identity": row[0], "total_requests": row[1]} for row in rows]

    async def get_timeline(self, minutes: int = 30) -> List[Dict]:
        from datetime import datetime, timedelta
        from sqlalchemy import case
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        async with async_session() as session:
            dialect = session.bind.dialect.name if session.bind else "sqlite"
            if dialect == "postgresql":
                minute_expr = func.date_trunc("minute", RequestLogDB.timestamp).label("minute")
            else:
                minute_expr = func.strftime("%Y-%m-%d %H:%M", RequestLogDB.timestamp).label("minute")
            result = await session.execute(
                select(
                    minute_expr,
                    func.count(RequestLogDB.id).label("total"),
                    func.sum(case((RequestLogDB.allowed == False, 1), else_=0)).label("blocked"),
                )
                .where(RequestLogDB.timestamp >= cutoff)
                .group_by("minute")
                .order_by("minute")
            )
            rows = result.all()
            return [
                {"time": row[0], "total": row[1], "blocked": row[2] if row[2] else 0}
                for row in rows
            ]
