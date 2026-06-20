from fastapi import Request


async def get_identity(request: Request):
    return {
        "ip": request.client.host if request.client else "unknown",
        "api_key": request.headers.get("X-API-Key", ""),
        "user_id": request.headers.get("X-User-ID", ""),
        "endpoint": str(request.url.path),
        "method": request.method,
    }
