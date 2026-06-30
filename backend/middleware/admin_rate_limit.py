"""
Self-rate-limiting middleware for the admin/management API.

Protects management endpoints from abuse by applying a simple
in-memory fixed-window rate limit per API key or IP address.

This is separate from the main RateLimitMiddleware and applies
only to endpoints under /api/v1 that require admin authentication.
"""
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException, Depends
from backend.api.dependencies import require_admin_key

logger = logging.getLogger("ratelimiter.admin_rate_limit")

# In-memory store: {client_key: (window_start, count)}
_admin_rate_store: Dict[str, Tuple[float, int]] = {}

# Default limits for admin API
ADMIN_RATE_LIMIT = 60  # requests
ADMIN_RATE_WINDOW = 60  # seconds


async def admin_rate_limit_dependency(
    request: Request,
    _=Depends(require_admin_key),
) -> None:
    """
    FastAPI dependency that rate-limits admin API calls per client.

    Uses the admin API key (or IP as fallback) as the client identifier.
    Applies a simple fixed-window counter in memory.
    """
    client_id = request.headers.get("X-Admin-Key") or request.client.host if request.client else "unknown"

    now = time.time()
    window_start, count = _admin_rate_store.get(client_id, (0, 0))

    # Reset window if expired
    if now - window_start > ADMIN_RATE_WINDOW:
        window_start = now
        count = 0

    count += 1
    _admin_rate_store[client_id] = (window_start, count)

    if count > ADMIN_RATE_LIMIT:
        retry_after = int(window_start + ADMIN_RATE_WINDOW - now)
        logger.warning(f"Admin rate limit exceeded for client {client_id[:8]}...")
        raise HTTPException(
            status_code=429,
            detail="Admin API rate limit exceeded. Please slow down.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(ADMIN_RATE_LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(retry_after),
            },
        )


def get_admin_rate_limit_remaining(request: Request) -> int:
    """
    Get the remaining requests for the current client.
    Useful for response headers.
    """
    client_id = request.headers.get("X-Admin-Key") or (request.client.host if request.client else "unknown")
    now = time.time()
    window_start, count = _admin_rate_store.get(client_id, (0, 0))
    if now - window_start > ADMIN_RATE_WINDOW:
        return ADMIN_RATE_LIMIT
    return max(0, ADMIN_RATE_LIMIT - count)
