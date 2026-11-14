"""Patches for the rule-consolidation dry runs (prompt 24, A6). Only candidates that can be switched in the rule files
alone get a patch; candidates that only rename or move text (K1, K2, K4–K7, K9) cannot change an output by construction
and are shown with data evidence in docs/redesign/06_rule_consolidation.md.

- K3  J-02 into J-01: legs 'GOW50+GOW50|GOW30' on J-01, row J-02 and its place in evaluation_order removed
- K8  J-11 removed (no tram in Hamburg): row and evaluation_order entry removed
- K10 C-NET-11 off: max_gap_m 0 (no run is short enough to be raised)
- K11 C-NET-10 as a flag only: min_run_m 1e9 (no run is long enough to be moved to a parallel route)
- ALL K3 + K8 + K10 + K11

Usage: uv run python -m analysis.redesign.make_consolidation_patches
Writes data/scenarios/redesign/<K>/<K>.patch.
"""

import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/scenarios/redesign"
DESIGN = "config/design_rules.yaml"
CYCLING = "config/cycling_rules.yaml"


def k3(files):
    t = files[DESIGN]
    t = t.replace("- {id: J-01, legs: 'GOW50+GOW50',", "- {id: J-01, legs: 'GOW50+GOW50|GOW30',", 1)
    t = t.replace("      - {id: J-02, legs: 'GOW50+GOW30', same_as: J-01, status: draft}\n", "", 1)
    t = t.replace("J-14, J-01, J-02, J-03,", "J-14, J-01, J-03,", 1)
    files[DESIGN] = t


def k8(files):
    t = files[DESIGN]
    t = t.replace("      - {id: J-11, legs: 'any with tram', then: signal_protected, status: draft}\n", "", 1)
    t = t.replace("J-10b, J-11, J-09,", "J-10b, J-09,", 1)
    files[DESIGN] = t


def k10(files):
    t = files[CYCLING]
    t = t.replace("      max_gap_m: 200\n", "      max_gap_m: 0\n", 1)
    files[CYCLING] = t


def k11(files):
    t = files[CYCLING]
    t = t.replace("      min_run_m: 300\n      max_on_main_m: 60\n", "      min_run_m: 1000000000\n      max_on_main_m: 60\n", 1)
    files[CYCLING] = t


PATCHES = {"K3": [k3], "K8": [k8], "K10": [k10], "K11": [k11], "ALL": [k3, k8, k10, k11]}


def main():
    orig = {f: (ROOT / f).read_text(encoding="utf-8") for f in (DESIGN, CYCLING)}
    for name, fns in PATCHES.items():
        files = dict(orig)
        for fn in fns:
            fn(files)
        changed = [f for f in files if files[f] != orig[f]]
        assert changed, f"{name}: nothing changed"
        for f in changed:
            yaml.safe_load(files[f])  # still valid YAML
        with tempfile.TemporaryDirectory() as tmp:
            for base, content in (("a", orig), ("b", files)):
                for f, t in content.items():
                    p = Path(tmp) / base / f
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(t, encoding="utf-8")
            diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=tmp, capture_output=True, text=True).stdout
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.patch").write_text(diff, encoding="utf-8")
        print(name, changed, diff.count("\n"), "lines")
    # each patch must apply to the current tree
    for name in PATCHES:
        r = subprocess.run(["git", "apply", "--check", str(OUT / name / f"{name}.patch")], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, f"{name}: {r.stderr}"
    print("all patches apply")


if __name__ == "__main__":
    main()
