from pydantic import BaseModel
from typing import Optional, List
from backend.models.rule import Rule


class RuleCreate(BaseModel):
    name: str
    identity: str
    algorithm: str
    limit: int
    window: int
    endpoint: str = "*"
    tier: Optional[str] = None

    def to_model(self) -> Rule:
        return Rule(
            name=self.name,
            identity=self.identity,
            algorithm=self.algorithm,
            limit=self.limit,
            window=self.window,
            endpoint=self.endpoint,
            tier=self.tier,
        )


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    limit: Optional[int] = None
    window: Optional[int] = None
    endpoint: Optional[str] = None
    tier: Optional[str] = None

    def to_model(self) -> Rule:
        return Rule(
            name=self.name or "",
            identity="",
            algorithm="",
            limit=self.limit or 0,
            window=self.window or 0,
            endpoint=self.endpoint or "*",
            tier=self.tier,
        )


class RuleResponse(BaseModel):
    id: str
    name: str
    identity: str
    algorithm: str
    limit: int
    window: int
    endpoint: str
    tier: Optional[str] = None


class WhitelistRequest(BaseModel):
    identity: str
    reason: str = ""


class BlacklistRequest(BaseModel):
    identity: str
    reason: str = ""


class AnalyticsResponse(BaseModel):
    identity: str
    requests: int
    blocked: int


class CheckRequest(BaseModel):
    endpoint: str = "*"
    method: str = "GET"
    ip: str = ""
    api_key: str = ""
    user_id: str = ""


class AlertResponse(BaseModel):
    identity: str
    current: int
    limit: int
    threshold: str


class TimelinePoint(BaseModel):
    time: str
    total: int
    blocked: int
