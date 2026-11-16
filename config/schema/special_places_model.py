"""Schema of config/special_places.yaml (prompts/26): places proposed, decided or built by others, shown next to the
rule result. Not part of the classification."""

import datetime as dt
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Kind = Literal["proposal", "decided", "built"]
_SEGMENT_ID = re.compile(r"^seg_[0-9a-f]+$")
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileChange(_Strict):
    """How the measure changes the inputs of our cross-section logic (pipeline/lib/profile.py) for the sketch
    "Querschnitt im Vorschlag"; everything else stays as in the rule result."""
    cat: str | None = None
    facility: str | None = None


class Measure(_Strict):
    label_plain: str
    profile: ProfileChange | None = None


class Source(_Strict):
    title: str
    url: str = Field(pattern=r"^https://")
    checked: dt.date


class Theme(_Strict):
    palette: dict[str, str]
    pattern: dict[str, Literal["solid", "dashed"]]

    @field_validator("palette")
    @classmethod
    def _colours(cls, v: dict[str, str]) -> dict[str, str]:
        missing = {"main"} - set(v)
        if missing:
            raise ValueError(f"palette needs {sorted(missing)}")
        bad = [k for k, c in v.items() if not _HEX.match(c)]
        if bad:
            raise ValueError(f"palette colours must be #rrggbb: {bad}")
        return v


class SegmentGroup(_Strict):
    measure: str
    streets: list[str] = Field(min_length=1)
    segment_ids: list[str] = Field(min_length=1)

    @field_validator("segment_ids")
    @classmethod
    def _ids(cls, v: list[str]) -> list[str]:
        bad = [s for s in v if not _SEGMENT_ID.match(s)]
        if bad:
            raise ValueError(f"invalid segment ids: {bad}")
        return v


class Texts(_Strict):
    glance: str
    explain: str
    details: str


class Place(_Strict):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    title: str
    kind: Kind
    initiator: str
    status: str
    status_date: dt.date
    status_note: str | None = None
    sources: list[Source] = Field(min_length=1)
    exceptions: list[str] = []
    theme: Theme
    segments: list[SegmentGroup] = Field(min_length=1)
    texts: Texts

    def segment_ids(self) -> list[str]:
        return [s for g in self.segments for s in g.segment_ids]


class Meta(_Strict):
    version: str
    updated: dt.date


class SpecialPlaces(_Strict):
    meta: Meta
    measures: dict[str, Measure]
    places: list[Place]

    @model_validator(mode="after")
    def _consistent(self) -> "SpecialPlaces":
        ids = [p.id for p in self.places]
        if len(ids) != len(set(ids)):
            raise ValueError("place ids must be unique")
        for p in self.places:
            unknown = {g.measure for g in p.segments} - set(self.measures)
            if unknown:
                raise ValueError(f"{p.id}: unknown measures {sorted(unknown)}")
            unknown = set(p.theme.pattern) - set(self.measures)
            if unknown:
                raise ValueError(f"{p.id}: theme.pattern for unknown measures {sorted(unknown)}")
            seg = p.segment_ids()
            dup = sorted({s for s in seg if seg.count(s) > 1})
            if dup:
                raise ValueError(f"{p.id}: segment ids in more than one group: {dup}")
        return self
