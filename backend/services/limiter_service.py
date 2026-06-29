import time
from typing import Optional
from backend.algorithms import (
    FixedWindowAlgorithm,
    SlidingWindowLogAlgorithm,
    SlidingWindowCounterAlgorithm,
    TokenBucketAlgorithm,
    LeakyBucketAlgorithm,
)
from backend.storage.base_store import BaseStore
from backend.storage.redis_store import RedisStore
from backend.storage.redis_cluster import RedisClusterStore
from backend.storage.memory_store import MemoryStore
from backend.models.rule import Rule
from backend.utils.config import settings
import logging

logger = logging.getLogger("ratelimiter.limiter_service")


class LimiterService:
    def __init__(self, store: Optional[BaseStore] = None):
        if store is not None:
            self.store = store
        elif settings.use_redis_cluster:
            nodes = [n.strip() for n in settings.redis_cluster_nodes.split(",") if n.strip()]
            startup_nodes = []
            for node in nodes:
                host, port = node.split(":")
                startup_nodes.append((host, int(port)))
            self.store = RedisClusterStore(startup_nodes)
        elif settings.use_redis:
            self.store = RedisStore()
        else:
            self.store = MemoryStore()
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

    async def reset_identity(self, identity_value: str):
        pattern = f"rate_limit:{identity_value}:*"
        await self.store.delete_by_pattern(pattern)

    async def close(self):
        if hasattr(self.store, "client") and hasattr(self.store.client, "aclose"):
            try:
                await self.store.client.aclose()
            except Exception as e:
                logger.warning(f"Error closing store client: {e}")
