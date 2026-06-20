from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.middleware.identity_extractor import extract_identity
from backend.middleware.rule_matcher import match_rule
from backend.services.limiter_service import LimiterService
from backend.utils.metrics import REQUEST_COUNT, LATENCY
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: LimiterService):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        identity = await extract_identity(request)

        # Check whitelist/blacklist
        from backend.services.whitelist_service import WhitelistService
        from backend.services.analytics_service import AnalyticsService
        
        whitelist_service = WhitelistService()
        analytics_service = AnalyticsService()

        for key in ["api_key", "user_id", "ip"]:
            val = identity.get(key)
            if val:
                if await whitelist_service.is_blacklisted(val):
                    await analytics_service.log_request(
                        identity=val,
                        endpoint=identity.get("endpoint", "*"),
                        method=identity.get("method", "GET"),
                        allowed=False
                    )
                    REQUEST_COUNT.labels(
                        identity=val,
                        endpoint=identity.get("endpoint", "*"),
                        method=identity.get("method", "GET"),
                        status="blacklisted"
                    ).inc()
                    return Response(
                        status_code=403,
                        content="Forbidden (Blacklisted)",
                    )
                if await whitelist_service.is_whitelisted(val):
                    await analytics_service.log_request(
                        identity=val,
                        endpoint=identity.get("endpoint", "*"),
                        method=identity.get("method", "GET"),
                        allowed=True
                    )
                    REQUEST_COUNT.labels(
                        identity=val,
                        endpoint=identity.get("endpoint", "*"),
                        method=identity.get("method", "GET"),
                        status="whitelisted"
                    ).inc()
                    return await call_next(request)

        rule = await match_rule(request, identity)

        if rule is None:
            ident_str = identity.get("api_key") or identity.get("user_id") or identity.get("ip") or "unknown"
            await analytics_service.log_request(
                identity=ident_str,
                endpoint=identity.get("endpoint", "*"),
                method=identity.get("method", "GET"),
                allowed=True
            )
            REQUEST_COUNT.labels(
                identity=ident_str,
                endpoint=identity.get("endpoint", "*"),
                method=identity.get("method", "GET"),
                status="no_rule_allowed"
            ).inc()
            return await call_next(request)

        # Measure rate limiter check latency
        check_start = time.time()
        allowed, remaining, reset = await self.limiter.check(identity, rule)
        LATENCY.observe(time.time() - check_start)

        ident_str = identity.get("api_key") or identity.get("user_id") or identity.get("ip") or "unknown"
        await analytics_service.log_request(
            identity=ident_str,
            endpoint=identity.get("endpoint", "*"),
            method=identity.get("method", "GET"),
            allowed=allowed
        )

        status_str = "allowed" if allowed else "blocked"
        REQUEST_COUNT.labels(
            identity=ident_str,
            endpoint=identity.get("endpoint", "*"),
            method=identity.get("method", "GET"),
            status=status_str
        ).inc()

        response = await call_next(request) if allowed else Response(
            status_code=429,
            content="Too Many Requests",
        )

        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        response.headers["X-RateLimit-Algorithm"] = rule.algorithm

        return response
