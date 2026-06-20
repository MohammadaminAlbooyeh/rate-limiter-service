from backend.storage.memory_store import MemoryStore
from backend.algorithms.fixed_window import FixedWindowAlgorithm

store = MemoryStore()
algo = FixedWindowAlgorithm(store)

key = "user:123:api:/data"
limit = 5
window = 60

for i in range(7):
    allowed = algo.allow_request(key, limit, window)
    print(f"Request {i+1}: {'✅ ALLOWED' if allowed else '❌ BLOCKED'}")
