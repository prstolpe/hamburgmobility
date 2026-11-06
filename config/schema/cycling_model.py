"""pydantic model for config/cycling_rules.yaml (cycle network, five principles, separation matrix, widths).

Deep sections stay plain dicts; the cross-checks below validate provenance, ids, categories and
facility names. Rule texts stay strings; later prompts (16–18) evaluate them. Prompt 15 adds cycle_graph,
demand_model and routing_impedance.ist_mapping, whose condition names are fixed here; prompt 16 adds
network_design (C-NET-01..13); prompt 17 adds principle_scoring (C-PRI-01..16); prompt 18 adds
facility_assignment (C-FAC-01..07).
"""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config.schema.provenance import META_KEYS, check_provenance, collect_ids
from config.schema.rules_model import EXPECTED_CATEGORIES

CYCLE_CATEGORIES = {"RSV", "HAUPT", "BASIS", "ERSCHL"}
# Matrix column for streets that are not part of the cycle network.
NO_CYCLE_CATEGORY = "none"
# Cycle facility vocabulary; must match the list in separation_matrix.note (tested).
FACILITIES = {"separated_oneway_both", "separated_twoway", "cycle_lane", "cycle_street", "mixed", "own_path"}
PRINCIPLES = {"cohesion", "directness", "safety", "comfort", "attractiveness"}
RURAL_CATEGORIES = {"GOW80", "ETW60"}
# Keys of a matrix cell given as a dict; the others are metadata or conditions.
CELL_FACILITY_KEYS = {"preferred", "fallback", "all"}
# Condition names of routing_impedance.ist_mapping; evaluated in pipeline/lib/cycle_graph.py.
IMPEDANCE_CONDITIONS = {"cycle_street", "own_path", "separated_track", "low_speed_access_road", "low_speed_with_lane",
                        "low_speed_mixed", "other", "unpaved_or_cobbles"}
# Factor keys that are delays (seconds), not length factors.
DELAY_KEYS = {"signal_delay_s", "give_way_delay_s"}
ASSIGNMENT_METHODS = {"stochastic", "aon"}
DESTINATION_TYPES = {"jobs_floor_area", "shops", "schools", "universities", "rapid_transit_stops"}
GRAPH_RULE_IDS = {f"C-GRAPH-0{i}" for i in range(1, 7)}
DEMAND_RULE_IDS = {f"C-DEM-0{i}" for i in range(1, 8)}
NETWORK_RULE_IDS = {f"C-NET-{i:02d}" for i in range(1, 14)}
# Keys of C-NET-03 soll_factors besides the road categories: own paths (kind = path).
SOLL_FACTOR_EXTRA_KEYS = {"path"}
PRINCIPLE_RULE_IDS = {f"C-PRI-{i:02d}" for i in range(1, 17)}
# Score forms of C-PRI-01; evaluated in pipeline/lib/principles.py.
SCORE_FORMS = {"share", "ratio", "inverse_ratio", "excess", "percentile_inverse"}
FACILITY_RULE_IDS = {f"C-FAC-0{i}" for i in range(1, 8)}
# Ist classes of C-FAC-05 (prompts/18); evaluated in pipeline/lib/facility.py.
IST_CLASSES = {"cycle_street", "track", "lane", "shared_lane", "no"}
# Flags of pipeline/lib/facility.py that C-FAC-07 may name.
FACILITY_FLAGS = {"dtv_unknown", "fallback_check_p19", "cycle_street_blocked", "mixed_over_s04", "no_target_width",
                  "ist_width_unknown"}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Meta(_Strict):
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    date: date
    crs_work: Literal["EPSG:25832"]
    depends_on: str | list[str]


class Source(_Strict):
    title: str
    url: str | None
    note: str | None = None


def _cell_facilities(cell: Any, path: str) -> list[str]:
    if isinstance(cell, str):
        return [cell]
    if isinstance(cell, dict):
        return [cell[k] for k in CELL_FACILITY_KEYS if k in cell]
    raise ValueError(f"{path}: matrix cell must be a facility name or a dict")


def _check_matrix(matrix: dict) -> None:
    columns = CYCLE_CATEGORIES | {NO_CYCLE_CATEGORY}
    urban = EXPECTED_CATEGORIES - RURAL_CATEGORIES
    missing = (urban - set(matrix)) | (RURAL_CATEGORIES - set(matrix.get("rural", {})))
    if missing:
        raise ValueError(f"separation_matrix: road categories missing: {sorted(missing)}")
    for cat in urban:
        row = matrix[cat]
        if "all" in row:
            cells = {"all": row}
        else:
            cells = {k: v for k, v in row.items() if k not in META_KEYS}
            if set(cells) != columns:
                raise ValueError(f"separation_matrix.{cat}: cycle categories must be {sorted(columns)}, "
                                 f"got {sorted(cells)}")
        for col, cell in cells.items():
            for f in _cell_facilities(cell, f"separation_matrix.{cat}.{col}"):
                if f not in FACILITIES:
                    raise ValueError(f"separation_matrix.{cat}.{col}: unknown facility {f!r}")
    for cat in RURAL_CATEGORIES:
        for f in _cell_facilities(matrix["rural"][cat], f"separation_matrix.rural.{cat}"):
            if f not in FACILITIES:
                raise ValueError(f"separation_matrix.rural.{cat}: unknown facility {f!r}")


def _check_project_target(target: dict) -> None:
    columns = CYCLE_CATEGORIES | {NO_CYCLE_CATEGORY}
    for facility in ("separated_oneway", "separated_twoway", "cycle_lane"):
        cols = set(target[facility]) - META_KEYS
        if not cols <= columns:
            raise ValueError(f"widths_m.project_target.{facility}: unknown cycle categories {sorted(cols - columns)}")


def _check_ist_mapping(impedance: dict) -> None:
    factors = set(impedance["factors"]) - DELAY_KEYS
    for rule in impedance["ist_mapping"]["rules"]:
        if rule["when"] not in IMPEDANCE_CONDITIONS:
            raise ValueError(f"routing_impedance.ist_mapping {rule['id']}: unknown condition {rule['when']!r}")
        key = rule.get("factor", rule.get("multiply"))
        if key not in factors:
            raise ValueError(f"routing_impedance.ist_mapping {rule['id']}: unknown factor {key!r}")


def _rules_by_id(section: dict, expected: set[str], name: str) -> dict[str, dict]:
    rules = {r["id"]: r for r in section["rules"]}
    missing = sorted(expected - set(rules))
    if missing:
        raise ValueError(f"{name}: rules missing: {missing}")
    return rules


def _check_demand_model(section: dict) -> None:
    rules = _rules_by_id(section, DEMAND_RULE_IDS, "demand_model")
    weights = {k: v for k, v in rules["C-DEM-02"]["weights"].items() if k not in META_KEYS}
    if set(weights) != DESTINATION_TYPES:
        raise ValueError(f"demand_model C-DEM-02: destination types must be {sorted(DESTINATION_TYPES)}, got {sorted(weights)}")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"demand_model C-DEM-02: weights must sum to 1, got {sum(weights.values())}")
    lo, hi = rules["C-DEM-04"]["distance_band_km"]
    if not 0 <= lo < hi:
        raise ValueError(f"demand_model C-DEM-04: distance_band_km must be [min, max] with min < max, got {[lo, hi]}")
    if rules["C-DEM-05"]["method"] not in ASSIGNMENT_METHODS:
        raise ValueError(f"demand_model C-DEM-05: assignment method must be one of {sorted(ASSIGNMENT_METHODS)}")
    lo, hi = rules["C-DEM-07"]["high_ratio_band"]
    if not 0 < lo < hi:
        raise ValueError(f"demand_model C-DEM-07: high_ratio_band must be [min, max] with 0 < min < max")


def _check_network_design(section: dict, impedance: dict) -> None:
    rules = _rules_by_id(section, NETWORK_RULE_IDS, "network_design")
    factors = set(impedance["factors"]) - DELAY_KEYS
    soll = rules["C-NET-03"]["soll_factors"]
    unknown_keys = set(soll) - EXPECTED_CATEGORIES - SOLL_FACTOR_EXTRA_KEYS
    if unknown_keys:
        raise ValueError(f"network_design C-NET-03: unknown soll_factors keys {sorted(unknown_keys)}")
    bad = sorted(k for k, v in soll.items() if v not in factors)
    if bad:
        raise ValueError(f"network_design C-NET-03: soll_factors refer to unknown factors for {bad}")
    if not 0 <= rules["C-NET-04"]["max_reduction"] < 1:
        raise ValueError("network_design C-NET-04: max_reduction must be in [0, 1)")
    c05 = rules["C-NET-05"]
    if not 0 < c05["multiplier"] <= 1:
        raise ValueError("network_design C-NET-05: multiplier must be in (0, 1]")
    if set(c05["official_status"]) & set(c05["planned_status"]):
        raise ValueError("network_design C-NET-05: official_status and planned_status overlap")
    q = rules["C-NET-01"]["job_cluster_quantile"]
    if not 0 < q < 1:
        raise ValueError("network_design C-NET-01: job_cluster_quantile must be in (0, 1)")


def principle_check_ids(principles: dict) -> set[str]:
    return {c["id"] for p in principles.values() for c in p["checks"]}


def _check_principle_scoring(section: dict, principles: dict, impedance: dict, widths: dict) -> None:
    rules = _rules_by_id(section, PRINCIPLE_RULE_IDS, "principle_scoring")
    checks = principle_check_ids(principles)
    forms = rules["C-PRI-01"]["score_forms"]
    if set(forms) != checks:
        raise ValueError(f"principle_scoring C-PRI-01: score_forms must name every check, missing "
                         f"{sorted(checks - set(forms))}, unknown {sorted(set(forms) - checks)}")
    bad = sorted(k for k, v in forms.items() if v not in SCORE_FORMS)
    if bad:
        raise ValueError(f"principle_scoring C-PRI-01: unknown score form for {bad}")
    for name in ("network_only",):
        unknown = set(rules["C-PRI-01"][name]) - checks
        if unknown:
            raise ValueError(f"principle_scoring C-PRI-01 {name}: unknown checks {sorted(unknown)}")
    c02 = rules["C-PRI-02"]
    conditions = IMPEDANCE_CONDITIONS - {"unpaved_or_cobbles"}
    if set(c02["by_condition"]) != conditions:
        raise ValueError(f"principle_scoring C-PRI-02: by_condition must map {sorted(conditions)}")
    used = list(c02["by_condition"].values()) + [c02["lane_upgrade"], c02["sidepath_oneway"], c02["sidepath_twoway"]]
    if not set(used) <= FACILITIES:
        raise ValueError(f"principle_scoring C-PRI-02: unknown facilities {sorted(set(used) - FACILITIES)}")
    c03 = rules["C-PRI-03"]
    if set(c03["satisfies"]) != FACILITIES:
        raise ValueError("principle_scoring C-PRI-03: satisfies must name every facility")
    for key in ("satisfies", "partial"):
        for soll, ist in c03[key].items():
            if soll not in FACILITIES or not set(ist) <= FACILITIES:
                raise ValueError(f"principle_scoring C-PRI-03 {key}.{soll}: unknown facility")
            if key == "partial" and set(ist) & set(c03["satisfies"].get(soll, [])):
                raise ValueError(f"principle_scoring C-PRI-03 partial.{soll}: overlaps satisfies")
    if not 0 < c03["partial_score"] < 1:
        raise ValueError("principle_scoring C-PRI-03: partial_score must be in (0, 1)")
    req = rules["C-PRI-08"]["required_by_facility"]
    targets = set(widths["project_target"]) - META_KEYS
    if not set(req) <= FACILITIES or not set(req.values()) <= targets:
        raise ValueError("principle_scoring C-PRI-08: required_by_facility must map facilities to widths_m.project_target keys")
    if not 0 < rules["C-PRI-10"]["target_share"] <= 1:
        raise ValueError("principle_scoring C-PRI-10: target_share must be in (0, 1]")
    c13 = rules["C-PRI-13"]
    if not 0 < c13["medium"] < c13["high"] <= 1:
        raise ValueError("principle_scoring C-PRI-13: need 0 < medium < high <= 1")
    if not 0 < rules["C-PRI-14"]["delta"] < 1:
        raise ValueError("principle_scoring C-PRI-14: delta must be in (0, 1)")
    unknown = set(rules["C-PRI-16"]["unavailable"]) - checks
    if unknown:
        raise ValueError(f"principle_scoring C-PRI-16: unknown checks {sorted(unknown)}")


def width_ref(widths: dict, path: str):
    """Value at a dotted path relative to widths_m (C-FAC-04 floor, de_reference, nl_reference)."""
    node = widths
    for key in path.split("."):
        node = node[key]
    return node


def _check_facility_assignment(section: dict, widths: dict) -> None:
    rules = _rules_by_id(section, FACILITY_RULE_IDS, "facility_assignment")
    if set(rules["C-FAC-01"]["category_order"]) != CYCLE_CATEGORIES:
        raise ValueError(f"facility_assignment C-FAC-01: category_order must name {sorted(CYCLE_CATEGORIES)}")
    c04 = rules["C-FAC-04"]
    targets = set(widths["project_target"]) - META_KEYS
    if not set(c04["target_by_facility"]) <= FACILITIES or not set(c04["target_by_facility"].values()) <= targets:
        raise ValueError("facility_assignment C-FAC-04: target_by_facility must map facilities to widths_m.project_target keys")
    for key in ("floor", "de_reference", "nl_reference"):
        for fac, path in c04[key].items():
            if fac not in FACILITIES:
                raise ValueError(f"facility_assignment C-FAC-04 {key}: unknown facility {fac!r}")
            try:
                value = width_ref(widths, path)
            except (KeyError, TypeError):
                raise ValueError(f"facility_assignment C-FAC-04 {key}.{fac}: widths_m.{path} not found") from None
            if not isinstance(value, (int, float)):
                raise ValueError(f"facility_assignment C-FAC-04 {key}.{fac}: widths_m.{path} is not a number")
    c05 = rules["C-FAC-05"]
    if set(c05["ist_classes"]) != IST_CLASSES:
        raise ValueError(f"facility_assignment C-FAC-05: ist_classes must be {sorted(IST_CLASSES)}")
    if set(c05["to_facility"]) != IST_CLASSES or not set(c05["to_facility"].values()) | {c05["twoway_track_facility"]} <= FACILITIES:
        raise ValueError("facility_assignment C-FAC-05: to_facility must map every Ist class to a facility")
    c06 = rules["C-FAC-06"]
    if not set(c06["missing_classes"]) <= IST_CLASSES:
        raise ValueError("facility_assignment C-FAC-06: missing_classes must be Ist classes")
    if not set(c06["not_assessed_soll"]) <= FACILITIES:
        raise ValueError("facility_assignment C-FAC-06: not_assessed_soll must be facilities")
    unknown = set(rules["C-FAC-07"]["lowers_confidence"]) - FACILITY_FLAGS
    if unknown:
        raise ValueError(f"facility_assignment C-FAC-07: unknown flags {sorted(unknown)}")
    share = rules["C-FAC-03"]["motor_peak_hour_share"]["value"]
    if not 0 < share <= 1:
        raise ValueError("facility_assignment C-FAC-03: motor_peak_hour_share must be in (0, 1]")


class CyclingRuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    cycle_categories: dict[str, dict[str, Any]]
    principles: dict[str, dict[str, Any]]
    principle_weights: dict[str, Any]
    principle_scoring: dict[str, Any]
    routing_impedance: dict[str, Any]
    cycle_graph: dict[str, Any]
    demand_model: dict[str, Any]
    network_design: dict[str, Any]
    separation_matrix: dict[str, Any]
    facility_assignment: dict[str, Any]
    cycle_street: dict[str, Any]
    demand: dict[str, Any]
    widths_m: dict[str, Any]
    hamburg_reference: dict[str, Any]

    def rule_ids(self) -> list[str]:
        return collect_ids(self.model_dump(exclude={"meta", "sources"}))

    @model_validator(mode="after")
    def _cross_checks(self) -> "CyclingRuleSet":
        body = self.model_dump(exclude={"meta", "sources"})
        check_provenance(body, "cycling_rules", set(self.sources))

        ids = self.rule_ids()
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate rule ids: {duplicates}")

        if set(self.cycle_categories) != CYCLE_CATEGORIES:
            raise ValueError(f"cycle categories must be {sorted(CYCLE_CATEGORIES)}, got {sorted(self.cycle_categories)}")
        if set(self.principles) != PRINCIPLES:
            raise ValueError(f"principles must be {sorted(PRINCIPLES)}, got {sorted(self.principles)}")
        weights = {k: v for k, v in self.principle_weights.items() if k not in META_KEYS}
        if set(weights) != PRINCIPLES:
            raise ValueError(f"principle_weights must name every principle, got {sorted(weights)}")
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise ValueError(f"principle_weights must sum to 1, got {sum(weights.values())}")

        _check_matrix(self.separation_matrix)
        _check_project_target(self.widths_m["project_target"])
        _check_ist_mapping(self.routing_impedance)
        _rules_by_id(self.cycle_graph, GRAPH_RULE_IDS, "cycle_graph")
        _check_demand_model(self.demand_model)
        _check_network_design(self.network_design, self.routing_impedance)
        _check_principle_scoring(self.principle_scoring, self.principles, self.routing_impedance, self.widths_m)
        _check_facility_assignment(self.facility_assignment, self.widths_m)
        return self
