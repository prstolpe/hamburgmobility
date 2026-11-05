"""pydantic model for config/cycling_rules.yaml (cycle network, five principles, separation matrix, widths).

Deep sections stay plain dicts; the cross-checks below validate provenance, ids, categories and
facility names. Rule texts stay strings; later prompts (15–18) evaluate them.
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


class CyclingRuleSet(_Strict):
    meta: Meta
    sources: dict[str, Source]
    cycle_categories: dict[str, dict[str, Any]]
    principles: dict[str, dict[str, Any]]
    principle_weights: dict[str, Any]
    routing_impedance: dict[str, Any]
    separation_matrix: dict[str, Any]
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
        return self
