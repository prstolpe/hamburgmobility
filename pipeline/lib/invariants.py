"""Executable invariants V-INV-01..09 (rules.yaml validation.invariants, Review 2026-11 structural rec. 6).

Each check reads the current data/interim files (and the three rule files) and returns an InvariantResult with the
number of violating rows. pipeline/validate.py writes the results to reports/validation.md; the data tests in
tests/ assert them (tests/test_invariants_data.py compares every result with `expected` in rules.yaml).
A check whose input file is missing returns status "not_checked".
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules, required_width_formula_mismatches

INTERIM = REPO_ROOT / "data" / "interim"
FILES = {"final": "final.parquet", "junctions": "junctions.parquet", "soll": "cross_section_soll.parquet",
         "facility": "cycle_facility.parquet", "ist": "ist_facility.parquet", "discrepancy": "discrepancy.parquet",
         "principles": "cycle_principles.parquet", "network": "cycle_network.parquet"}
ETW_CATEGORIES = ("ETW30", "ETW_ERF")
# Abbaustufen, bis zu denen V-INV-05 ein "passt" aus S-XS-06 erwartet (D6/D7 sind reine Flags).
V_INV_05_STEPS = frozenset({"D1", "D2", "D3", "fallback", "D4"})
V_INV_05_FLAG_STEPS = frozenset({"D6", "D7"})


@dataclass
class InvariantResult:
    id: str
    status: str            # ok | violated | not_checked
    n: int | None          # number of violating rows (segments, junctions, categories, entries)
    detail: str
    inputs: list[str]      # interim files read (with modification time in the report)

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _path(key: str, interim: Path) -> Path:
    return interim / FILES[key]


def _missing(inv_id: str, keys: list[str], interim: Path) -> InvariantResult | None:
    missing = [FILES[k] for k in keys if not _path(k, interim).exists()]
    if missing:
        return InvariantResult(inv_id, "not_checked", None, "fehlt: " + ", ".join(missing), [FILES[k] for k in keys])
    return None


def _result(inv_id: str, n: int, detail_ok: str, detail_bad: str, keys: list[str]) -> InvariantResult:
    return InvariantResult(inv_id, "ok" if n == 0 else "violated", int(n), detail_ok if n == 0 else detail_bad,
                           [FILES[k] for k in keys])


def file_times(inputs: list[str], interim: Path = INTERIM) -> str:
    out = []
    for f in inputs:
        p = interim / f
        if p.exists():
            out.append(f"{f} ({datetime.fromtimestamp(p.stat().st_mtime).strftime('%d.%m. %H:%M')})")
    return ", ".join(out)


def _flags(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.split("|")


def _effective_cat(soll: pd.DataFrame) -> pd.Series:
    """Category the c06 profile was built for: the D5 proposal (GOW30) where present, else cat_final."""
    return soll["cat_change_proposal"].fillna(soll["cat_final"])


# --- V-INV-01 ------------------------------------------------------------------------------------------------


def categories_without_matrix_or_profile(rules=None, cycling=None, design=None) -> dict[str, str]:
    """Categories that have neither (active matrix row and profile rule) nor an entry in no_profile_categories."""
    rules = rules or load_rules()
    cycling = cycling or load_cycling_rules()
    design = design or load_design_rules()
    matrix = cycling.separation_matrix
    rural = matrix.get("rural", {})
    prf = {r["id"]: r for r in design.profile_assignment["rules"]}
    no_profile = set(prf["PRF-04"]["no_profile_categories"])
    profile = set(prf["PRF-03"].get("parking_by_category") or {})
    bad = {}
    for cat in rules.categories:
        if cat in no_profile:
            continue
        if cat in rural:
            has_row = rural.get("status") != "inactive" and isinstance(rural[cat], dict)
        else:
            has_row = isinstance(matrix.get(cat), dict) and matrix[cat].get("status") != "inactive"
        missing = [w for w, ok in (("Matrixzeile", has_row), ("Profilregel", cat in profile)) if not ok]
        if missing:
            bad[cat] = " und ".join(missing) + " fehlt"
    return bad


def check_v_inv_01(interim: Path = INTERIM) -> InvariantResult:
    keys = ["final"]
    if (m := _missing("V-INV-01", keys, interim)):
        return m
    cats = pd.read_parquet(_path("final", interim), columns=["cat_final"])["cat_final"]
    bad = categories_without_matrix_or_profile()
    hit = cats.isin(list(bad))
    detail = "; ".join(f"{c}: {why}" for c, why in bad.items())
    return _result("V-INV-01", int(hit.sum()), f"alle {cats.nunique()} Kategorien in cat_final abgedeckt",
                   f"{int(hit.sum())} Abschnitte, {detail}", keys)


# --- V-INV-02, V-INV-07 (junctions) --------------------------------------------------------------------------


def check_v_inv_02(interim: Path = INTERIM) -> InvariantResult:
    keys = ["junctions"]
    if (m := _missing("V-INV-02", keys, interim)):
        return m
    j = pd.read_parquet(_path("junctions", interim), columns=["junction_type_soll", "conflict_flags"])
    bad = j["junction_type_soll"].isna() | _flags(j["conflict_flags"]).map(lambda xs: "no_rule" in xs)
    return _result("V-INV-02", int(bad.sum()), f"{len(j)} Knoten, alle mit Soll-Typ",
                   f"{int(bad.sum())} von {len(j)} Knoten ohne Soll-Typ bzw. mit no_rule", keys)


def check_v_inv_07(interim: Path = INTERIM) -> InvariantResult:
    keys = ["junctions"]
    if (m := _missing("V-INV-07", keys, interim)):
        return m
    j = pd.read_parquet(_path("junctions", interim), columns=["junction_type_soll", "cyclist_treatment"])
    jc = _flags(j["cyclist_treatment"])
    jc01_bad = jc.map(lambda xs: "JC-01" in xs) & (j["junction_type_soll"] != "roundabout_single_lane_cycle_priority")
    turbo_bad = (j["junction_type_soll"] == "turbo_roundabout") & ~jc.map(lambda xs: "JC-06" in xs)
    n = int((jc01_bad | turbo_bad).sum())
    return _result("V-INV-07", n, f"JC-01 an {int(jc.map(lambda xs: 'JC-01' in xs).sum())} einstreifigen Kreiseln, "
                   f"{int((j['junction_type_soll'] == 'turbo_roundabout').sum())} Turbokreisel mit JC-06",
                   f"JC-01 außerhalb einstreifiger Kreisel {int(jc01_bad.sum())}, Turbokreisel ohne JC-06 "
                   f"{int(turbo_bad.sum())}", keys)


# --- V-INV-03, V-INV-04, V-INV-05 (cross-section Soll, facility) ---------------------------------------------


def check_v_inv_03(interim: Path = INTERIM) -> InvariantResult:
    keys = ["soll"]
    if (m := _missing("V-INV-03", keys, interim)):
        return m
    s = pd.read_parquet(_path("soll", interim), columns=["cat_final", "cat_change_proposal", "profile_elements",
                                                          "lanes_per_dir_soll", "median_soll"])
    cat = _effective_cat(s)
    el = s["profile_elements"].map(lambda v: {e["element"] for e in json.loads(v)} if isinstance(v, str) else set())
    gow50 = (cat == "GOW50") & el.map(lambda e: "parking_parallel" in e or "cycle_lane" in e)
    gow30 = (cat == "GOW30") & ((s["lanes_per_dir_soll"] != "1") | s["median_soll"].fillna(False).astype(bool)
                                | el.map(lambda e: "median" in e))
    n = int((gow50 | gow30).sum())
    return _result("V-INV-03", n, "kein verbotenes Element in GOW50- und GOW30-Profilen",
                   f"GOW50 mit Parken/Radfahrstreifen {int(gow50.sum())}, GOW30 mit 2. Fahrstreifen/Mittelstreifen "
                   f"{int(gow30.sum())}", keys)


def check_v_inv_04(interim: Path = INTERIM) -> InvariantResult:
    keys = ["facility", "soll", "final"]
    if (m := _missing("V-INV-04", keys, interim)):
        return m
    from pipeline.lib import facility as fa
    limit = fa.FacilityParams.from_rules(load_cycling_rules()).high_volume["GOW30"].dtv_above
    fac = pd.read_parquet(_path("facility", interim), columns=["cat_final", "dtv_official", "cycle_facility_soll"])
    c05 = (fac["cat_final"] == "GOW30") & (fac["dtv_official"] > limit) & (fac["cycle_facility_soll"] == "cycle_lane")
    s = pd.read_parquet(_path("soll", interim), columns=["segment_id", "cat_final", "cat_change_proposal",
                                                          "cycle_facility_final"])
    dtv = s["segment_id"].map(pd.read_parquet(_path("final", interim), columns=["segment_id", "dtv_official"])
                              .set_index("segment_id")["dtv_official"])
    c06 = (_effective_cat(s) == "GOW30") & (dtv > limit) & (s["cycle_facility_final"] == "cycle_lane")
    n = int(c05.sum() + c06.sum())
    return _result("V-INV-04", n, f"kein Radfahrstreifen an GOW30 über {limit:,.0f} Kfz/24 h".replace(",", "."),
                   f"c05 {int(c05.sum())}, c06 {int(c06.sum())} Abschnitte mit Radfahrstreifen über {limit:g}", keys)


def v_inv_05_violations(soll: pd.DataFrame, final: pd.DataFrame) -> pd.DataFrame:
    """Segments that fit in S-XS-06 (feasibility of their category) but not in c06 after at most D4."""
    target = {"GOW50": "feasibility_GOW50", "GOW30": "feasibility_GOW30_narrow", "ETW30": "feasibility_ETW30"}
    final = final.set_index("segment_id")
    feas = pd.Series(None, index=soll.index, dtype=object)
    for cat, col in target.items():
        m = soll["cat_final"] == cat
        feas[m] = soll.loc[m, "segment_id"].map(final[col]).to_numpy()
    rated = soll["fit_class"].notna() & (feas == "fits")
    steps = soll["degrade_steps_applied"].fillna("").str.split("|").map(
        lambda xs: {x for x in xs if x} - V_INV_05_FLAG_STEPS)
    ok = soll["fit_class"].isin(["fits", "fits_after_degrade"]) & steps.map(lambda st: st <= V_INV_05_STEPS)
    return soll[rated & ~ok]


def check_v_inv_05(interim: Path = INTERIM) -> InvariantResult:
    keys = ["soll", "final"]
    if (m := _missing("V-INV-05", keys, interim)):
        return m
    soll = pd.read_parquet(_path("soll", interim), columns=["segment_id", "cat_final", "fit_class",
                                                             "degrade_steps_applied"])
    final = pd.read_parquet(_path("final", interim), columns=["segment_id", "length_m", "feasibility_GOW50",
                                                               "feasibility_GOW30_narrow", "feasibility_ETW30"])
    bad = v_inv_05_violations(soll, final)
    km = bad["segment_id"].map(final.set_index("segment_id")["length_m"]).sum() / 1000
    by_cat = ", ".join(f"{c} {n}" for c, n in bad["cat_final"].value_counts().items())
    return _result("V-INV-05", len(bad), "alle in S-XS-06 passenden Abschnitte passen in c06 spätestens nach D4",
                   f"{len(bad)} Abschnitte ({km:.1f} km): {by_cat}".replace(".", ","), keys)


# --- V-INV-06 (config) -----------------------------------------------------------------------------------------


def check_v_inv_06(interim: Path = INTERIM) -> InvariantResult:
    bad = required_width_formula_mismatches(load_rules(), load_cycling_rules(), load_design_rules())
    return InvariantResult("V-INV-06", "ok" if not bad else "violated", len(bad),
                           "required_width: value = formula" if not bad else "; ".join(bad), [])


# --- V-INV-08 (Ist facility) -----------------------------------------------------------------------------------


def _same(a: pd.Series, b: pd.Series) -> pd.Series:
    a, b = a.astype("object"), b.astype("object")
    return (a == b) | (a.isna() & b.isna())


def check_v_inv_08(interim: Path = INTERIM) -> InvariantResult:
    keys = ["ist", "facility", "discrepancy", "principles", "network"]
    if (m := _missing("V-INV-08", keys, interim)):
        return m
    ist = pd.read_parquet(_path("ist", interim)).set_index("segment_id")
    fac = pd.read_parquet(_path("facility", interim), columns=["segment_id", "cycle_facility_ist", "cycle_osm_ist"]
                          ).set_index("segment_id").join(ist.add_suffix("_s13"), how="inner")
    c05 = int((~(_same(fac["cycle_facility_ist"], fac["cycle_facility_ist_s13"])
                 & _same(fac["cycle_osm_ist"], fac["cycle_osm_ist_s13"]))).sum())
    cols = ["cycle_facility_ist", "separated_cycle_track_present", "parallel_cycle_route_present"]
    d = pd.read_parquet(_path("discrepancy", interim), columns=["segment_id", *cols]).set_index("segment_id")
    d = d.join(ist.add_suffix("_s13"), how="inner")
    ok = pd.Series(True, index=d.index)
    for c in cols:
        ok &= _same(d[c].astype("boolean") if c != "cycle_facility_ist" else d[c],
                    d[f"{c}_s13"].astype("boolean") if c != "cycle_facility_ist" else d[f"{c}_s13"])
    s08 = int((~ok).sum())
    pri = pd.read_parquet(_path("principles", interim), columns=["level", "id", "facility_ist"])
    pri = pri[pri["level"] == "edge"].set_index("id")
    net = pd.read_parquet(_path("network", interim), columns=["edge_id", "kind", "segment_id", "sidepath_of"]
                          ).set_index("edge_id")
    owner = net["segment_id"].where(net["kind"] == "road").fillna(net["sidepath_of"].where(net["kind"] == "path"))
    owner = owner.reindex(pri.index).dropna()
    owner = owner[owner.isin(ist.index)]
    c04 = int((pri.loc[owner.index, "facility_ist"].to_numpy()
               != ist.loc[owner.to_numpy(), "cycle_facility_ist"].to_numpy()).sum())
    n = c05 + s08 + c04
    return _result("V-INV-08", n, f"identisch in c05 ({len(fac)}), s08 ({len(d)}) und c04 ({len(owner)} Kanten)",
                   f"abweichend: c05 {c05}, s08 {s08}, c04 {c04}", keys)


# --- V-INV-09 (HVS) ----------------------------------------------------------------------------------------------


def v_inv_09_violations(final: pd.DataFrame) -> pd.DataFrame:
    """HVS segments with cat_final ETW30/ETW_ERF that have no approved override."""
    from pipeline.lib.overrides import APPLIED_STATUS, read_overrides
    ov = read_overrides()
    justified = set(ov.loc[ov["review_status"] == APPLIED_STATUS, "segment_id"])
    hvs = final["in_hvs"].fillna(False).astype(bool)
    return final[hvs & final["cat_final"].isin(ETW_CATEGORIES) & ~final["segment_id"].isin(justified)]


def check_v_inv_09(interim: Path = INTERIM) -> InvariantResult:
    keys = ["final"]
    if (m := _missing("V-INV-09", keys, interim)):
        return m
    final = pd.read_parquet(_path("final", interim), columns=["segment_id", "in_hvs", "cat_final", "cat_cascade",
                                                               "length_m"])
    bad = v_inv_09_violations(final)
    cascade = int(bad["cat_cascade"].isin(ETW_CATEGORIES).sum())
    detail = (f"{len(bad)} Abschnitte ({bad['length_m'].sum() / 1000:.1f} km): "
              f"{', '.join(f'{c} {n}' for c, n in bad['cat_final'].value_counts().items())}; "
              f"davon aus der Kaskade {cascade}, aus der Harmonisierung {len(bad) - cascade}").replace(".", ",")
    return _result("V-INV-09", len(bad), "kein HVS-Abschnitt als ETW30/ETW_ERF ohne approved Override", detail, keys)


CHECKS = {"V-INV-01": check_v_inv_01, "V-INV-02": check_v_inv_02, "V-INV-03": check_v_inv_03,
          "V-INV-04": check_v_inv_04, "V-INV-05": check_v_inv_05, "V-INV-06": check_v_inv_06,
          "V-INV-07": check_v_inv_07, "V-INV-08": check_v_inv_08, "V-INV-09": check_v_inv_09}


def run_all(rules=None, interim: Path = INTERIM) -> list[InvariantResult]:
    """All invariants listed in rules.yaml validation.invariants, in their order."""
    rules = rules or load_rules()
    return [CHECKS[inv.id](interim) for inv in rules.validation.invariants]
