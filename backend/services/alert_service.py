from typing import List, Dict


class AlertService:
    def __init__(self):
        self._alerts: List[Dict] = []

    async def check_threshold(self, identity: str, current: int, limit: int) -> bool:
        if current >= limit * 0.9:
            self._alerts.append({
                "identity": identity,
                "current": current,
                "limit": limit,
                "threshold": "90%",
            })
            return True
        return False

    async def get_alerts(self) -> List[Dict]:
        return self._alerts
