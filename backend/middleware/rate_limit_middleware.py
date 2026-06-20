from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.middleware.identity_extractor import extract_identity
from backend.middleware.rule_matcher import match_rule
from backend.middleware.response_handler import rate_limit_response
from backend.services.limiter_service import LimiterService
from backend.utils.metrics import REQUEST_COUNT, LATENCY
import time
import logging

logger = logging.getLogger("ratelimiter.middleware")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: LimiterService, exclude_paths: set = None):
        super().__init__(app)
        self.limiter = limiter
        self.exclude_paths = exclude_paths or set()

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        try:
            identity = await extract_identity(request)
        except Exception as e:
            logger.error(f"RateLimiter identity extraction failed: {e}")
            return await call_next(request)

        # Check whitelist/blacklist with fail-open fallback
        try:
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
        except Exception as e:
            logger.error(f"RateLimiter whitelist/blacklist check failed: {e}")

        try:
            rule = await match_rule(request, identity)
        except Exception as e:
            logger.error(f"RateLimiter rule matching failed: {e}")
            return await call_next(request)

        if rule is None:
            try:
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
            except Exception as e:
                pass
            return await call_next(request)

        try:
            # Measure rate limiter check latency
            check_start = time.time()
            allowed, remaining, reset = await self.limiter.check(identity, rule)
            LATENCY.observe(time.time() - check_start)

            # Alert integration (checks if capacity matches or exceeds 90%)
            if remaining <= rule.limit * 0.1:
                try:
                    from backend.services.alert_service import AlertService
                    alert_service = AlertService()
                    ident_str = identity.get("api_key") or identity.get("user_id") or identity.get("ip") or "unknown"
                    await alert_service.check_threshold(ident_str, rule.limit - remaining, rule.limit)
                except Exception as alert_err:
                    logger.error(f"RateLimiter AlertService error: {alert_err}")

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

        except Exception as e:
            logger.error(f"RateLimiter check/logging failed (FAIL-OPEN): {e}")
            return await call_next(request)

        response = await call_next(request) if allowed else rate_limit_response(reset, rule.limit, str(rule.window), rule.algorithm)

        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        response.headers["X-RateLimit-Algorithm"] = rule.algorithm

        return response
