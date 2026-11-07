"""Scenario D (review 2026-11): simple car assignment on the Ist and the Soll network.

Deliberately simple prototype for prompt 22 (stage B); it does not replace it. Every parameter that is not in the
rule files is an assumption and listed in ASSUMPTIONS (source_type assumption).

Model
- Network: car segments of data/interim/final.parquet (cat_final, travel_speed_kmh), undirected (no oneway data,
  docs/open_questions.md: betweenness question). Segments without speed (service/track) are left out.
- Zones: 1 km grid; production = residents (Zensus 100 m), attraction = residents + non-residential floor area
  (ALKIS, same function as the cycle model, pipeline/lib/cycle_demand.jobs_floor_area). External zones at the end
  nodes of counted roads (DTV 2019) on the outer edge of the network; their weight = counted DTV.
- Distribution: gravity with exp(-beta * t) (t in minutes); beta from a grid, scale fitted on DTV 2019.
- Assignment: incremental (4 x 25 %) with BPR on daily capacity = lanes x lane capacity (L-02) / peak share
  (C-FAC-03). Shortest paths and loading via pipeline/lib/cycle_demand.assign_od.
- Soll: speed per cat_final (rules.yaml categories.*.speed_kmh; SW keeps travel_speed_kmh), lanes per direction
  from cross_section_soll, ETW30/ETW_ERF resistance factor (1.0 / 1.5 / 3.0 as a stand-in for filters), evaporation
  0/10/20 % of all trips.
- Result per segment: dtv_soll = dtv_official x model_soll / model_ist where counted (pivot), else model_soll.

Usage: python -m analysis.review_2026_11.scenario_d <out_dir> [--origins-sample N]
"""

import argparse
import itertools
import json
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr

from pipeline.lib import cycle_demand as cd

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data/interim"
RAW = ROOT / "data/raw"

ASSUMPTIONS = {
    "zone_m": {"value": 1000, "source_type": "assumption", "note": "Zonengröße; Kfz-Wege sind länger als Radwege"},
    "beta_per_min_grid": {"value": [0.04, 0.07, 0.10, 0.14], "source_type": "assumption",
                          "note": "Raumwiderstand exp(-beta t); Wahl nach Anpassung an DTV 2019"},
    "attraction_residents_weight": {"value": 1.0, "source_type": "assumption",
                                    "note": "Wohnen zieht Rückwege an; Gewicht gegenüber Geschossfläche (normiert)"},
    "bpr_alpha_beta": {"value": [0.15, 4], "source_type": "assumption", "source": "Bureau of Public Roads 1964"},
    "increments": {"value": [0.25, 0.25, 0.25, 0.25], "source_type": "assumption"},
    "etw_factor": {"value": [1.0, 1.5, 3.0], "source_type": "assumption",
                   "note": "Widerstand auf ETW30/ETW_ERF: 1,0 nur Tempo; 1,5 Gestaltung nach DV; 3,0 Näherung für "
                           "modale Filter (kein echter Filter, Durchfahrt bleibt möglich)"},
    "evaporation": {"value": [0.0, 0.10, 0.20], "source_type": "assumption",
                    "source": "Cairns, Atkins, Goodwin (2002), Disappearing traffic? – als Quelle zu prüfen"},
    "external_edge_m": {"value": 300, "source_type": "assumption",
                        "note": "Endknoten gezählter Straßen höchstens so weit vom Netzrand: externe Zone"},
    "min_lanes": {"value": 1, "source_type": "assumption"},
    "ext_search_m": {"value": 3000, "source_type": "assumption",
                     "note": "nächste Zählstelle zu einem Netzende im Randbereich; weiter weg: keine externe Zone"},
    "peak_direction_share": {"value": 0.55, "source_type": "assumption",
                             "note": "Lastrichtung; steht nur in der Notiz zu C-FAC-03/L-02 (0,10 x 0,55)"},
}


def rules():
    r = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    d = yaml.safe_load((ROOT / "config/design_rules.yaml").read_text(encoding="utf-8"))
    c = yaml.safe_load((ROOT / "config/cycling_rules.yaml").read_text(encoding="utf-8"))
    speed = {k: v.get("speed_kmh") for k, v in r["categories"].items()}
    l02 = next(x for x in d["lanes"]["rules"] if x["id"] == "L-02")
    lane_cap = float(l02["lane_capacity_veh_h"]["value"])
    peak = next(x for x in _walk(c) if isinstance(x, dict) and x.get("id") == "C-FAC-03")
    peak_share = float(_find_value(peak, "peak_hour_share"))
    gow30_wide = float(r["requirements"]["GOW30"]["profiles"]["wide"]["max_dtv"])
    gow30_narrow = float(r["requirements"]["GOW30"]["profiles"]["narrow"]["max_dtv"])
    street_max = float(c["cycle_street"]["max_motor_vehicles_day"]["value"])
    return dict(speed=speed, lane_cap=lane_cap, peak_share=peak_share, gow30_wide=gow30_wide,
                gow30_narrow=gow30_narrow, cycle_street_max=street_max)


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _find_value(d: dict, key_part: str):
    for k, v in d.items():
        if key_part in k:
            return v["value"] if isinstance(v, dict) else v
    raise KeyError(key_part)


def load_network(r) -> pd.DataFrame:
    seg = gpd.read_parquet(INTERIM / "final.parquet",
                           columns=["segment_id", "node_u", "node_v", "length_m", "highway", "cat_final", "bezirk",
                                    "travel_speed_kmh", "dtv_official", "in_hvs", "name", "geometry"])
    xs = pd.read_parquet(INTERIM / "cross_section_soll.parquet",
                         columns=["segment_id", "lanes_per_dir_ist", "lanes_per_dir_soll"])
    seg = seg.merge(xs, on="segment_id", how="left")
    seg = seg[seg.travel_speed_kmh.notna() & (seg.travel_speed_kmh > 0)].reset_index(drop=True)
    soll_speed = seg.cat_final.map(r["speed"]).astype("float64")
    seg["speed_soll"] = soll_speed.fillna(seg.travel_speed_kmh)  # SW and uncategorised (buffer ring): Ist speed
    lanes_min = ASSUMPTIONS["min_lanes"]["value"]
    seg["lanes_ist"] = seg.lanes_per_dir_ist.fillna(lanes_min).clip(lower=lanes_min)
    # Soll lanes are text: "shared" (mixed traffic, one lane per direction for capacity) or "1"/"2"
    soll = pd.to_numeric(seg.lanes_per_dir_soll.replace({"shared": "1"}), errors="coerce")
    seg["lanes_soll"] = soll.fillna(seg.lanes_ist).clip(lower=lanes_min)
    return seg


def build_zones(seg: gpd.GeoDataFrame, zone_m: float) -> tuple[pd.DataFrame, np.ndarray]:
    """Zones with production/attraction and the network node each zone is attached to."""
    pop = gpd.read_parquet(RAW / "population_grid__100m.parquet")
    pop = pd.DataFrame({"x": pop.geometry.centroid.x, "y": pop.geometry.centroid.y,
                        "population": pop["population"].to_numpy(dtype="float64"), "floor": 0.0})
    b = gpd.read_parquet(RAW / "alkis__GebaeudeBauwerk.parquet", columns=["gebnutzbez", "funktion", "anzahlgs", "rellage",
                                                                            "geometry"])
    params = _demand_params()
    fl = cd.jobs_floor_area(b, params)
    pts = b.geometry.representative_point()
    jobs = pd.DataFrame({"x": pts.x, "y": pts.y, "population": 0.0, "floor": fl.to_numpy()})
    jobs = jobs[jobs.floor > 0]
    del b
    p = pd.concat([pop, jobs], ignore_index=True)
    p["zone"] = (np.floor(p.x / zone_m).astype(int).astype(str) + "_" + np.floor(p.y / zone_m).astype(int).astype(str))
    z = p.groupby("zone").agg(population=("population", "sum"), floor=("floor", "sum"),
                              x=("x", "mean"), y=("y", "mean"))
    z = z[(z.population > 0) | (z.floor > 0)].copy()
    w = ASSUMPTIONS["attraction_residents_weight"]["value"]
    z["attraction"] = w * z.population / z.population.sum() + z.floor / z.floor.sum()
    z["production"] = z.population / z.population.sum()
    z["external"] = False
    return z.reset_index()


def _demand_params():
    """Cycle demand parameters (only the jobs_floor_area settings are used)."""
    from pipeline.lib.rules import load_cycling_rules
    return cd.DemandParams.from_rules(load_cycling_rules())


def node_index(seg: pd.DataFrame):
    nodes = pd.Index(pd.unique(np.concatenate([seg.node_u.to_numpy(), seg.node_v.to_numpy()])))
    return nodes, nodes.get_indexer(seg.node_u), nodes.get_indexer(seg.node_v)


def node_xy(seg: gpd.GeoDataFrame, nodes: pd.Index, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    xy = np.full((len(nodes), 2), np.nan)
    g = seg.geometry
    start = np.array([c.coords[0] for c in g])
    end = np.array([c.coords[-1] for c in g])
    xy[u] = start
    xy[v] = end
    return xy


def attach(z: pd.DataFrame, xy: np.ndarray, allowed: np.ndarray) -> np.ndarray:
    from scipy.spatial import cKDTree
    idx = np.flatnonzero(allowed)
    tree = cKDTree(xy[idx])
    _, k = tree.query(z[["x", "y"]].to_numpy())
    return idx[k]


def external_zones(seg: gpd.GeoDataFrame, xy: np.ndarray, u: np.ndarray, v: np.ndarray, edge_m: float) -> pd.DataFrame:
    """Dead ends (degree 1) of main roads near the outer edge of the network (the clipped buffer ring).

    Weight = DTV of the nearest counted segment (DTV 2019 only exists inside Hamburg), searched within
    EXT_SEARCH_M; dead ends without a count nearby are dropped.
    """
    from scipy.spatial import cKDTree
    from shapely.geometry import Point
    deg = np.bincount(np.concatenate([u, v]), minlength=len(xy))
    hull = seg.geometry.union_all().convex_hull.exterior
    main = seg.highway.isin(["motorway", "trunk", "primary", "secondary", "tertiary"]).to_numpy()
    ends = sorted({n for i in np.flatnonzero(main) for n in (u[i], v[i]) if deg[n] == 1})
    ends = [n for n in ends if hull.distance(Point(xy[n])) <= edge_m]
    counted = seg[seg.dtv_official.notna()]
    mids = np.array([g.interpolate(0.5, normalized=True).coords[0] for g in counted.geometry])
    tree = cKDTree(mids)
    dist, k = tree.query(xy[ends]) if ends else (np.array([]), np.array([], dtype=int))
    rows = [{"zone": f"ext_{n}", "node": n, "x": xy[n][0], "y": xy[n][1],
             "dtv": float(counted.dtv_official.iat[j]), "name": counted["name"].iat[j], "dist_m": float(d)}
            for n, d, j in zip(ends, dist, k) if d <= ASSUMPTIONS["ext_search_m"]["value"]]
    return pd.DataFrame(rows, columns=["zone", "node", "x", "y", "dtv", "name", "dist_m"])


def run_assignment(n_nodes, tail, head, t0_min, cap_day, zones, zone_node, beta, scale, increments,
                   evaporation=0.0, sample=None, seed=42):
    """Incremental assignment; returns daily flow per segment (both directions) and the final travel times."""
    alpha, power = ASSUMPTIONS["bpr_alpha_beta"]["value"]
    prod = zones["production"].to_numpy() * (1 - evaporation)
    attr = zones["attraction"].to_numpy()
    origins = np.arange(len(zones))
    weight = 1.0
    if sample and sample < len(origins):
        rng = np.random.default_rng(seed)
        origins = np.sort(rng.choice(origins, size=sample, replace=False))
        weight = len(zones) / sample
    dest_nodes = zone_node
    flow = np.zeros(len(tail))
    t = t0_min.copy()
    for share in increments:
        cost = np.concatenate([t, t]) * 60.0  # seconds, both directions
        tl = np.concatenate([tail, head])
        hd = np.concatenate([head, tail])

        def od(i, d_sec, _o=origins):
            o = _o[i]
            w = np.where(np.isfinite(d_sec), attr * np.exp(-beta * d_sec / 60.0), 0.0)
            w[o] = 0.0  # no intrazonal trips on the network
            tot = w.sum()
            k = scale[o] if np.ndim(scale) else scale
            return k * share * weight * prod[o] * w / tot if tot > 0 else np.zeros_like(w)

        f = cd.assign_od(n_nodes, tl, hd, cost, zone_node[origins].tolist(), dest_nodes, od)
        flow += f[:len(tail)] + f[len(tail):]
        t = t0_min * (1 + alpha * (flow / cap_day) ** power)
    return flow, t


def fit(seg, flow) -> dict:
    m = seg.dtv_official.notna().to_numpy() & (flow > 0)
    obs, mod = seg.dtv_official.to_numpy()[m], flow[m]
    s = float(spearmanr(obs, mod).statistic)
    ratio = mod / obs
    geh = np.sqrt(2 * (mod - obs) ** 2 / (mod + obs))
    return {"n": int(m.sum()), "spearman": round(s, 3), "within_factor_2": round(float(((ratio > 0.5) & (ratio < 2)).mean()), 3),
            "geh_lt_10": round(float((geh < 10).mean()), 3), "median_ratio": round(float(np.median(ratio)), 3)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--origins-sample", type=int, default=None)
    ap.add_argument("--beta", type=float, default=None, help="skip the beta grid")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    r = rules()
    seg = load_network(r)
    nodes, u, v = node_index(seg)
    xy = node_xy(seg, nodes, u, v)
    z = build_zones(seg, ASSUMPTIONS["zone_m"]["value"])
    ext = external_zones(seg, xy, u, v, ASSUMPTIONS["external_edge_m"]["value"])
    # internal zones attach to the nearest node of a non-motorway road
    allowed = np.zeros(len(nodes), dtype=bool)
    ok = ~seg.highway.isin(["motorway", "motorway_link", "trunk_link"]).to_numpy()
    allowed[u[ok]] = True
    allowed[v[ok]] = True
    zone_node = attach(z, xy, allowed)
    # external zones: production/attraction share by counted DTV, total scaled with the internal total below
    ext_share = ext.dtv.to_numpy() / ext.dtv.sum()
    zones = pd.concat([z.assign(node=zone_node), pd.DataFrame({
        "zone": ext.zone, "x": ext.x, "y": ext.y, "population": 0.0, "floor": 0.0, "node": ext.node,
        "production": ext_share, "attraction": ext_share * 0.5, "external": True})], ignore_index=True)
    zone_node = zones.node.to_numpy(dtype="int64")
    # daily two-way capacity: lanes per direction x lane capacity in the peak direction / (peak share x direction share)
    k = r["lane_cap"] / (r["peak_share"] * ASSUMPTIONS["peak_direction_share"]["value"])
    cap_ist = seg.lanes_ist.to_numpy() * k
    cap_soll = seg.lanes_soll.to_numpy() * k
    t_ist = seg.length_m.to_numpy() / (seg.travel_speed_kmh.to_numpy() / 3.6) / 60.0
    etw = seg.cat_final.isin(["ETW30", "ETW_ERF"]).to_numpy()
    t_soll_base = seg.length_m.to_numpy() / (seg.speed_soll.to_numpy() / 3.6) / 60.0
    inc = ASSUMPTIONS["increments"]["value"]
    counted = seg.dtv_official.notna().to_numpy()

    # calibration: external zones carry their counted DTV; internal production scaled to fit HVS counts
    calib = []
    betas = [a.beta] if a.beta else ASSUMPTIONS["beta_per_min_grid"]["value"]
    best = None
    for beta in betas:
        # uncongested first pass, internal and external origins separately; two scales by non-negative LS
        ext_mask = zones.external.to_numpy()
        f_int, _ = run_assignment(len(nodes), u, v, t_ist, cap_ist, zones.assign(production=np.where(ext_mask, 0, zones.production)),
                                  zone_node, beta, 1.0, [1.0], sample=a.origins_sample)
        f_ext, _ = run_assignment(len(nodes), u, v, t_ist, cap_ist, zones.assign(production=np.where(ext_mask, zones.production, 0)),
                                  zone_node, beta, 1.0, [1.0], sample=a.origins_sample)
        from scipy.optimize import nnls
        (s_int, s_ext), _ = nnls(np.column_stack([f_int[counted], f_ext[counted]]), seg.dtv_official.to_numpy()[counted])
        scale = np.where(ext_mask, s_ext, s_int)
        f, t_fin = run_assignment(len(nodes), u, v, t_ist, cap_ist, zones, zone_node, beta, scale, inc,
                                  sample=a.origins_sample)
        st = fit(seg, f) | {"beta": beta, "scale_internal": round(float(s_int), 1), "scale_external": round(float(s_ext), 1)}
        calib.append(st)
        print("calibration", st, f"{time.time() - t_start:.0f}s", flush=True)
        if best is None or st["spearman"] > best[0]["spearman"]:
            best = (st, f, beta, scale)
    st, f_ist, beta, scale = best
    res = seg[["segment_id", "name", "bezirk", "highway", "cat_final", "length_m", "dtv_official", "in_hvs"]].copy()
    res["model_ist"] = f_ist
    runs = []
    for fac, evap in itertools.product(ASSUMPTIONS["etw_factor"]["value"], ASSUMPTIONS["evaporation"]["value"]):
        t_soll = np.where(etw, t_soll_base * fac, t_soll_base)
        f_soll, _ = run_assignment(len(nodes), u, v, t_soll, cap_soll, zones, zone_node, beta, scale, inc,
                                   evaporation=evap, sample=a.origins_sample)
        key = f"etw{fac:g}_evap{int(evap * 100)}"
        ratio = np.where(f_ist > 0, f_soll / np.maximum(f_ist, 1e-9), np.nan)
        res[f"model_{key}"] = f_soll
        res[f"dtv_{key}"] = np.where(counted, seg.dtv_official.to_numpy() * ratio, f_soll)
        runs.append(key)
        print("soll run", key, f"{time.time() - t_start:.0f}s", flush=True)
    res.to_parquet(out / "scenario_d_segments.parquet")
    meta = {"assumptions": ASSUMPTIONS, "rules_used": r, "calibration": calib, "chosen": st, "runs": runs,
            "n_zones_internal": int((~zones.external).sum()), "n_zones_external": int(zones.external.sum()),
            "n_segments": len(seg), "origins_sample": a.origins_sample, "runtime_s": round(time.time() - t_start)}
    (out / "scenario_d_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(meta["chosen"]), meta["runtime_s"], "s")


if __name__ == "__main__":
    main()
