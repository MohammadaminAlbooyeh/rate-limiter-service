from backend.storage.redis_store import RedisStore
from backend.algorithms.sliding_window_counter import SlidingWindowCounterAlgorithm

store = RedisStore()
algo = SlidingWindowCounterAlgorithm(store)

key = "distributed:user:1:api:/data"

allowed = algo.allow_request(key, 1000, 60)
print(f"Request {'allowed' if allowed else 'blocked'}")
