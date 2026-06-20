from backend.services.rule_service import RuleService


class RuleLoader:
    def __init__(self):
        self.service = RuleService()

    async def load(self):
        return await self.service.get_rules()
