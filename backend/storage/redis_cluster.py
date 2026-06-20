from redis.cluster import RedisCluster as RedisClusterClient
from backend.storage.base_store import BaseStore


class RedisClusterStore(BaseStore):
    def __init__(self, startup_nodes: list):
        self.client = RedisClusterClient(startup_nodes=startup_nodes, decode_responses=True)

    async def get(self, key: str) -> int:
        val = await self.client.get(key)
        return int(val) if val else 0

    async def increment(self, key: str, ttl: int) -> int:
        val = await self.client.incr(key)
        if val == 1:
            await self.client.expire(key, ttl)
        return val

    async def ttl(self, key: str) -> int:
        return await self.client.ttl(key)

    async def remove_range_by_score(self, key: str, min: float, max: float) -> None:
        await self.client.zremrangebyscore(key, min, max)

    async def count(self, key: str) -> int:
        return await self.client.zcard(key)

    async def count_range_by_score(self, key: str, min: float, max: float) -> int:
        return await self.client.zcount(key, min, max)

    async def add_timestamp(self, key: str, timestamp: float, ttl: int) -> None:
        await self.client.zadd(key, {str(timestamp): timestamp})
        await self.client.expire(key, ttl)

    async def get_bucket(self, key: str) -> Optional[dict]:
        val = await self.client.get(key)
        if val:
            data = json.loads(val)
            return {"tokens": data["tokens"], "last_refill": data["last_refill"]}
        return None

    async def set_bucket(self, key: str, tokens: float, timestamp: float) -> None:
        data = json.dumps({"tokens": tokens, "last_refill": timestamp})
        await self.client.set(key, data)
