from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.api.routes import router
from backend.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Rate Limiter Service",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
