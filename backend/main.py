from fastapi import FastAPI
from backend.api.routes import router
from backend.utils.config import settings

app = FastAPI(
    title="Rate Limiter Service",
    version="1.0.0",
    docs_url="/docs",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
