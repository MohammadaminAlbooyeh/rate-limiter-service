from fastapi import APIRouter, HTTPException, Depends, Request
from backend.api.schemas import (
    RuleCreate, RuleUpdate, RuleResponse,
    WhitelistRequest, BlacklistRequest,
    AnalyticsResponse, CheckRequest, AlertResponse, TimelinePoint,
    SimulateRequest, SimulateResponse
)
from backend.api.dependencies import require_admin_key
from backend.services.limiter_service import LimiterService
from backend.services.rule_service import RuleService
from backend.services.whitelist_service import WhitelistService
from backend.services.analytics_service import AnalyticsService
from backend.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1")

# RuleService and other stateless services can stay as module-level singletons
rule_service = RuleService()
whitelist_service = WhitelistService()
analytics_service = AnalyticsService()
alert_service = AlertService()


@router.post("/simulate", response_model=SimulateResponse)
async def simulate_rate_limit(req: SimulateRequest):
    identity = {
        "ip": req.ip,
        "api_key": req.api_key,
        "user_id": req.user_id,
        "endpoint": req.endpoint,
        "method": req.method,
    }
    
    # Use temporary store for simulation (isolated from live state)
    from backend.storage.memory_store import MemoryStore
    temp_store = MemoryStore()
    temp_limiter = LimiterService(store=temp_store)
    
    # Create temporary rule from request
    rule = req.rule.to_model()
    
    # Simulate rate limit check
    allowed, remaining, reset = await temp_limiter.check(identity, rule)
    
    # Clean up temporary limiter
    await temp_limiter.close()
    
    return {
        "allowed": allowed,
        "remaining": remaining,
        "reset": reset
    }


@router.post("/check")
async def check_rate_limit(req: CheckRequest, request: Request):
    limiter = request.app.state.limiter
    identity = {
        "ip": req.ip,
        "api_key": req.api_key,
        "user_id": req.user_id,
        "endpoint": req.endpoint,
        "method": req.method,
    }

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
                    "X-RateLimit-Limit": str(rule.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "X-RateLimit-Algorithm": rule.algorithm,
                    "Retry-After": str(reset),
                },
            )
    return {"allowed": True}


@router.post("/reset/{identity}", dependencies=[Depends(require_admin_key)])
async def reset_limit(identity: str, request: Request):
    limiter = request.app.state.limiter
    await limiter.reset_identity(identity)
    return {"reset": True}


@router.get("/rules", response_model=list[RuleResponse])
async def list_rules():
    return await rule_service.get_rules()


@router.post("/rules", response_model=RuleResponse, dependencies=[Depends(require_admin_key)])
async def create_rule(rule: RuleCreate):
    return await rule_service.create_rule(rule.to_model())


@router.put("/rules/{rule_id}", response_model=RuleResponse, dependencies=[Depends(require_admin_key)])
async def update_rule(rule_id: str, rule: RuleUpdate):
    updated = await rule_service.update_rule(rule_id, rule.to_model())
    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated


@router.delete("/rules/{rule_id}", dependencies=[Depends(require_admin_key)])
async def delete_rule(rule_id: str):
    deleted = await rule_service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"deleted": True}


@router.post("/whitelist", dependencies=[Depends(require_admin_key)])
async def add_whitelist(req: WhitelistRequest):
    await whitelist_service.add_whitelist(req.identity, req.reason)
    return {"added": True}


@router.post("/blacklist", dependencies=[Depends(require_admin_key)])
async def add_blacklist(req: BlacklistRequest):
    await whitelist_service.add_blacklist(req.identity, req.reason)
    return {"added": True}


@router.delete("/whitelist/{identity}", dependencies=[Depends(require_admin_key)])
async def remove_whitelist(identity: str):
    removed = await whitelist_service.remove_whitelist(identity)
    if not removed:
        raise HTTPException(status_code=404, detail="Not found")
    return {"removed": True}


@router.delete("/blacklist/{identity}", dependencies=[Depends(require_admin_key)])
async def remove_blacklist(identity: str):
    removed = await whitelist_service.remove_blacklist(identity)
    if not removed:
        raise HTTPException(status_code=404, detail="Not found")
    return {"removed": True}


@router.get("/analytics/usage", dependencies=[Depends(require_admin_key)])
async def usage_stats(identity: str = ""):
    return await analytics_service.get_usage(identity)


@router.get("/analytics/blocked", dependencies=[Depends(require_admin_key)])
async def blocked_requests():
    return await analytics_service.get_blocked()


@router.get("/analytics/top", dependencies=[Depends(require_admin_key)])
async def top_consumers(limit: int = 10):
    return await analytics_service.get_top_consumers(limit)


@router.get("/analytics/timeline", dependencies=[Depends(require_admin_key)])
async def usage_timeline(minutes: int = 30):
    return await analytics_service.get_timeline(minutes)


@router.get("/alerts", response_model=list[AlertResponse], dependencies=[Depends(require_admin_key)])
async def get_alerts():
    return await alert_service.get_alerts()


@router.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
