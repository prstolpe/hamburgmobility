"""Rule inventory: rule IDs in the three rule files against pipeline code, tests and golden cases;
number literals in pipeline code that might be thresholds outside the rule files.

Usage: python -m analysis.review_2026_11.rule_inventory <out_dir>
Writes rules.csv (one row per rule id) and literals.csv (one row per suspicious literal).
"""

import ast
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
RULE_FILES = ["config/rules.yaml", "config/cycling_rules.yaml", "config/design_rules.yaml"]
# Literals that are structural, not thresholds
HARMLESS = {0, 1, 2, -1, 0.0, 1.0, 0.5, 2.0, 3, 10, 100, 1000, 1e-9, 1e-6, 3.6, 24, 60, 3600, 25832, 4326}


def walk_ids(node, path, out, inherited):
    """Collect every mapping that carries an `id`; source/source_type are inherited from parents."""
    if isinstance(node, dict):
        inh = dict(inherited)
        for k in ("source", "source_type"):
            if k in node:
                inh[k] = node[k]
        if "id" in node and isinstance(node["id"], str):
            out.append({"id": node["id"], "path": path, "status": node.get("status"),
                        "source": inh.get("source"), "source_type": inh.get("source_type")})
        for k, v in node.items():
            walk_ids(v, f"{path}.{k}", out, inh)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_ids(v, f"{path}[{i}]", out, inherited)


def texts(globs):
    return {p: p.read_text(encoding="utf-8") for g in globs for p in ROOT.glob(g)}


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rules = []
    for f in RULE_FILES:
        found = []
        walk_ids(yaml.safe_load((ROOT / f).read_text(encoding="utf-8")), "", found, {})
        for r in found:
            r["file"] = f
        rules += found
    code = texts(["pipeline/*.py", "pipeline/lib/*.py"])
    tests = texts(["tests/*.py"])
    golden = texts(["tests/golden/**/*.geojson", "tests/golden/**/*.json", "tests/golden/**/*.yaml",
                    "tests/golden/**/*.csv"])
    for r in rules:
        pat = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(r['id'])}(?![A-Za-z0-9])")
        r["code_files"] = sorted({p.name for p, t in code.items() if pat.search(t)})
        r["test_files"] = sorted({p.name for p, t in tests.items() if pat.search(t)})
        r["golden_files"] = len({p for p, t in golden.items() if pat.search(t)})
    df = pd.DataFrame(rules)
    df["in_code"] = df.code_files.str.len() > 0
    df["in_tests"] = (df.test_files.str.len() > 0) | (df.golden_files > 0)
    df.to_csv(out / "rules.csv", index=False)

    lits = []
    for p, t in code.items():
        for node in ast.walk(ast.parse(t)):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                    and not isinstance(node.value, bool) and node.value not in HARMLESS:
                line = t.splitlines()[node.lineno - 1].strip()
                lits.append({"file": p.name, "line": node.lineno, "value": node.value, "code": line[:140]})
    pd.DataFrame(lits).to_csv(out / "literals.csv", index=False)

    print(df.groupby("file").agg(rules=("id", "size"), no_status=("status", lambda s: s.isna().sum()),
                                 no_source_type=("source_type", lambda s: s.isna().sum()),
                                 not_in_code=("in_code", lambda s: (~s).sum()),
                                 not_in_tests=("in_tests", lambda s: (~s).sum())))
    print(f"{len(lits)} number literals outside the harmless set")


if __name__ == "__main__":
    main(sys.argv[1])
