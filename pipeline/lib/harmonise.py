"""Harmonisation of categories along streets (H-STR-01, prompts follow-up 2026-11-04).

A street (stroke, pipeline/lib/coherence.py: strokes) is split into runs of equal category. Short runs
(< min_run_m from coherence N2) are adjusted in four steps per pass, repeated until nothing changes:
  1. ETW30 run between two GOW runs -> GOW (lower Soll speed of the two neighbours).
  2. GOW run between two ETW30 runs -> ETW30.
  3. GOW50 run between two GOW30 runs (gap closing: shorter than gap_close_m, F07), or at the end of the street
     next to GOW30 (shorter than min_run_m) -> GOW30.
  4. GOW30 run between GOW50 runs (or at the end next to GOW50) stays GOW30 and is extended into the
     neighbouring GOW50 segments, shorter neighbour first, until it reaches min_run_m.
Locked categories (SW, ETW_ERF, rural) and locked segments (approved overrides) are never changed.
Works on segment ids only, so the sensitivity runs can reuse the strokes.

H-PAIR-01 (rules.yaml 0.23.0): separately mapped carriageways of one street (carriageway_pairs) get the same speed,
the lower one wins (pair_carriageways). Strokes run along one carriageway only, so H-STR-01 never sees the other one.
"""

import numpy as np
import shapely

from config.schema.rules_model import RuleSet

GOW = {"GOW50", "GOW30"}
ETW = "ETW30"
RULE_ID = "H-STR-01"
PAIR_RULE_ID = "H-PAIR-01"


def _runs(stroke: list[str], key) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    for sid in stroke:
        k = key(sid)
        if out and out[-1][0] == k:
            out[-1][1].append(sid)
        else:
            out.append((k, [sid]))
    return out


def harmonise(strokes: list[list[str]], cats: dict[str, str], lengths: dict[str, float], rules: RuleSet,
              locked: set[str] | None = None) -> tuple[dict[str, str], dict[str, list[dict]]]:
    """New category per segment id and, per changed segment, the list of steps applied."""
    rule = rules.harmonisation.rule(RULE_ID)
    min_run = rules.coherence_rule(rule.min_run_from).param("min_run_m")
    gap_close = rule.thresholds["gap_close_m"].value if "gap_close_m" in rule.thresholds else min_run
    locked_cats = set(rule.locked_categories)
    locked = set(locked or ())
    speed = {c: (v.speed_kmh if v.speed_kmh is not None else 999) for c, v in rules.categories.items()}
    cur = dict(cats)
    trace: dict[str, list[dict]] = {}

    def length(sids):
        return float(sum(lengths[s] for s in sids))

    def free(sids):
        return not any(s in locked or cur[s] in locked_cats for s in sids)

    def change(sids, to, step, run_m, neighbours, pass_no):
        for s in sids:
            if cur[s] != to:
                trace.setdefault(s, []).append({"id": RULE_ID, "step": step, "from": cur[s], "to": to,
                                                "run_m": round(run_m, 1), "neighbours": neighbours,
                                                "pass": pass_no})
                cur[s] = to

    def group(sid):
        c = cur[sid]
        return "GOW" if c in GOW else c

    def pass_once(stroke, pass_no) -> bool:
        changed = False
        # step 1: ETW30 island between GOW runs
        runs = _runs(stroke, group)
        for i in range(1, len(runs) - 1):
            k, sids = runs[i]
            if k == ETW and runs[i - 1][0] == "GOW" and runs[i + 1][0] == "GOW" and length(sids) < min_run and free(sids):
                left, right = cur[runs[i - 1][1][-1]], cur[runs[i + 1][1][0]]
                to = min((left, right), key=lambda c: speed[c])
                change(sids, to, 1, length(sids), [left, right], pass_no)
                changed = True
        # step 2: GOW island between ETW30 runs
        runs = _runs(stroke, group)
        for i in range(1, len(runs) - 1):
            k, sids = runs[i]
            if k == "GOW" and runs[i - 1][0] == ETW and runs[i + 1][0] == ETW and length(sids) < min_run and free(sids):
                change(sids, ETW, 2, length(sids), [ETW, ETW], pass_no)
                changed = True
        # step 3: GOW50 gap between GOW30 runs (< gap_close_m), or at the end next to GOW30 (< min_run_m)
        runs = _runs(stroke, lambda s: cur[s])
        for i, (k, sids) in enumerate(runs):
            if k != "GOW50" or not free(sids):
                continue
            left = runs[i - 1][0] if i > 0 else None
            right = runs[i + 1][0] if i < len(runs) - 1 else None
            limit = gap_close if (left, right) == ("GOW30", "GOW30") else min_run
            if length(sids) >= limit:
                continue
            if (left, right) in {("GOW30", "GOW30"), ("GOW30", None), (None, "GOW30")}:
                change(sids, "GOW30", 3, length(sids), [left, right], pass_no)
                changed = True
        # step 4: short GOW30 run between GOW50 (or at the end next to GOW50) is extended
        done: set[str] = set()
        while True:
            runs = _runs(stroke, lambda s: cur[s])
            target = None
            for i, (k, sids) in enumerate(runs):
                if k != "GOW30" or sids[0] in done or length(sids) >= min_run:
                    continue
                left = runs[i - 1][0] if i > 0 else None
                right = runs[i + 1][0] if i < len(runs) - 1 else None
                if (left, right) in {("GOW50", "GOW50"), ("GOW50", None), (None, "GOW50")}:
                    target = (sids, left, right)
                    break
            if target is None:
                break
            sids, left, right = target
            done.add(sids[0])
            start, end = stroke.index(sids[0]), stroke.index(sids[-1])
            run_m = length(sids)
            while run_m < min_run:
                cands = []
                if start > 0 and cur[stroke[start - 1]] == "GOW50" and free([stroke[start - 1]]):
                    cands.append((lengths[stroke[start - 1]], 0, start - 1))
                if end < len(stroke) - 1 and cur[stroke[end + 1]] == "GOW50" and free([stroke[end + 1]]):
                    cands.append((lengths[stroke[end + 1]], 1, end + 1))
                if not cands:
                    break
                _, side, idx = min(cands)
                change([stroke[idx]], "GOW30", 4, run_m, [left, right], pass_no)
                run_m += lengths[stroke[idx]]
                changed = True
                if side == 0:
                    start = idx
                else:
                    end = idx
            done.add(stroke[start])
        return changed

    for stroke in strokes:
        stroke = [s for s in stroke if s in cur]
        for p in range(1, rule.max_passes + 1):
            if not pass_once(stroke, p):
                break
    return cur, trace


def _axis_deg(g) -> float:
    """Undirected direction of the chord from first to last point, 0-180."""
    (x0, y0), (x1, y1) = g.coords[0], g.coords[-1]
    return float(np.degrees(np.arctan2(y1 - y0, x1 - x0)) % 180)


def carriageway_pairs(seg, rules: RuleSet) -> list[dict]:
    """H-PAIR-01: pairs of separately mapped carriageways.

    seg: segment_id, name, oneway, node_u, node_v, geometry (EPSG:25832). A pair is two oneway segments of the same
    name without a shared node, at most pair_max_angle_deg apart, with the midpoint of the shorter one at most
    pair_max_distance_m from the longer one and at least pair_min_overlap_share of the shorter one projected onto it.
    """
    t = rules.harmonisation.rule(PAIR_RULE_ID).thresholds
    max_dist, max_angle = t["pair_max_distance_m"].value, t["pair_max_angle_deg"].value
    min_overlap = t["pair_min_overlap_share"].value
    cand = seg[seg["oneway"].fillna(False).astype(bool) & seg["name"].notna()].reset_index(drop=True)
    if len(cand) < 2:
        return []
    geoms = cand.geometry.to_numpy()
    left, right = shapely.STRtree(geoms).query(geoms, predicate="dwithin", distance=max_dist)
    keep = left < right
    out = []
    for i, j in zip(left[keep], right[keep]):
        a, b = cand.iloc[i], cand.iloc[j]
        if a["name"] != b["name"] or {a["node_u"], a["node_v"]} & {b["node_u"], b["node_v"]}:
            continue
        angle = abs(_axis_deg(geoms[i]) - _axis_deg(geoms[j]))
        angle = min(angle, 180 - angle)
        if angle > max_angle:
            continue
        short, long_ = (geoms[i], geoms[j]) if geoms[i].length <= geoms[j].length else (geoms[j], geoms[i])
        if short.length == 0:
            continue
        ends = shapely.points([short.coords[0], short.coords[-1]])
        overlap = abs(float(np.diff(long_.project(ends))[0])) / short.length
        dist = long_.distance(short.interpolate(0.5, normalized=True))
        if overlap < min_overlap or dist > max_dist:
            continue
        out.append({"a": a["segment_id"], "b": b["segment_id"], "dist_m": round(float(dist), 1),
                    "angle_deg": round(angle, 1), "overlap_share": round(min(overlap, 1.0), 2)})
    return out


def pair_carriageways(pairs: list[dict], cats: dict[str, str], rules: RuleSet,
                      locked: set[str] | None = None) -> tuple[dict[str, str], dict[str, list[dict]]]:
    """H-PAIR-01: GOW50 with a GOW30 partner becomes GOW30, repeated over chains of pairs until nothing changes."""
    rule = rules.harmonisation.rule(PAIR_RULE_ID)
    locked_cats = set(rule.locked_categories)
    locked = set(locked or ())
    cur = dict(cats)
    trace: dict[str, list[dict]] = {}
    for p_no in range(1, rule.max_passes + 1):
        changed = False
        for p in pairs:
            a, b = p["a"], p["b"]
            if a not in cur or b not in cur or {cur[a], cur[b]} != GOW:
                continue
            sid, partner = (a, b) if cur[a] == "GOW50" else (b, a)
            if sid in locked or cur[sid] in locked_cats:
                continue
            trace.setdefault(sid, []).append({"id": PAIR_RULE_ID, "from": cur[sid], "to": "GOW30", "partner": partner,
                                              "dist_m": p["dist_m"], "overlap_share": p["overlap_share"], "pass": p_no})
            cur[sid] = "GOW30"
            changed = True
        if not changed:
            break
    return cur, trace


def harmonise_all(strokes: list[list[str]], pairs: list[dict], cats: dict[str, str], lengths: dict[str, float],
                  rules: RuleSet, locked: set[str] | None = None) -> tuple[dict[str, str], dict[str, list[dict]]]:
    """H-STR-01, then H-PAIR-01 and H-STR-01 in turns until H-PAIR-01 changes nothing; steps per segment in order."""
    cur, trace = harmonise(strokes, cats, lengths, rules, locked=locked)
    for _ in range(rules.harmonisation.rule(PAIR_RULE_ID).max_passes):
        cur, paired = pair_carriageways(pairs, cur, rules, locked=locked)
        if not paired:
            break
        cur, along = harmonise(strokes, cur, lengths, rules, locked=locked)
        for t in (paired, along):
            for sid, steps in t.items():
                trace.setdefault(sid, []).extend(steps)
    return cur, trace
