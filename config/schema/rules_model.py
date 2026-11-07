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


class MissingDefault(_Strict):
    value: bool | str
    note: str | None = None


class FallbackInput(_Strict):
    when: str | None = None  # condition on the segment; absent = always a fallback
    note: str | None = None


class PolicyRule(_Strict):
    """How the cascade is evaluated (C-MISS-*: missing values, C-CONF-*: confidence)."""
    id: str = Field(pattern=r"^C-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    thresholds: dict[str, Threshold] = {}
    defaults: dict[str, MissingDefault] = {}
    fallback_inputs: dict[str, FallbackInput] = {}
    note: str | None = None


class GateTransition(_Strict):
    from_: list[str] = Field(alias="from", min_length=1)
    to: list[str] = Field(min_length=1)


class NodeTypeEntry(_Strict):
    pair: list[str] = Field(min_length=2, max_length=2)
    type: str


class IstCheck(_Strict):
    ok: list[str]
    not_checkable: list[str]


class CoherenceRule(BaseModel):
    # Extra keys are rule parameters (e.g. min_run_m); their units are checked in RuleSet.
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str = Field(pattern=r"^N\d+$")
    rule: str
    source: str | list[str] | None = None
    source_type: SourceType
    status: Status
    note: str | None = None
    thresholds: dict[str, Threshold] = {}
    # N1
    gow_categories: list[str] = []
    end_ok_categories: list[str] = []
    # N4
    speed_fallback: str | None = None
    exclude_highway: list[str] = []
    etw_categories: list[str] = []
    restricted_categories: list[str] = []
    # N5
    gate_transitions: list[GateTransition] = []
    # N6
    category_rank: list[str] = []
    node_types: list[NodeTypeEntry] = []
    ist_check: dict[str, IstCheck] = {}

    def param(self, name: str) -> float:
        """Numeric parameter: flat key (e.g. min_run_m) or thresholds entry."""
        if name in self.thresholds:
            return self.thresholds[name].value
        extra = self.model_extra or {}
        if name not in extra:
            raise KeyError(f"coherence[{self.id}]: parameter {name!r} missing in rules.yaml")
        return extra[name]

    def categories_used(self) -> set[str]:
        cats = (set(self.gow_categories) | set(self.end_ok_categories) | set(self.etw_categories)
                | set(self.restricted_categories) | set(self.category_rank))
        for g in self.gate_transitions:
            cats |= set(g.from_) | set(g.to)
        for n in self.node_types:
            cats |= set(n.pair)
        return cats


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
    # extra ways besides highway_classes (S-NET-04)
    include_highway: list[str] = []
    require_name: bool = False
    service_values: list[str] = []           # allowed service=* values besides untagged
    motor_access_keys: list[str] = []        # most specific first; first known value decides
    motor_access_values: list[str] = []      # allowed values besides untagged
    motor_access_applies_to: list[str] = []  # highway classes the access check applies to
    note: str | None = None


class Network(_Strict):
    highway_classes: HighwayClasses
    rules: list[NetworkRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> NetworkRule:
        return next(r for r in self.rules if r.id == rule_id)


class ConflationRule(_Strict):
    id: str = Field(pattern=r"^S-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    thresholds: dict[str, Threshold] = {}
    note: str | None = None
    text_values: dict[str, float] = {}  # S-CONF-03: speed texts without a number -> calculation value


class Conflation(_Strict):
    rules: list[ConflationRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> ConflationRule:
        return next(r for r in self.rules if r.id == rule_id)


class FeatureRule(_Strict):
    id: str = Field(pattern=r"^S-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    method: str | None = None
    ties: Literal["min", "average"] | None = None  # percentile rank: rank of equal values
    thresholds: dict[str, Threshold] = {}
    exclude_highway: list[str] = []
    amenity_excluded: list[str] = []
    alkis_gebnutzbez: list[str] = []
    alkis_rellage_excluded: list[str] = []
    alkis_public_functions: list[str] = []
    alkis_ancillary_functions: list[str] = []
    route_types: list[int] = []
    path_highways: list[str] = []      # S-FEAT-11
    bicycle_allowed: list[str] = []    # S-FEAT-11
    official_status: list[str] = []    # S-FEAT-11
    note: str | None = None


class Features(_Strict):
    rules: list[FeatureRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> FeatureRule:
        return next(r for r in self.rules if r.id == rule_id)


class CrosssectionRule(_Strict):
    id: str = Field(pattern=r"^S-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    thresholds: dict[str, Threshold] = {}
    alkis_nutzart: list[str] = []
    targets: list[str] = []
    range_reference: Literal["min", "max"] | None = None
    note: str | None = None


class Crosssection(_Strict):
    rules: list[CrosssectionRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> CrosssectionRule:
        return next(r for r in self.rules if r.id == rule_id)


class FeasibilityClass(_Strict):
    source_type: SourceType
    min: float | None = None
    max: float | None = None
    source: str | list[str] | None = None


Direction = Literal["flow", "sparse"]


class SpeedLevel(_Strict):
    severity: int = Field(ge=1, le=3)
    min_excess_kmh: float
    source_type: SourceType
    source: str | list[str] | None = None
    check: str | None = None


class DiscrepancySpeed(_Strict):
    id: str = Field(pattern=r"^D-[A-Z]+-\d{2}$")
    rule: str
    levels: list[SpeedLevel] = Field(min_length=1)
    direction: Direction
    source: str | list[str]
    source_type: SourceType
    status: Status
    note: str | None = None


class DesignViolation(_Strict):
    check: str
    requirement: Any = None  # applies only if the category's requirement value equals this (None: any value)
    violated_if: str
    direction: Direction | dict[str, Direction]
    label_de: str
    source_type: SourceType
    source: str | list[str] | None = None
    note: str | None = None

    def direction_for(self, category: str) -> str:
        if isinstance(self.direction, str):
            return self.direction
        if category not in self.direction:
            raise KeyError(f"discrepancy.design: no direction for {self.check} in category {category}")
        return self.direction[category]


class DiscrepancyDesign(_Strict):
    id: str = Field(pattern=r"^D-[A-Z]+-\d{2}$")
    checks: list[str]
    severity: str
    max_severity: int = Field(ge=1, le=3)
    violations: list[DesignViolation] = Field(min_length=1)
    source: str | list[str]
    source_type: SourceType
    status: Status
    note: str | None = None


class UseLevel(_Strict):
    severity: int = Field(ge=1, le=3)
    factor: float = Field(gt=0)
    source_type: SourceType
    source: str | list[str] | None = None
    check: str | None = None


class DiscrepancyUse(_Strict):
    id: str = Field(pattern=r"^D-[A-Z]+-\d{2}$")
    rule: str
    profile_if_track: str
    profile_default: str
    profile_reported: str | None = None
    levels: list[UseLevel] = Field(min_length=1)
    direction: Direction
    source: str | list[str]
    source_type: SourceType
    status: Status
    note: str | None = None


class TypeRule(_Strict):
    id: str = Field(pattern=r"^D-[A-Z]+-\d{2}$")
    rule: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None


class Discrepancy(_Strict):
    speed: DiscrepancySpeed
    design: DiscrepancyDesign
    use: DiscrepancyUse
    types: dict[Literal["D1", "D2", "D3"], str]
    type_rule: TypeRule


class RiskRule(_Strict):
    id: str = Field(pattern=r"^P-[A-Z]+-\d{2}$")
    description: str
    components: dict[str, str]  # risk weight key -> column (0-1)
    severe_weight_key: str
    thresholds: dict[str, Threshold]
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    note: str | None = None


class ValidationRule(_Strict):
    id: str = Field(pattern=r"^V-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    thresholds: dict[str, Threshold] = {}
    runs: int | None = Field(default=None, gt=0)       # Monte-Carlo runs
    seed: int | None = None                            # random seed (reproducible runs)
    vary: list[Literal["weights", "thresholds"]] = []  # what the Monte-Carlo runs vary
    note: str | None = None


class Validation(_Strict):
    rules: list[ValidationRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> ValidationRule:
        return next(r for r in self.rules if r.id == rule_id)


class HarmonisationRule(_Strict):
    id: str = Field(pattern=r"^H-[A-Z]+-\d{2}$")
    description: str
    source_type: SourceType
    status: Status
    source: str | list[str] | None = None
    min_run_from: str                   # coherence rule whose min_run_m is used (N2)
    max_passes: int = Field(gt=0)       # technical limit of the repeated passes
    locked_categories: list[str] = []   # never changed
    thresholds: dict[str, Threshold] = {}
    note: str | None = None


class Harmonisation(_Strict):
    rules: list[HarmonisationRule] = Field(min_length=1)

    def rule(self, rule_id: str) -> HarmonisationRule:
        return next(r for r in self.rules if r.id == rule_id)


class Priority(_Strict):
    formula: str
    risk_weights: dict[str, float]
    risk: RiskRule


class RuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    categories: dict[str, Category]
    classification: list[ClassificationRule]
    classification_policy: list[PolicyRule]
    scores: dict[str, ScoreDef]
    requirements: dict[str, dict[str, Any]]
    required_width: dict[str, WidthEntry]
    feasibility_classes: dict[str, FeasibilityClass]
    network: Network
    conflation: Conflation
    features: Features
    crosssection: Crosssection
    coherence: list[CoherenceRule]
    discrepancy: Discrepancy
    priority: Priority
    harmonisation: Harmonisation
    validation: Validation

    def coherence_rule(self, rule_id: str) -> CoherenceRule:
        for rule in self.coherence:
            if rule.id == rule_id:
                return rule
        raise KeyError(f"coherence rule {rule_id} not in rules.yaml")

    @model_validator(mode="after")
    def _cross_checks(self) -> "RuleSet":
        source_ids = set(self.sources)
        cats = set(self.categories)
        targets = cats | set(CATEGORY_GROUPS)

        if cats != EXPECTED_CATEGORIES:
            raise ValueError(f"categories must be {sorted(EXPECTED_CATEGORIES)}, got {sorted(cats)}")

        ids = ([r.id for r in self.classification] + [r.id for r in self.classification_policy]
               + [r.id for r in self.coherence]
               + [r.id for r in self.network.rules] + [r.id for r in self.conflation.rules]
               + [r.id for r in self.features.rules] + [r.id for r in self.crosssection.rules]
               + [self.discrepancy.speed.id, self.discrepancy.design.id, self.discrepancy.use.id,
                  self.discrepancy.type_rule.id, self.priority.risk.id]
               + [r.id for r in self.harmonisation.rules]
               + [r.id for r in self.validation.rules])
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

        if not any(r.thresholds.get("near_threshold") for r in self.classification_policy):
            raise ValueError("classification_policy: threshold near_threshold missing (confidence)")

        _check_provenance(self.network.highway_classes.model_dump(include={"source", "source_type"}),
                          "network.highway_classes", source_ids)
        stage_rules = ([(f"classification_policy[{r.id}]", r) for r in self.classification_policy]
                       + [(f"network.rules[{r.id}]", r) for r in self.network.rules]
                       + [(f"conflation.rules[{r.id}]", r) for r in self.conflation.rules]
                       + [(f"features.rules[{r.id}]", r) for r in self.features.rules]
                       + [(f"crosssection.rules[{r.id}]", r) for r in self.crosssection.rules]
                       + [(f"harmonisation.rules[{r.id}]", r) for r in self.harmonisation.rules]
                       + [(f"validation.rules[{r.id}]", r) for r in self.validation.rules])
        for path, rule in stage_rules:
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            for name, threshold in rule.thresholds.items():
                _check_provenance(threshold.model_dump(include={"source", "source_type"}),
                                  f"{path}.thresholds.{name}", source_ids)

        for rule in self.coherence:
            path = f"coherence[{rule.id}]"
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            _check_units(rule.model_extra or {}, path, None)
            for name, threshold in rule.thresholds.items():
                _check_provenance(threshold.model_dump(include={"source", "source_type"}),
                                  f"{path}.thresholds.{name}", source_ids)
            unknown = sorted(rule.categories_used() - set(cats))
            if unknown:
                raise ValueError(f"{path}: unknown categories {unknown}")
            if rule.category_rank and (set(rule.category_rank) != set(cats) or len(rule.category_rank) != len(cats)):
                raise ValueError(f"{path}.category_rank must list every category exactly once")
            missing_checks = sorted({n.type for n in rule.node_types} - set(rule.ist_check))
            if missing_checks:
                raise ValueError(f"{path}.ist_check: missing node types {missing_checks}")

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

        for r in self.harmonisation.rules:
            if r.min_run_from not in {c.id for c in self.coherence}:
                raise ValueError(f"harmonisation.rules[{r.id}].min_run_from: unknown coherence rule {r.min_run_from}")
            unknown = sorted(set(r.locked_categories) - cats)
            if unknown:
                raise ValueError(f"harmonisation.rules[{r.id}].locked_categories: unknown {unknown}")
        self._check_discrepancy(source_ids, cats)
        for rule in self.crosssection.rules:
            unknown_targets = [t for t in rule.targets if t not in self.required_width]
            if unknown_targets:
                raise ValueError(f"crosssection.rules[{rule.id}].targets: not in required_width: {unknown_targets}")
        requirement_keys = {k for reqs in self.requirements.values() for k in reqs}
        unknown_checks = set(self.discrepancy.design.checks) - requirement_keys
        if unknown_checks:
            raise ValueError(f"discrepancy.design.checks: not defined in requirements: {sorted(unknown_checks)}")

        return self

    def _check_discrepancy(self, source_ids: set[str], cats: set[str]) -> None:
        d = self.discrepancy
        for name in ("speed", "design", "use", "type_rule"):
            _check_provenance(getattr(d, name).model_dump(include={"source", "source_type"}),
                              f"discrepancy.{name}", source_ids)
        for name, levels in (("speed", d.speed.levels), ("use", d.use.levels)):
            for i, level in enumerate(levels):
                _check_provenance(level.model_dump(include={"source", "source_type"}),
                                  f"discrepancy.{name}.levels[{i}]", source_ids)
            if [lv.severity for lv in levels] != sorted({lv.severity for lv in levels}):
                raise ValueError(f"discrepancy.{name}.levels: severities must be unique and ascending")
        if [lv.min_excess_kmh for lv in d.speed.levels] != sorted(lv.min_excess_kmh for lv in d.speed.levels):
            raise ValueError("discrepancy.speed.levels: min_excess_kmh must ascend with severity")
        if [lv.factor for lv in d.use.levels] != sorted(lv.factor for lv in d.use.levels):
            raise ValueError("discrepancy.use.levels: factor must ascend with severity")
        for i, v in enumerate(d.design.violations):
            path = f"discrepancy.design.violations[{i}]"
            _check_provenance(v.model_dump(include={"source", "source_type"}), path, source_ids)
            if v.check not in d.design.checks:
                raise ValueError(f"{path}: check {v.check!r} not in discrepancy.design.checks")
            if isinstance(v.direction, dict):
                unknown = sorted(set(v.direction) - cats)
                if unknown:
                    raise ValueError(f"{path}.direction: unknown categories {unknown}")
        for path, rule in ((f"priority.risk[{self.priority.risk.id}]", self.priority.risk),):
            _check_provenance(rule.model_dump(include={"source", "source_type"}), path, source_ids)
            for name, threshold in rule.thresholds.items():
                _check_provenance(threshold.model_dump(include={"source", "source_type"}),
                                  f"{path}.thresholds.{name}", source_ids)
        risk = self.priority.risk
        weights = set(self.priority.risk_weights)
        if risk.severe_weight_key not in weights:
            raise ValueError(f"priority.risk.severe_weight_key {risk.severe_weight_key!r} not in risk_weights")
        if set(risk.components) != weights - {risk.severe_weight_key}:
            raise ValueError("priority.risk.components must name every risk weight except severe_weight_key: "
                             f"{sorted(weights - {risk.severe_weight_key})}")

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
