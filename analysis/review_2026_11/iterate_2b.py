"""Phase 2b: coordinated iteration street network <-> cycle network (dry run in a worktree, nothing in production).

Round 1  street rule from 2a (C-GOW-01 also for bus_trips_weekday >= BUS_GOW, assumption) -> rerun from classify
Round k  feedback of the cross section into the street category: every D5 proposal (GOW50 does not fit ->
         GOW30, C-G30-02, design_rules PRF-06) becomes a category override in the worktree (review_status approved,
         author review-2026-11-dryrun) -> rerun from coherence (overrides are applied in s06b)
Stop     no new D5 proposals, or MAX_ROUNDS reached. D6/D7 stay flags: moving a route or cutting through traffic
         is a design decision (listed as remaining trade-offs).
After each round: conflicts_2b.count on the worktree's data/interim.

Usage: python -m analysis.review_2026_11.iterate_2b [--bus-gow 100] [--max-rounds 3]
"""

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

from analysis.review_2026_11.conflicts_2b import count
from analysis.review_2026_11.variants_2a import bus_rule

ROOT = Path(__file__).resolve().parents[2]
NAME = "iter_2b"
WT = ROOT.parent / f"SFP_wt_{NAME}"
OUT = ROOT / "data/scenarios" / NAME


CHAIN_AFTER_OVERRIDES = ["coherence", "discrepancy", "cycle-demand", "cycle-network", "cycle-principles",
                         "cycle-facility", "cross-section-soll", "junctions"]


def run(from_stage: str, seed: bool) -> None:
    """Round 1: make rerun via run_worktree.sh. Later rounds: only the stages the conflicts need, without validate
    and export (validate's base check flags 6 segments after category overrides, see 02b_konflikte.md)."""
    if from_stage == "classify":
        env = dict(os.environ, SEED_INTERIM="1" if seed else "0", WARM_CACHE="1" if seed else "0")
        subprocess.run([str(ROOT / "analysis/review_2026_11/run_worktree.sh"), NAME, from_stage, "HEAD"], env=env,
                       check=True)
        log = (OUT / "run.log").read_text(encoding="utf-8")
        if "Error" in log or "check(s) failed" in log:
            raise RuntimeError(f"worktree run failed, see {OUT / 'run.log'}")
        return
    env = dict(os.environ, UV_NO_SYNC="1")
    with open(OUT / f"run_{from_stage}.log", "a", encoding="utf-8") as fh:
        subprocess.run(["make", "--no-print-directory", *CHAIN_AFTER_OVERRIDES], cwd=WT, env=env, check=True,
                       stdout=fh, stderr=subprocess.STDOUT)


def d5_proposals(interim: Path) -> pd.DataFrame:
    x = pd.read_parquet(interim / "cross_section_soll.parquet",
                        columns=["segment_id", "cat_final", "cat_change_proposal", "length_m", "name"])
    return x[x.cat_change_proposal.notna() & (x.cat_change_proposal != x.cat_final)]


def write_overrides(rows: pd.DataFrame, rnd: int) -> None:
    path = WT / "overrides/overrides.csv"
    cur = pd.read_csv(path)
    new = pd.DataFrame({
        "segment_id": rows.segment_id, "cat_final": rows.cat_change_proposal,
        "reason": f"Review 2026-11 Trockenlauf Runde {rnd}: Querschnitt passt als GOW50 nicht (D5, C-G30-02)",
        "author": "review-2026-11-dryrun", "date": dt.date.today().isoformat(),
        "source": "analysis/review_2026_11/iterate_2b.py", "review_status": "approved"})
    new = new[~new.segment_id.isin(cur.segment_id)]
    pd.concat([cur, new], ignore_index=True).to_csv(path, index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bus-gow", type=int, default=100)
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--resume", action="store_true",
                    help="worktree already holds round 1 and the round-2 overrides with a finished cycling chain")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rounds = [{"round": 0, "state": "A (heute)", "conflicts": count(ROOT / "data/interim")}]
    # round 1: street rule
    if not WT.exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(WT), "HEAD"], check=True)
    interim = WT / "data/interim"
    applied = set()
    start = 2
    if a.resume:
        r1 = json.loads((OUT / "round1.json").read_text(encoding="utf-8"))
        rounds.append(r1)
        ov = pd.read_csv(WT / "overrides/overrides.csv")
        applied = set(ov.segment_id[ov.author == "review-2026-11-dryrun"])
        prop = d5_proposals(interim)
        rounds.append({"round": 2, "state": f"D5 übernommen ({len(applied)} Abschnitte)", "conflicts": count(interim),
                       "d5_new": int((~prop.segment_id.isin(applied)).sum()),
                       "d5_km": round(prop[~prop.segment_id.isin(applied)].length_m.sum() / 1000, 1)})
        print(json.dumps(rounds[-1], ensure_ascii=False), flush=True)
        start = 3
    else:
        rules = WT / "config/rules.yaml"
        rules.write_text(bus_rule(a.bus_gow)(rules.read_text(encoding="utf-8")), encoding="utf-8")
        run("classify", seed=True)
        prop = d5_proposals(interim)
        rounds.append({"round": 1, "state": f"Busregel {a.bus_gow}", "conflicts": count(interim),
                       "d5_new": len(prop), "d5_km": round(prop.length_m.sum() / 1000, 1)})
        (OUT / "round1.json").write_text(json.dumps(rounds[-1], ensure_ascii=False), encoding="utf-8")
        print(json.dumps(rounds[-1], ensure_ascii=False), flush=True)
    for rnd in range(start, a.max_rounds + 1):
        new = prop[~prop.segment_id.isin(applied)]
        if new.empty:
            rounds.append({"round": rnd, "state": "Abbruch: keine neuen D5-Vorschläge"})
            break
        write_overrides(new, rnd - 1)
        applied |= set(new.segment_id)
        run("coherence", seed=False)
        prop = d5_proposals(interim)
        rounds.append({"round": rnd, "state": f"D5 übernommen ({len(new)} Abschnitte)", "conflicts": count(interim),
                       "d5_new": int((~prop.segment_id.isin(applied)).sum()),
                       "d5_km": round(prop[~prop.segment_id.isin(applied)].length_m.sum() / 1000, 1)})
        print(json.dumps(rounds[-1], ensure_ascii=False), flush=True)
    # remaining trade-offs: D7 on RSV/HAUPT, K1, K2 after the last round
    x = pd.read_parquet(interim / "cross_section_soll.parquet",
                        columns=["segment_id", "name", "bezirk", "length_m", "cat_final", "cycle_cat_final",
                                 "fit_class", "degrade_steps_applied"])
    x["d7"] = x.degrade_steps_applied.fillna("").str.contains("D7")
    x[x.d7 | (x.fit_class == "does_not_fit")].to_parquet(OUT / "remaining.parquet")
    for f in ("final.parquet", "cross_section_soll.parquet", "cycle_facility.parquet", "junctions.parquet"):
        subprocess.run(["cp", str(interim / f), str(OUT / f)], check=True)
    (OUT / "rounds.json").write_text(json.dumps(rounds, ensure_ascii=False, indent=1, default=str))
    print("done", OUT)


if __name__ == "__main__":
    main()
