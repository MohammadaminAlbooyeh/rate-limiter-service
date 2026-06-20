from starlette.requests import Request


async def match_rule(request: Request, identity: dict):
    from backend.services.rule_service import RuleService
    service = RuleService()
    rules = await service.get_rules()
    for rule in rules:
        if _matches(rule, identity):
            return rule
    return None


def _matches(rule, identity: dict) -> bool:
    if rule.endpoint != "*" and rule.endpoint != identity["endpoint"]:
        return False
    if rule.identity == "ip" and identity["ip"]:
        return True
    if rule.identity == "api_key" and identity["api_key"]:
        return True
    if rule.identity == "user_id" and identity["user_id"]:
        return True
    return False
