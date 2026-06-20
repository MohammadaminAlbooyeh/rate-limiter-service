from datetime import datetime


class RequestLog:
    def __init__(
        self,
        identity: str,
        endpoint: str,
        method: str,
        allowed: bool,
        timestamp: datetime = None,
    ):
        self.identity = identity
        self.endpoint = endpoint
        self.method = method
        self.allowed = allowed
        self.timestamp = timestamp or datetime.utcnow()
