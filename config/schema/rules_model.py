"""pydantic model for config/rules.yaml.

Validates structure, provenance (source / source_type), units, categories, unique IDs and
cross-references. Rule conditions stay strings here; the classifier (prompt 08) evaluates them.
"""

import re
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SourceType = Literal["swov_crow", "de_regelwerk", "hamburg", "assumption"]
Status = Literal["draft", "reviewed", "approved"]

# The seven categories from CLAUDE.md (Ziel).
EXPECTED_CATEGORIES = {"SW", "GOW50", "GOW30", "ETW30", "ETW_ERF", "GOW80", "ETW60"}
# Intermediate group used inside the cascade ("GOW (weiter mit C-G30-*)").
CATEGORY_GROUPS = {"GOW": {"GOW50", "GOW30"}}

# Unit from the key name, e.g. cycle_track_width_m.
UNIT_SUFFIXES = {"_m": "m", "_ha": "ha", "_kmh": "km/h"}
# Numeric keys whose unit is not encoded in the name.
# TODO(open_questions): max_dtv has no unit in rules.yaml; Kfz/24h is the usual DTV unit.
KEY_UNITS = {
    "max_dtv": "Kfz/24h",
    "median_if_lanes_per_dir_gte": "Fahrstreifen je Richtung (Anzahl)",
}
# Keys holding the number of an entry whose unit comes from the entry itself.
VALUE_KEYS = {"value", "min", "max", "ideal", "range"}
# Non-numeric metadata keys inside entries.
META_KEYS = {"source", "source_type", "status", "note", "exception", "formula", "check", "unit"}

THRESHOLD_REF = re.compile(r"\bthresholds\.([A-Za-z0-9_]+)")
WIDTH_REF = re.compile(r"\brequired_width\.([A-Za-z0-9_]+)")
RULE_REF = re.compile(r"\b(C-[A-Z0-9]+-)(?:\d{2}|\*)")
UPPER_TOKEN = re.compile(r"\b[A-Z][A-Z0-9_]+\b")


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _unit_from_key(key: str) -> str | None:
    for suffix, unit in UNIT_SUFFIXES.items():
        if key.endswith(suffix):
            return unit
    return KEY_UNITS.get(key)


def _as_list(source: str | list[str] | None) -> list[str]:
    if source is None:
        return []
    return [source] if isinstance(source, str) else list(source)


def _check_provenance(entry: dict, path: str, source_ids: set[str]) -> None:
    """source_type is required; source is required unless source_type is 'assumption'."""
    source_type = entry.get("source_type")
    if source_type not in SourceType.__args__:
        raise ValueError(f"{path}: source_type missing or invalid ({source_type!r})")
    sources = _as_list(entry.get("source"))
    if not sources and source_type != "assumption":
        raise ValueError(f"{path}: source missing (required unless source_type is assumption)")
    unknown = [s for s in sources if s not in source_ids]
    if unknown:
        raise ValueError(f"{path}: unknown source reference(s) {unknown}")


def _check_units(entry: dict, path: str, entry_unit: str | None) -> None:
    """Every number must have a unit: explicit `unit`, key suffix, KEY_UNITS or section unit."""
    for key, val in entry.items():
        if key in META_KEYS:
            continue
        numeric = _is_number(val) or (isinstance(val, list) and val and all(_is_number(v) for v in val))
        if not numeric:
            continue
        unit = (entry.get("unit") or entry_unit) if key in VALUE_KEYS else _unit_from_key(key)
        if not unit:
            raise ValueError(f"{path}.{key}: number without unit")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Meta(_Strict):
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    date: date
    crs_work: Literal["EPSG:25832"]
    owner: str
    note: str | None = None


class Source(_Strict):
    title: str
    date: str
    url: str | None

    @field_validator("date", mode="before")
    @classmethod
    def _date_to_str(cls, v: Any) -> str:
        return str(v)


class Category(_Strict):
    label_de: str
    speed_kmh: int | None
    class_report2: str | None = None
    nl: str | None = None
    rural: bool = False
    note: str | None = None


class Threshold(_Strict):
    value: float
    unit: str
    source_type: SourceType
    source: str | list[str] | None = None
    check: str | None = None

    @field_validator("unit")
    @classmethod
    def _unit_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("unit must not be empty")
        return v


class ClassificationRule(_Strict):
    id: str = Field(pattern=r"^C-[A-Z0-9]+-\d{2}$")
    if_: str = Field(alias="if")
    then: str
    source: str | list[str] | None = None
    source_type: SourceType
    status: Status
    description: str | None = None
    applies_to: str | None = None
    thresholds: dict[str, Threshold] = {}
    note: str | None = None


class CoherenceRule(BaseModel):
    # Extra keys are rule parameters (e.g. min_run_m); their units are checked in RuleSet.
    model_config = ConfigDict(extra="allow")

    id: str = Field(pattern=r"^N\d+$")
    rule: str
    source: str | list[str] | None = None
    source_type: SourceType
    # TODO(open_questions): N1–N6 have no status in rules.yaml yet.
    status: Status | None = None


class ScoreDef(_Strict):
    weights: dict[str, float]
    missing_value_policy: str | None = None

    @field_validator("weights")
    @classmethod
    def _weights_sum_to_one(cls, v: dict[str, float]) -> dict[str, float]:
        if abs(sum(v.values()) - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1 (sum = {sum(v.values())})")
        return v


class WidthEntry(_Strict):
    source_type: SourceType
    value: float | None = None
    range: tuple[float, float] | None = None
    source: str | list[str] | None = None
    # TODO(open_questions): status here is free text ("am Original prüfen"), not draft/reviewed/approved.
    status: str | None = None
    formula: str | None = None

    @model_validator(mode="after")
    def _value_xor_range(self) -> "WidthEntry":
        if (self.value is None) == (self.range is None):
            raise ValueError("exactly one of value or range is required")
        if self.range is not None and self.range[0] >= self.range[1]:
            raise ValueError("range must be ascending")
        return self


class HighwayClasses(_Strict):
    values: list[str] = Field(min_length=1)
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    note: str | None = None

    @field_validator("values")
    @classmethod
    def _unique(cls, v: list[str]) -> list[str]:
        if len(set(v)) != len(v):
            raise ValueError("highway_classes.values must be unique")
        return v


class NetworkRule(_Strict):
    id: str = Field(pattern=r"^S-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    attribute: str | None = None  # OSM tag whose change ends a segment
    thresholds: dict[str, Threshold] = {}
    note: str | None = None


class Network(_Strict):
    highway_classes: HighwayClasses
    rules: list[NetworkRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> NetworkRule:
        return next(r for r in self.rules if r.id == rule_id)


class FeasibilityClass(_Strict):
    source_type: SourceType
    min: float | None = None
    max: float | None = None
    source: str | list[str] | None = None


class DiscrepancySpeed(_Strict):
    rule: str
    severity: dict[str, int]
    source: str | list[str]
    source_type: SourceType


class DiscrepancyDesign(_Strict):
    checks: list[str]
    severity: str
    source: str | list[str]
    source_type: SourceType


class DiscrepancyUse(_Strict):
    rule: str
    source: str | list[str]
    source_type: SourceType


class Discrepancy(_Strict):
    speed: DiscrepancySpeed
    design: DiscrepancyDesign
    use: DiscrepancyUse
    types: dict[str, str]


class Priority(_Strict):
    formula: str
    risk_weights: dict[str, float]


class RuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    categories: dict[str, Category]
    classification: list[ClassificationRule]
    scores: dict[str, ScoreDef]
    requirements: dict[str, dict[str, Any]]
    required_width: dict[str, WidthEntry]
    feasibility_classes: dict[str, FeasibilityClass]
    network: Network
    coherence: list[CoherenceRule]
    discrepancy: Discrepancy
    priority: Priority

    @model_validator(mode="after")
    def _cross_checks(self) -> "RuleSet":
        source_ids = set(self.sources)
        cats = set(self.categories)
        targets = cats | set(CATEGORY_GROUPS)

        if cats != EXPECTED_CATEGORIES:
            raise ValueError(f"categories must be {sorted(EXPECTED_CATEGORIES)}, got {sorted(cats)}")

        ids = ([r.id for r in self.classification] + [r.id for r in self.coherence]
               + [r.id for r in self.network.rules])
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate rule ids: {duplicates}")

        threshold_names = {n for r in self.classification for n in r.thresholds}
        rule_prefixes = {r.id.rsplit("-", 1)[0] + "-" for r in self.classification}

        for rule in self.classification:
            path = f"classification[{rule.id}]"
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            for name, threshold in rule.thresholds.items():
                _check_provenance(threshold.model_dump(include={"source", "source_type"}),
                                  f"{path}.thresholds.{name}", source_ids)
            for expr in (rule.if_, rule.then):
                for name in THRESHOLD_REF.findall(expr):
                    if name not in threshold_names:
                        raise ValueError(f"{path}: unknown threshold reference thresholds.{name}")
                for name in WIDTH_REF.findall(expr):
                    if name not in self.required_width:
                        raise ValueError(f"{path}: unknown width reference required_width.{name}")
                for prefix in RULE_REF.findall(expr):
                    if prefix not in rule_prefixes:
                        raise ValueError(f"{path}: reference to unknown rule group {prefix}*")
            then_tokens = set(UPPER_TOKEN.findall(RULE_REF.sub("", rule.then)))
            if not then_tokens or not then_tokens <= targets:
                raise ValueError(f"{path}: then must name categories from {sorted(targets)}, got {sorted(then_tokens)}")
            if rule.applies_to is not None and rule.applies_to not in targets:
                raise ValueError(f"{path}: unknown applies_to {rule.applies_to!r}")

        defaults = [r.id for r in self.classification if r.if_.strip() == "default"]
        if not defaults or self.classification[-1].if_.strip() != "default" or len(defaults) > 1:
            raise ValueError("cascade must end with exactly one rule with if: default")

        _check_provenance(self.network.highway_classes.model_dump(include={"source", "source_type"}),
                          "network.highway_classes", source_ids)
        for rule in self.network.rules:
            path = f"network.rules[{rule.id}]"
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            for name, threshold in rule.thresholds.items():
                _check_provenance(threshold.model_dump(include={"source", "source_type"}),
                                  f"{path}.thresholds.{name}", source_ids)

        for rule in self.coherence:
            path = f"coherence[{rule.id}]"
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            _check_units(rule.model_extra or {}, path, None)

        for cat, reqs in self.requirements.items():
            if cat not in cats:
                raise ValueError(f"requirements: unknown category {cat!r}")
            self._check_requirement_group(reqs, f"requirements.{cat}", source_ids)

        for key, entry in self.required_width.items():
            path = f"required_width.{key}"
            is_component = key.endswith("_m")
            is_category = any(key == c or key.startswith(c + "_") for c in cats)
            if not (is_component or is_category):
                raise ValueError(f"{path}: key must be a width component (*_m) or start with a category")
            _check_provenance(entry.model_dump(include={"source", "source_type"}), path, source_ids)

        for key, cls in self.feasibility_classes.items():
            _check_provenance(cls.model_dump(include={"source", "source_type"}),
                              f"feasibility_classes.{key}", source_ids)

        for name in ("speed", "design", "use"):
            part = getattr(self.discrepancy, name)
            _check_provenance(part.model_dump(include={"source", "source_type"}),
                              f"discrepancy.{name}", source_ids)
        requirement_keys = {k for reqs in self.requirements.values() for k in reqs}
        unknown_checks = set(self.discrepancy.design.checks) - requirement_keys
        if unknown_checks:
            raise ValueError(f"discrepancy.design.checks: not defined in requirements: {sorted(unknown_checks)}")

        return self

    @staticmethod
    def _check_requirement_group(group: dict, path: str, source_ids: set[str]) -> None:
        for key, entry in group.items():
            entry_path = f"{path}.{key}"
            if not isinstance(entry, dict):
                raise ValueError(f"{entry_path}: expected a mapping with value, source and source_type")
            if "source_type" in entry:
                _check_provenance(entry, entry_path, source_ids)
                _check_units(entry, entry_path, _unit_from_key(key))
            elif entry and all(isinstance(v, dict) for v in entry.values()):
                RuleSet._check_requirement_group(entry, entry_path, source_ids)  # e.g. profiles
            else:
                raise ValueError(f"{entry_path}: source_type missing")
