"""Harmonisation of categories along streets (H-STR-01, prompts follow-up 2026-11-04).

A street (stroke, pipeline/lib/coherence.py: strokes) is split into runs of equal category. Short runs
(< min_run_m from coherence N2) are adjusted in four steps per pass, repeated until nothing changes:
  1. ETW30 run between two GOW runs -> GOW (lower Soll speed of the two neighbours).
  2. GOW run between two ETW30 runs -> ETW30.
  3. GOW50 run between two GOW30 runs, or at the end of the street next to GOW30 -> GOW30.
  4. GOW30 run between GOW50 runs (or at the end next to GOW50) stays GOW30 and is extended into the
     neighbouring GOW50 segments, shorter neighbour first, until it reaches min_run_m.
Locked categories (SW, ETW_ERF, rural) and locked segments (approved overrides) are never changed.
Works on segment ids only, so the sensitivity runs can reuse the strokes.
"""

from config.schema.rules_model import RuleSet

GOW = {"GOW50", "GOW30"}
ETW = "ETW30"
RULE_ID = "H-STR-01"


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
        # step 3: GOW50 island between GOW30 runs, or at the end next to GOW30
        runs = _runs(stroke, lambda s: cur[s])
        for i, (k, sids) in enumerate(runs):
            if k != "GOW50" or length(sids) >= min_run or not free(sids):
                continue
            left = runs[i - 1][0] if i > 0 else None
            right = runs[i + 1][0] if i < len(runs) - 1 else None
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
