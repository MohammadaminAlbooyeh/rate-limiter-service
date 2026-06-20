from typing import Dict, Optional


class WhitelistService:
    def __init__(self):
        self._whitelist: Dict[str, str] = {}
        self._blacklist: Dict[str, str] = {}

    async def is_whitelisted(self, identity: str) -> bool:
        return identity in self._whitelist

    async def is_blacklisted(self, identity: str) -> bool:
        return identity in self._blacklist

    async def add_whitelist(self, identity: str, reason: str = "") -> None:
        self._whitelist[identity] = reason

    async def add_blacklist(self, identity: str, reason: str = "") -> None:
        self._blacklist[identity] = reason

    async def remove_whitelist(self, identity: str) -> bool:
        return self._whitelist.pop(identity, None) is not None

    async def remove_blacklist(self, identity: str) -> bool:
        return self._blacklist.pop(identity, None) is not None
