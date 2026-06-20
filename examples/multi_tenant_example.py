from backend.storage.memory_store import MemoryStore
from backend.algorithms.token_bucket import TokenBucketAlgorithm

store = MemoryStore()
algo = TokenBucketAlgorithm(store, refill_rate=5)

tenants = [
    ("tenant:premium", 100),
    ("tenant:free", 10),
]

for tenant_id, limit in tenants:
    for i in range(limit + 5):
        allowed = algo.allow_request(tenant_id, limit, 3600)
        print(f"{tenant_id} req {i+1}: {'✅' if allowed else '❌'}")
