from backend.models.rule import Rule


class RuleValidator:
    VALID_ALGORITHMS = {
        "fixed_window",
        "sliding_window_log",
        "sliding_window_counter",
        "token_bucket",
        "leaky_bucket",
    }

    VALID_IDENTITY_TYPES = {"ip", "api_key", "user_id"}

    def validate(self, rule: Rule) -> bool:
        if rule.algorithm not in self.VALID_ALGORITHMS:
            return False
        if rule.identity not in self.VALID_IDENTITY_TYPES:
            return False
        if rule.limit <= 0:
            return False
        if rule.window <= 0:
            return False
        return True

    def matches(self, rule: Rule, identity: dict) -> bool:
        if rule.endpoint != "*" and rule.endpoint != identity.get("endpoint"):
            return False
        if rule.identity == "ip" and identity.get("ip"):
            return True
        if rule.identity == "api_key" and identity.get("api_key"):
            return True
        if rule.identity == "user_id" and identity.get("user_id"):
            return True
        return False
