from starlette.requests import Request


async def extract_identity(request: Request) -> dict:
    ip = request.client.host if request.client else "unknown"
    api_key = request.headers.get("X-API-Key", "")
    user_id = request.headers.get("X-User-ID", "")
    endpoint = str(request.url.path)
    method = request.method

    return {
        "ip": ip,
        "api_key": api_key,
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
    }
