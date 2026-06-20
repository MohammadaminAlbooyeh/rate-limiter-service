from typing import Optional
import uuid


class Rule:
    def __init__(
        self,
        name: str,
        identity: str,
        algorithm: str,
        limit: int,
        window: int,
        endpoint: str = "*",
        tier: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.identity = identity
        self.algorithm = algorithm
        self.limit = limit
        self.window = window
        self.endpoint = endpoint
        self.tier = tier
