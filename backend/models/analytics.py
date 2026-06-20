class Analytics:
    def __init__(
        self,
        identity: str,
        total_requests: int = 0,
        blocked_requests: int = 0,
        allowed_requests: int = 0,
    ):
        self.identity = identity
        self.total_requests = total_requests
        self.blocked_requests = blocked_requests
        self.allowed_requests = allowed_requests
