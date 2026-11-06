"""pydantic model for config/design_rules.yaml (lanes, placement, cross-section allocation, profile, junctions).

Conditions stay strings; prompts 19 and 20 evaluate them. The cross-checks validate provenance,
ids, categories, junction types, the names used in junction conditions and the profile rules (prompt 19).
"""

import re
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config.schema.cycling_model import CYCLE_CATEGORIES, FACILITIES, Meta, Source
from config.schema.provenance import META_KEYS, check_provenance, collect_ids
from config.schema.rules_model import EXPECTED_CATEGORIES

# Words in junction conditions that are operators.
_KEYWORDS = {"and", "or", "not"}
# Names in conditions are snake_case; plain words without an underscore (e.g. "space ok") are
# informal text and are not checked.
_NAME = re.compile(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b")
# Leg descriptors that are not road or cycle categories.
LEG_WORDS = {"any", "with", "tram", "cycle_path", "cycle_street"}
_LEG_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Row keys naming a junction type.
TYPE_KEYS = ("then", "else_then", "otherwise", "fallback")
# Rules of profile_assignment read by pipeline/lib/profile.py (prompt 19).
PROFILE_RULE_IDS = {"PRF-01", "PRF-02", "PRF-03", "PRF-04", "PRF-05", "PRF-06", "PRF-07"}
# Cascade step that switches to the fallback facility of the matrix cell (not a degrade step).
FALLBACK_STEP = "fallback"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class _Open(BaseModel):
    """Entries with free-form extra keys (thresholds, notes); values are checked by provenance."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Lanes(_Strict):
    principle: str
    default_per_direction: dict[str, Any]
    rules: list[dict[str, Any]]
    lane_width_m: dict[str, Any]


class JunctionRow(_Open):
    id: str
    legs: str
    if_: str | None = Field(default=None, alias="if")
    else_if: str | None = None
    same_as: str | None = None


class DecisionTable(_Strict):
    source: str | list[str]
    source_type: str
    rows: list[JunctionRow]


class Junctions(_Strict):
    inputs: list[str]
    types: list[str]
    decision_table: DecisionTable
    thresholds: dict[str, dict[str, Any]]
    cyclist_treatment: list[dict[str, Any]]
    output_fields: list[str]


def _check_lane_defaults(defaults: dict) -> None:
    cats = set(defaults) - META_KEYS
    if cats != EXPECTED_CATEGORIES:
        raise ValueError(f"lanes.default_per_direction: categories must be {sorted(EXPECTED_CATEGORIES)}, "
                         f"got {sorted(cats)}")
    for cat in cats:
        v = defaults[cat]
        if not (v is None or v == "shared" or (isinstance(v, int) and v >= 1)):
            raise ValueError(f"lanes.default_per_direction.{cat}: must be a count, 'shared' or null, got {v!r}")


def _check_junctions(j: Junctions) -> None:
    types = set(j.types)
    names = set(j.inputs) | set(j.thresholds)
    row_ids = {r.id for r in j.decision_table.rows}
    leg_words = EXPECTED_CATEGORIES | CYCLE_CATEGORIES | LEG_WORDS
    for row in j.decision_table.rows:
        extra = row.model_extra or {}
        for key in TYPE_KEYS:
            if key in extra and extra[key] not in types:
                raise ValueError(f"{row.id}.{key}: unknown junction type {extra[key]!r}")
        if row.same_as is not None and row.same_as not in row_ids:
            raise ValueError(f"{row.id}.same_as: unknown row {row.same_as!r}")
        for cond in (row.if_, row.else_if):
            for name in _NAME.findall(cond or ""):
                if name not in names and name not in _KEYWORDS:
                    raise ValueError(f"{row.id}: unknown name {name!r} in condition (not an input or threshold)")
        unknown_legs = set(_LEG_TOKEN.findall(row.legs)) - leg_words
        if unknown_legs:
            raise ValueError(f"{row.id}.legs: unknown categories {sorted(unknown_legs)}")


def _check_profile(profile: dict, allocation: dict) -> None:
    rules = {r.get("id"): r for r in profile.get("rules", [])}
    missing = PROFILE_RULE_IDS - set(rules)
    if missing:
        raise ValueError(f"profile_assignment: rules missing {sorted(missing)}")
    steps = [s["step"] for s in allocation["degrade_cascade_if_not_fit"]]
    order = rules["PRF-06"]["cascade_order"]
    unknown = [s for s in order if s not in steps and s != FALLBACK_STEP]
    if unknown:
        raise ValueError(f"PRF-06.cascade_order: unknown steps {unknown}")
    if [s for s in order if s != FALLBACK_STEP] != steps:
        raise ValueError(f"PRF-06.cascade_order: must contain the degrade steps {steps} in order")
    if not set(rules["PRF-06"]["flag_only_steps"]) <= set(order):
        raise ValueError("PRF-06.flag_only_steps: not in cascade_order")
    prf03 = rules["PRF-03"]
    elements = set(allocation["elements_min_m"]) | set(prf03.get("extra_elements", []))
    cells = prf03["cycle_elements"]
    if set(cells) != FACILITIES:
        raise ValueError(f"PRF-03.cycle_elements: facilities must be {sorted(FACILITIES)}, got {sorted(cells)}")
    for fac, cell in cells.items():
        for key in ("element", "buffer"):
            if cell.get(key) is not None and cell[key] not in elements:
                raise ValueError(f"PRF-03.cycle_elements.{fac}.{key}: unknown element {cell[key]!r}")
    for rule_id, key in (("PRF-03", "no_sidewalk_categories"), ("PRF-03", "tree_categories"),
                         ("PRF-04", "no_profile_categories")):
        unknown = set(rules[rule_id][key]) - EXPECTED_CATEGORIES
        if unknown:
            raise ValueError(f"{rule_id}.{key}: unknown categories {sorted(unknown)}")


class DesignRuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    lanes: Lanes
    placement: dict[str, Any]
    cross_section_allocation: dict[str, Any]
    profile_assignment: dict[str, Any]
    junctions: Junctions

    def rule_ids(self) -> list[str]:
        return collect_ids(self.model_dump(exclude={"meta", "sources"}, by_alias=True))

    @model_validator(mode="after")
    def _cross_checks(self) -> "DesignRuleSet":
        body = self.model_dump(exclude={"meta", "sources"}, by_alias=True)
        check_provenance(body, "design_rules", set(self.sources))

        ids = self.rule_ids()
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate rule ids: {duplicates}")

        steps = [s["step"] for s in self.cross_section_allocation["degrade_cascade_if_not_fit"]]
        if len(steps) != len(set(steps)):
            raise ValueError(f"degrade_cascade_if_not_fit: duplicate steps {steps}")

        _check_lane_defaults(self.lanes.default_per_direction)
        _check_profile(self.profile_assignment, self.cross_section_allocation)
        _check_junctions(self.junctions)
        return self
