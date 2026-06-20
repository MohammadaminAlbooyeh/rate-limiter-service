from fastapi import APIRouter, HTTPException
from backend.api.schemas import (
    RuleCreate, RuleUpdate, RuleResponse,
    WhitelistRequest, BlacklistRequest,
    AnalyticsResponse,
)
from backend.services.limiter_service import LimiterService
from backend.services.rule_service import RuleService
from backend.services.whitelist_service import WhitelistService
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/v1")

limiter = LimiterService()
rule_service = RuleService()
whitelist_service = WhitelistService()
analytics_service = AnalyticsService()


@router.post("/check")
async def check_rate_limit(identity: dict):
    # Check whitelist/blacklist
    for key in ["api_key", "user_id", "ip"]:
        val = identity.get(key)
        if val:
            if await whitelist_service.is_blacklisted(val):
                raise HTTPException(status_code=403, detail="Forbidden (Blacklisted)")
            if await whitelist_service.is_whitelisted(val):
                return {"allowed": True}

    rules = await rule_service.get_rules()
    for rule in rules:
        allowed, remaining, reset = await limiter.check(identity, rule)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="rate_limit_exceeded",
                headers={
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(reset),
                },
            )
    return {"allowed": True}


@router.post("/reset/{identity}")
async def reset_limit(identity: str):
    return {"reset": True}


@router.get("/rules", response_model=list[RuleResponse])
async def list_rules():
    return await rule_service.get_rules()


@router.post("/rules", response_model=RuleResponse)
async def create_rule(rule: RuleCreate):
    return await rule_service.create_rule(rule.to_model())


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str, rule: RuleUpdate):
    updated = await rule_service.update_rule(rule_id, rule.to_model())
    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    deleted = await rule_service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"deleted": True}


@router.post("/whitelist")
async def add_whitelist(req: WhitelistRequest):
    await whitelist_service.add_whitelist(req.identity, req.reason)
    return {"added": True}


@router.post("/blacklist")
async def add_blacklist(req: BlacklistRequest):
    await whitelist_service.add_blacklist(req.identity, req.reason)
    return {"added": True}


@router.delete("/whitelist/{identity}")
async def remove_whitelist(identity: str):
    removed = await whitelist_service.remove_whitelist(identity)
    if not removed:
        raise HTTPException(status_code=404, detail="Not found")
    return {"removed": True}


@router.delete("/blacklist/{identity}")
async def remove_blacklist(identity: str):
    removed = await whitelist_service.remove_blacklist(identity)
    if not removed:
        raise HTTPException(status_code=404, detail="Not found")
    return {"removed": True}


@router.get("/analytics/usage")
async def usage_stats(identity: str = ""):
    return await analytics_service.get_usage(identity)


@router.get("/analytics/blocked")
async def blocked_requests():
    return await analytics_service.get_blocked()


@router.get("/analytics/top")
async def top_consumers(limit: int = 10):
    return await analytics_service.get_top_consumers(limit)


@router.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
