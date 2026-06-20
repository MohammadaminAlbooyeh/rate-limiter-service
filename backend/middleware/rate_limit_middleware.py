from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.middleware.identity_extractor import extract_identity
from backend.middleware.rule_matcher import match_rule
from backend.services.limiter_service import LimiterService


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: LimiterService):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next) -> Response:
        identity = await extract_identity(request)
        rule = await match_rule(request, identity)

        if rule is None:
            return await call_next(request)

        allowed, remaining, reset = await self.limiter.check(identity, rule)

        response = await call_next(request) if allowed else Response(
            status_code=429,
            content="Too Many Requests",
        )

        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        response.headers["X-RateLimit-Algorithm"] = rule.algorithm

        return response
