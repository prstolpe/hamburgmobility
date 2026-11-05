"""pydantic model for config/design_rules.yaml (lanes, placement, cross-section allocation, junctions).

Conditions stay strings; prompts 19 and 20 evaluate them. The cross-checks validate provenance,
ids, categories, junction types and the names used in junction conditions.
"""

import re
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config.schema.cycling_model import CYCLE_CATEGORIES, Meta, Source
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


class DesignRuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    lanes: Lanes
    placement: dict[str, Any]
    cross_section_allocation: dict[str, Any]
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
        _check_junctions(self.junctions)
        return self
