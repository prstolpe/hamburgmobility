"""Load and validate config/rules.yaml, config/cycling_rules.yaml and config/design_rules.yaml."""

import re
from pathlib import Path

import yaml

from config.schema.cycling_model import CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from config.schema.provenance import collect_ids
from config.schema.rules_model import RULE_REF, RuleSet, Threshold

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
DEFAULT_RULES_PATH = CONFIG_DIR / "rules.yaml"
DEFAULT_CYCLING_RULES_PATH = CONFIG_DIR / "cycling_rules.yaml"
DEFAULT_DESIGN_RULES_PATH = CONFIG_DIR / "design_rules.yaml"

# Words in rule conditions that are operators or control words, not segment features.
_KEYWORDS = {"and", "or", "not", "in", "if", "else", "default", "no", "passed"}
_IDENTIFIER = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")


def load_rules(path: str | Path = DEFAULT_RULES_PATH) -> RuleSet:
    """Read rules.yaml and validate it; raises pydantic.ValidationError if invalid."""
    with open(path, encoding="utf-8") as f:
        return RuleSet.model_validate(yaml.safe_load(f))


def load_cycling_rules(path: str | Path = DEFAULT_CYCLING_RULES_PATH) -> CyclingRuleSet:
    """Read cycling_rules.yaml and validate it; raises pydantic.ValidationError if invalid."""
    with open(path, encoding="utf-8") as f:
        return CyclingRuleSet.model_validate(yaml.safe_load(f))


def load_design_rules(path: str | Path = DEFAULT_DESIGN_RULES_PATH) -> DesignRuleSet:
    """Read design_rules.yaml and validate it; raises pydantic.ValidationError if invalid."""
    with open(path, encoding="utf-8") as f:
        return DesignRuleSet.model_validate(yaml.safe_load(f))


def all_rule_ids(rules: RuleSet, cycling: CyclingRuleSet, design: DesignRuleSet) -> list[str]:
    """Rule ids of all three rule files (they share one id space for rule_trace)."""
    return (collect_ids(rules.model_dump(exclude={"meta", "sources"}, by_alias=True))
            + cycling.rule_ids() + design.rule_ids())


def network_highways(rules: RuleSet) -> list[str]:
    """highway classes in the network: highway_classes plus the extra ways of network rules (S-NET-04)."""
    out = list(rules.network.highway_classes.values)
    for r in rules.network.rules:
        out += [h for h in r.include_highway if h not in out]
    return out


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
