from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.models.database import init_db, engine, async_session
from backend.utils.ws_manager import manager
from backend.utils.config import settings
from backend.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.services.limiter_service import LimiterService
import logging

logger = logging.getLogger("ratelimiter.main")

limiter = LimiterService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    try:
        await limiter.close()
    except Exception as e:
        logger.warning(f"Error closing limiter connections: {e}")
    try:
        await engine.dispose()
    except Exception as e:
        logger.warning(f"Error disposing database engine: {e}")


app = FastAPI(
    title="Rate Limiter Service",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

excluded_paths = {"/health", "/metrics", "/docs", "/openapi.json", "/ws/analytics", "/api/v1/check"}
app.add_middleware(RateLimitMiddleware, limiter=limiter, exclude_paths=excluded_paths)

app.include_router(router)


@app.websocket("/ws/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
async def health():
    db_ok = False
    redis_ok = False
    try:
        from sqlalchemy import text
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning(f"Health check - DB not available: {e}")

    if settings.use_redis or settings.use_redis_cluster:
        try:
            if hasattr(limiter.store, "client") and hasattr(limiter.store.client, "ping"):
                await limiter.store.client.ping()
                redis_ok = True
        except Exception as e:
            logger.warning(f"Health check - Redis not available: {e}")
    else:
        redis_ok = True

    status = "ok" if db_ok else "degraded"
    return {
        "status": status,
        "database": db_ok,
        "redis": redis_ok,
    }
