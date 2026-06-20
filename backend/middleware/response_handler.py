from fastapi.responses import JSONResponse


def rate_limit_response(retry_after: int, limit: int, window: str, algorithm: str = ""):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests",
            "retry_after": retry_after,
            "limit": limit,
            "window": window,
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(retry_after),
            "X-RateLimit-Algorithm": algorithm,
        },
    )
