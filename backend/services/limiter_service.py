from backend.algorithms import (
    FixedWindowAlgorithm,
    SlidingWindowLogAlgorithm,
    SlidingWindowCounterAlgorithm,
    TokenBucketAlgorithm,
    LeakyBucketAlgorithm,
)
from backend.storage.redis_store import RedisStore
from backend.storage.memory_store import MemoryStore
from backend.models.rule import Rule
from backend.utils.config import settings


class LimiterService:
    def __init__(self):
        self.store = RedisStore() if settings.use_redis else MemoryStore()
        self.algorithms = {
            "fixed_window": FixedWindowAlgorithm(self.store),
            "sliding_window_log": SlidingWindowLogAlgorithm(self.store),
            "sliding_window_counter": SlidingWindowCounterAlgorithm(self.store),
            "token_bucket": TokenBucketAlgorithm(self.store),
            "leaky_bucket": LeakyBucketAlgorithm(self.store),
        }

    async def check(self, identity: dict, rule: Rule):
        algo = self.algorithms[rule.algorithm]
        key = f"rate_limit:{identity[rule.identity]}:{rule.endpoint}"
        allowed = await algo.allow_request(key, rule.limit, rule.window)
        remaining = await algo.get_remaining(key, rule.limit, rule.window)
        reset = await algo.get_reset_time(key, rule.window)
        return allowed, remaining, reset
