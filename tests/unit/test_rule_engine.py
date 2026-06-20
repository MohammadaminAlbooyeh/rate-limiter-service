import pytest
from backend.rules.rule_validator import RuleValidator
from backend.models.rule import Rule


def test_valid_rule_passes():
    validator = RuleValidator()
    rule = Rule(
        name="test",
        identity="ip",
        algorithm="fixed_window",
        limit=100,
        window=60,
    )
    assert validator.validate(rule) is True


def test_invalid_algorithm_fails():
    validator = RuleValidator()
    rule = Rule(
        name="test",
        identity="ip",
        algorithm="invalid",
        limit=100,
        window=60,
    )
    assert validator.validate(rule) is False
