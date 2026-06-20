from typing import List, Optional
from backend.models.rule import Rule


class RuleService:
    def __init__(self):
        self._rules: List[Rule] = []

    async def get_rules(self) -> List[Rule]:
        return self._rules

    async def get_rule(self, rule_id: str) -> Optional[Rule]:
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    async def create_rule(self, rule: Rule) -> Rule:
        self._rules.append(rule)
        return rule

    async def update_rule(self, rule_id: str, rule: Rule) -> Optional[Rule]:
        for i, r in enumerate(self._rules):
            if r.id == rule_id:
                self._rules[i] = rule
                return rule
        return None

    async def delete_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self._rules):
            if r.id == rule_id:
                self._rules.pop(i)
                return True
        return False
