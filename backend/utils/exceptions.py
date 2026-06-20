class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int, limit: int):
        self.retry_after = retry_after
        self.limit = limit
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")


class RuleNotFound(Exception):
    pass


class InvalidRule(Exception):
    pass
