from fastapi import Request, Header, HTTPException
from backend.utils.config import settings


async def get_identity(request: Request):
    return {
        "ip": request.client.host if request.client else "unknown",
        "api_key": request.headers.get("X-API-Key", ""),
        "user_id": request.headers.get("X-User-ID", ""),
        "endpoint": str(request.url.path),
        "method": request.method,
    }


async def require_admin_key(x_admin_key: str = Header("")):
    if settings.admin_api_key and x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin API key")
