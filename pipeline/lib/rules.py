"""Load and validate config/rules.yaml."""

import re
from pathlib import Path

import yaml

from config.schema.rules_model import RULE_REF, RuleSet, Threshold

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[2] / "config" / "rules.yaml"

# Words in rule conditions that are operators or control words, not segment features.
_KEYWORDS = {"and", "or", "not", "in", "if", "else", "default", "no", "passed"}
_IDENTIFIER = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")


def load_rules(path: str | Path = DEFAULT_RULES_PATH) -> RuleSet:
    """Read rules.yaml and validate it; raises pydantic.ValidationError if invalid."""
    with open(path, encoding="utf-8") as f:
        return RuleSet.model_validate(yaml.safe_load(f))


def all_thresholds(rules: RuleSet) -> dict[str, Threshold]:
    """All thresholds of the cascade by name (names are unique across rules)."""
    return {name: t for rule in rules.classification for name, t in rule.thresholds.items()}


def referenced_features(rules: RuleSet) -> set[str]:
    """Segment feature names used in the cascade conditions.

    Excludes operators, literals ([...] lists, right-hand side of ==), threshold/width
    references, rule references and category names.
    """
    features: set[str] = set()
    for rule in rules.classification:
        # Text in parentheses in `then` is a comment, e.g. "GOW (weiter mit C-G30-*)".
        for expr in (rule.if_, re.sub(r"\([^)]*\)", " ", rule.then)):
            expr = RULE_REF.sub(" ", expr)
            expr = re.sub(r"\[[^\]]*\]", " ", expr)
            expr = re.sub(r"==\s*\w+", " ", expr)
            for token in _IDENTIFIER.findall(expr):
                if "." in token or token in _KEYWORDS or token in rules.categories or token.isupper():
                    continue
                features.add(token)
    return features
