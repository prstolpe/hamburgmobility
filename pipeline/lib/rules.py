"""Load and validate config/rules.yaml, config/cycling_rules.yaml and config/design_rules.yaml."""

import re
from pathlib import Path

import yaml

from config.schema.cycling_model import CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from config.schema.provenance import collect_ids
from config.schema.rules_model import INACTIVE, RULE_REF, RuleSet, Threshold

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


def active_rule_ids(rules: RuleSet, cycling: CyclingRuleSet, design: DesignRuleSet) -> list[str]:
    """Rule ids without inactive rules (status inactive, also below an inactive block). Counts of covered rules use
    this list: an inactive rule never fires and does not count as covered (review 2026-11, recommendation 5)."""
    dumps = (rules.model_dump(exclude={"meta", "sources"}, by_alias=True),
             cycling.model_dump(exclude={"meta", "sources"}, by_alias=True),
             design.model_dump(exclude={"meta", "sources"}, by_alias=True))
    return [i for d in dumps for i in collect_ids(d, active_only=True)]


def with_rules_activated(rules: RuleSet, rule_ids: set[str] | list[str]) -> RuleSet:
    """Copy of rules.yaml with the given inactive classification rules set to draft – for tests of a rule's logic
    before it is activated (golden cases with `activate`)."""
    ids = set(rule_ids)
    unknown = ids - {r.id for r in rules.classification}
    if unknown:
        raise KeyError(f"unknown classification rules: {sorted(unknown)}")
    cls = [r.model_copy(update={"status": "draft"}) if r.id in ids and r.status == INACTIVE else r
           for r in rules.classification]
    return rules.model_copy(update={"classification": cls})


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


def cycling_with_blocks_activated(cycling: CyclingRuleSet, paths: set[str] | list[str]) -> CyclingRuleSet:
    """Copy of cycling_rules.yaml with the given inactive blocks (dotted path, e.g. separation_matrix.rural)
    switched on – for tests of their logic before activation (golden cases with `activate`)."""
    out = cycling.model_copy(deep=True)
    for path in paths:
        section, *rest = path.split(".")
        node = getattr(out, section)
        for key in rest:
            node = node[key]
        if node.get("status") != INACTIVE:
            raise ValueError(f"{path} is not inactive")
        node.pop("status")
    return out


def requirement_ref_mismatches(rules: RuleSet, cycling: CyclingRuleSet) -> list[str]:
    """F32: requirements entries with ref: point to cycling_rules.yaml widths_m; returns every field whose value
    differs from the referenced one (or whose path does not exist). widths_m is the source of truth."""
    widths = cycling.widths_m
    out = []
    for cat, reqs in rules.requirements.items():
        for key, entry in reqs.items():
            if not isinstance(entry, dict):
                continue
            for field, ref in (entry.get("ref") or {}).items():
                node = widths
                try:
                    for step in ref.removeprefix("cycling_rules.widths_m.").split("."):
                        node = node[step]
                except (KeyError, TypeError):
                    out.append(f"requirements.{cat}.{key}.{field}: {ref} not found")
                    continue
                if node != entry.get(field):
                    out.append(f"requirements.{cat}.{key}.{field} = {entry.get(field)}, {ref} = {node}")
    return out
