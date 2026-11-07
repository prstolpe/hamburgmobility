"""Compare two pipeline runs (data/interim of two worktrees) row by row.

Usage: python -m analysis.review_2026_11.compare_runs <dir_a> <dir_b> <out_csv>

For every parquet file present in both directories: row count, key set, and per column the number of rows
that differ (floats with relative tolerance 1e-9, geometries by WKB). Writes one CSV row per (file, column)
with differences and prints a summary. Key column = first of segment_id, edge_id, node_id, route_id found.
"""

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

KEYS = ["segment_id", "edge_id", "node_id", "route_id", "zone_id"]
FLOAT_RTOL = 1e-9


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def normalise(s: pd.Series) -> pd.Series:
    """Comparable representation: WKB hex for geometry, repr for nested values."""
    if s.dtype == object:
        return s.map(lambda v: v.hex() if isinstance(v, bytes) else repr(v.tolist() if hasattr(v, "tolist") else v))
    return s


def compare_file(a: Path, b: Path) -> tuple[dict, list[dict]]:
    ta, tb = pq.read_table(a), pq.read_table(b)
    da, db = ta.to_pandas(), tb.to_pandas()
    key = next((k for k in KEYS if k in da.columns), None)
    info = {"file": a.name, "rows_a": len(da), "rows_b": len(db), "key": key,
            "hash_equal": file_hash(a) == file_hash(b),
            "cols_only_a": sorted(set(da.columns) - set(db.columns)),
            "cols_only_b": sorted(set(db.columns) - set(da.columns))}
    rows = []
    if key is None or da[key].duplicated().any() or db[key].duplicated().any():
        # no unique key: compare in stored order
        info["order_compare"] = True
        n = min(len(da), len(db))
        da, db = da.iloc[:n].reset_index(drop=True), db.iloc[:n].reset_index(drop=True)
    else:
        ka, kb = set(da[key]), set(db[key])
        info["keys_only_a"], info["keys_only_b"] = len(ka - kb), len(kb - ka)
        common = sorted(ka & kb)
        info["order_equal"] = list(da[key]) == list(db[key])
        da = da.set_index(key).loc[common].reset_index()
        db = db.set_index(key).loc[common].reset_index()
    for col in sorted(set(da.columns) & set(db.columns)):
        x, y = da[col], db[col]
        if pd.api.types.is_float_dtype(x) and pd.api.types.is_float_dtype(y):
            xv, yv = x.to_numpy(), y.to_numpy()
            both_nan = np.isnan(xv) & np.isnan(yv)
            close = np.isclose(xv, yv, rtol=FLOAT_RTOL, atol=0) | both_nan
            exact = (xv == yv) | both_nan
            n_diff, n_float_only = int((~close).sum()), int((close & ~exact).sum())
            mask = ~exact
            max_abs = float(np.nanmax(np.abs(xv - yv))) if (~exact).any() else 0.0
        else:
            nx, ny = normalise(x), normalise(y)
            neq = ~((nx == ny) | (nx.isna() & ny.isna()))
            n_diff, n_float_only, max_abs = int(neq.sum()), 0, None
            mask = neq.to_numpy()
        if n_diff or n_float_only:
            example = da.loc[mask, da.columns[0]].head(3).tolist()
            rows.append({"file": a.name, "column": col, "rows_differ": n_diff, "float_noise_only": n_float_only,
                         "max_abs_diff": max_abs, "examples": example})
    return info, rows


def main(dir_a: str, dir_b: str, out_csv: str) -> None:
    a, b = Path(dir_a), Path(dir_b)
    infos, rows = [], []
    for fa in sorted(a.glob("*.parquet")):
        fb = b / fa.name
        if not fb.exists():
            infos.append({"file": fa.name, "missing_in_b": True})
            continue
        info, r = compare_file(fa, fb)
        infos.append(info)
        rows += r
    pd.DataFrame(infos).to_csv(Path(out_csv).with_suffix(".files.csv"), index=False)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    for i in infos:
        print(i)
    print(f"{len(rows)} differing (file, column) pairs -> {out_csv}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
