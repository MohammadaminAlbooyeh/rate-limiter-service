import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from backend.models.database import Base
from backend.models.rule import Rule

class RuleDB(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    identity = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    limit = Column(Integer, nullable=False)
    window = Column(Integer, nullable=False)
    endpoint = Column(String, default="*")
    tier = Column(String, nullable=True)

    def to_domain(self) -> Rule:
        return Rule(
            id=self.id,
            name=self.name,
            identity=self.identity,
            algorithm=self.algorithm,
            limit=self.limit,
            window=self.window,
            endpoint=self.endpoint,
            tier=self.tier
        )

    @classmethod
    def from_domain(cls, rule: Rule) -> "RuleDB":
        return cls(
            id=rule.id,
            name=rule.name,
            identity=rule.identity,
            algorithm=rule.algorithm,
            limit=rule.limit,
            window=rule.window,
            endpoint=rule.endpoint,
            tier=rule.tier
        )

class WhitelistDB(Base):
    __tablename__ = "whitelist"

    identity = Column(String, primary_key=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BlacklistDB(Base):
    __tablename__ = "blacklist"

    identity = Column(String, primary_key=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RequestLogDB(Base):
    __tablename__ = "request_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    identity = Column(String, nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    allowed = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
