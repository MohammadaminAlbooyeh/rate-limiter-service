from backend.rules.rule_loader import RuleLoader
from backend.rules.rule_validator import RuleValidator


class RuleEngine:
    def __init__(self):
        self.loader = RuleLoader()
        self.validator = RuleValidator()

    async def evaluate(self, identity: dict):
        rules = await self.loader.load()
        for rule in rules:
            if self.validator.matches(rule, identity):
                return rule
        return None
