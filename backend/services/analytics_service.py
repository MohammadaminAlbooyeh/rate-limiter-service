from typing import List, Dict


class AnalyticsService:
    async def get_usage(self, identity: str) -> Dict:
        return {"identity": identity, "requests": 0, "blocked": 0}

    async def get_blocked(self) -> List[Dict]:
        return []

    async def get_top_consumers(self, limit: int = 10) -> List[Dict]:
        return []
