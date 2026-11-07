"""Sensitivity analysis of the cascade and the priority (guide 7.1, prompts/12_validation.md).

V-SENS-01: every assumption threshold the cascade reads, one at a time, -delta and +delta.
V-SENS-02: Monte Carlo; every weight and every V-SENS-01 threshold times a uniform factor in [1-delta, 1+delta].
V-UNC-01:  a segment is "unsicher" if its category differs from cat_proposed in at least min_change_rate of the runs.

Parameters are addressed by keys:
  thresholds.<name>      cascade or classification_policy threshold
  required_width.<name>  width referenced in a cascade condition
  conn_score.<feature>   weight in scores.conn_score
  risk_weights.<key>     weight in priority.risk_weights
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from config.schema.rules_model import WIDTH_REF, RuleSet, Threshold
from pipeline.lib import classify as cl
from pipeline.lib import discrepancy as disc
from pipeline.lib import parallel
from pipeline.lib.features import weighted_score

CONN = "conn_score"


@dataclass(frozen=True)
class Param:
    key: str
    base: float
    group: str    # threshold | conn_weight | risk_weight
    effect: str   # category | confidence | priority
    source: str   # rule id or rules.yaml section (for the report)


# --- parameters ------------------------------------------------------------------------------


def varied_parameters(rules: RuleSet) -> list[Param]:
    """Assumptions varied by V-SENS-01/02, in rules.yaml order."""
    out = []
    for r in rules.classification:
        for name, t in r.thresholds.items():
            if t.source_type == "assumption":
                out.append(Param(f"thresholds.{name}", t.value, "threshold", "category", r.id))
    seen = set()
    for r in rules.classification:
        for name in WIDTH_REF.findall(r.if_ + " " + r.then):
            entry = rules.required_width[name]
            if name not in seen and entry.source_type == "assumption" and entry.value is not None:
                seen.add(name)
                out.append(Param(f"required_width.{name}", entry.value, "threshold", "category", r.id))
    for p in rules.classification_policy:
        for name, t in p.thresholds.items():
            if t.source_type == "assumption":
                out.append(Param(f"thresholds.{name}", t.value, "threshold", "confidence", p.id))
    for feature, w in rules.scores[CONN].weights.items():
        out.append(Param(f"{CONN}.{feature}", w, "conn_weight", "category", f"scores.{CONN}"))
    for key, w in rules.priority.risk_weights.items():
        out.append(Param(f"risk_weights.{key}", w, "risk_weight", "priority", rules.priority.risk.id))
    return out


_STAGE_REASONS = {
    "network": "Netz (Stufe 2): wirkt nur über einen neuen Lauf ab make network",
    "conflation": "Conflation (Stufe 3): wirkt nur über einen neuen Lauf ab make conflate",
    "features": "Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features",
    "crosssection": "Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection",
    "coherence": "Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht",
    "discrepancy": "Diskrepanz: ändert die Kategorie nicht",
    "priority": "Priorität: Zuordnung der Unfälle und Radien je Abschnitt bleiben fest; nur Gewichte variiert",
    "feasibility_classes": "Machbarkeit: ändert die Kategorie nicht",
    "required_width": "Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade",
}


def _threshold_rows(section: str, rule_id: str, thresholds: dict[str, Threshold]) -> list[dict]:
    return [{"path": f"{section}.{rule_id}.{name}", "value": t.value, "unit": t.unit, "reason": _STAGE_REASONS[section]}
            for name, t in thresholds.items() if t.source_type == "assumption"]


def fixed_assumptions(rules: RuleSet) -> list[dict]:
    """Assumption thresholds that the analysis lists but does not vary: path, value, unit, reason."""
    rows = []
    for section in ("network", "conflation", "features", "crosssection"):
        for r in getattr(rules, section).rules:
            rows += _threshold_rows(section, r.id, r.thresholds)
    for r in rules.coherence:
        rows += _threshold_rows("coherence", r.id, r.thresholds)
        if r.source_type == "assumption":
            for key, v in (r.model_extra or {}).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    rows.append({"path": f"coherence.{r.id}.{key}", "value": v, "unit": key.rsplit("_", 1)[-1],
                                 "reason": _STAGE_REASONS["coherence"]})
    d = rules.discrepancy
    rows += [{"path": f"discrepancy.{d.speed.id}.severity_{lv.severity}", "value": lv.min_excess_kmh, "unit": "km/h",
              "reason": _STAGE_REASONS["discrepancy"]} for lv in d.speed.levels if lv.source_type == "assumption"]
    rows += [{"path": f"discrepancy.{d.use.id}.severity_{lv.severity}", "value": lv.factor, "unit": "Faktor",
              "reason": _STAGE_REASONS["discrepancy"]} for lv in d.use.levels if lv.source_type == "assumption"]
    rows += _threshold_rows("priority", rules.priority.risk.id, rules.priority.risk.thresholds)
    for key, c in rules.feasibility_classes.items():
        if c.source_type == "assumption":
            rows.append({"path": f"feasibility_classes.{key}", "value": c.min if c.min is not None else c.max,
                         "unit": "width_ratio", "reason": _STAGE_REASONS["feasibility_classes"]})
    varied = {p.key for p in varied_parameters(rules)}
    for key, w in rules.required_width.items():
        if w.source_type == "assumption" and f"required_width.{key}" not in varied:
            rows.append({"path": f"required_width.{key}", "value": w.value if w.value is not None else w.range[0],
                         "unit": "m", "reason": _STAGE_REASONS["required_width"]})
    return rows


def with_values(rules: RuleSet, values: dict[str, float]) -> RuleSet:
    """Deep copy of rules with the given parameters replaced; KeyError for an unknown key."""
    out = rules.model_copy(deep=True)
    for key, v in values.items():
        section, name = key.split(".", 1)
        if section == "thresholds":
            hit = [r.thresholds[name] for r in [*out.classification, *out.classification_policy] if name in r.thresholds]
            if not hit:
                raise KeyError(key)
            for t in hit:
                t.value = float(v)
        elif section == "required_width":
            out.required_width[name].value = float(v)
        elif section == CONN:
            if name not in out.scores[CONN].weights:
                raise KeyError(key)
            out.scores[CONN].weights[name] = float(v)
        elif section == "risk_weights":
            if name not in out.priority.risk_weights:
                raise KeyError(key)
            out.priority.risk_weights[name] = float(v)
        else:
            raise KeyError(key)
    return out


# --- classification --------------------------------------------------------------------------


def conn_score(df: pd.DataFrame, rules: RuleSet) -> tuple[pd.Series, pd.Series]:
    """conn_score with the weights of rules; second value = share of the weight sum that had a value."""
    weights = rules.scores[CONN].weights
    score, available = weighted_score(df, weights)
    return score, available / sum(weights.values())


Post = Callable[[pd.Series, RuleSet], pd.Series]


def categories(df: pd.DataFrame, rules: RuleSet, post: Post | None = None) -> pd.Series:
    """cat_proposed for each row with conn_score recomputed from the normalised features.

    post: optional step after the cascade (harmonisation H-STR-01), gets and returns the categories."""
    score, share = conn_score(df, rules)
    data = df.assign(conn_score=score, conn_weight_available=share)
    cols = cl.classification_inputs(rules)
    data = data.reindex(columns=cols)
    cats = [cl.classify_segment(rec, rules)["cat_proposed"] for rec in data.to_dict("records")]
    cl.clear_cache()
    out = pd.Series(cats, index=df.index, dtype="object")
    return post(out, rules) if post else out


def one_at_a_time(df: pd.DataFrame, rules: RuleSet, params: list[Param], delta: float,
                  post: Post | None = None) -> pd.DataFrame:
    """V-SENS-01: categories with each parameter at base*(1-delta) ('<key>:-') and base*(1+delta) ('<key>:+')."""
    variants = [(f"{p.key}:{sign}", {p.key: p.base * f}) for p in params for sign, f in (("-", 1 - delta), ("+", 1 + delta))]
    cats = parallel.pmap(lambda i: categories(df, with_values(rules, variants[i][1]), post), len(variants))
    return pd.DataFrame({name: c for (name, _), c in zip(variants, cats)}, index=df.index)


def oat_changes(base: pd.Series, oat: pd.DataFrame) -> pd.Series:
    """Per segment the list of one-at-a-time variants that change its category."""
    changed = oat.ne(base, axis=0)
    return changed.apply(lambda row: [c for c in oat.columns if row[c]], axis=1)


# --- Monte Carlo -----------------------------------------------------------------------------


def sample_factors(runs: int, n_params: int, delta: float, seed: int) -> np.ndarray:
    """runs x n_params factors, uniform in [1-delta, 1+delta], reproducible with seed."""
    rng = np.random.default_rng(seed)
    return rng.uniform(1 - delta, 1 + delta, size=(runs, n_params))


def run_values(params: list[Param], factors: np.ndarray) -> dict[str, float]:
    return {p.key: p.base * float(f) for p, f in zip(params, factors)}


def monte_carlo(df: pd.DataFrame, rules: RuleSet, params: list[Param], factors: np.ndarray,
                progress: Callable[[int], None] | None = None, post: Post | None = None) -> pd.DataFrame:
    """V-SENS-02: one column of categories per run (columns 0..runs-1)."""
    cats = parallel.pmap(lambda i: categories(df, with_values(rules, run_values(params, factors[i])), post), len(factors),
                         progress=progress)
    return pd.DataFrame(dict(enumerate(cats)), index=df.index)


def change_summary(base: pd.Series, runs: pd.DataFrame, min_rate: float) -> pd.DataFrame:
    """change_rate (share of runs with another category), uncertain (>= min_rate), most frequent other category."""
    changed = runs.ne(base, axis=0)
    rate = changed.mean(axis=1)
    alt, alt_share = [], []
    for idx in runs.index:
        other = runs.loc[idx][changed.loc[idx]]
        if other.empty:
            alt.append(None)
            alt_share.append(0.0)
        else:
            counts = other.value_counts()
            top = sorted(counts[counts == counts.max()].index)[0]
            alt.append(top)
            alt_share.append(counts[top] / runs.shape[1])
    return pd.DataFrame({"change_rate": rate, "uncertain": rate >= min_rate - 1e-12,
                         "alt_category": pd.Series(alt, index=runs.index, dtype="object"),
                         "alt_share": alt_share}, index=runs.index)


# --- priority --------------------------------------------------------------------------------


def risk(df: pd.DataFrame, rules: RuleSet) -> pd.Series:
    """P-RISK-01 risk with the weights of rules (severe crashes counted severe_or_fatal_weight times).

    df needs crashes_ped_cyc, crashes_severe_fatal, length_m, in_cycle_network, population_100m_norm and
    schools_or_kitas_within_m; normalisation over the rows of df as in stage 8.
    """
    w = rules.priority.risk_weights[rules.priority.risk.severe_weight_key]
    severe = pd.to_numeric(df["crashes_severe_fatal"], errors="coerce").astype("float64")
    weighted = pd.to_numeric(df["crashes_ped_cyc"], errors="coerce").astype("float64") - severe + w * severe
    data = df.assign(crash_weighted_per_km=disc.crashes_per_km(weighted, df["length_m"], rules))
    return disc.risk_frame(data, rules)["risk"]


def priorities(df: pd.DataFrame, rules: RuleSet) -> pd.Series:
    """formula max(severity) * risk with df['disc_max'] fixed; NaN if not checkable."""
    r = risk(df, rules)
    vals = [disc.priority(m, x) for m, x in zip(df["disc_max"], r)]
    return pd.Series([np.nan if v is None else v for v in vals], index=df.index, dtype="float64")


def priority_runs(df: pd.DataFrame, rules: RuleSet, params: list[Param], factors: np.ndarray) -> pd.DataFrame:
    """Priority per run with the same factor rows as monte_carlo (only risk weights matter here)."""
    out = {}
    for i, row in enumerate(factors):
        values = {k: v for k, v in run_values(params, row).items() if k.startswith("risk_weights.")}
        out[i] = priorities(df, with_values(rules, values))
    return pd.DataFrame(out, index=df.index)


def _top(values: pd.Series, ids: pd.Series, top_n: int) -> list[str]:
    d = pd.DataFrame({"v": values.to_numpy(), "id": ids.to_numpy()})
    d = d[d["v"] > 0].sort_values(["v", "id"], ascending=[False, True])
    return d["id"].head(top_n).tolist()


def top_stability(base: pd.Series, runs: pd.DataFrame, ids: pd.Series, top_n: int) -> dict:
    """How often the base Top N (priority > 0, ties by id as in stage 8) stay in the Top N of each run."""
    base_top = _top(base, ids, top_n)
    tops = [set(_top(runs[c], ids, top_n)) for c in runs.columns]
    stay = {sid: sum(sid in t for t in tops) / len(tops) for sid in base_top}
    overlap = float(np.mean([len(set(base_top) & t) / len(base_top) for t in tops])) if base_top else float("nan")
    return {"base_top": base_top, "stay_share": stay, "mean_overlap": overlap}
