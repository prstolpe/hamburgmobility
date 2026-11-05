"""Directed cycle graph (prompts/15): way selection, one-way rules, Ist impedance and node delays.

Rules C-GRAPH-01..06 and C-IMP-01..08 in config/cycling_rules.yaml. Every value comes in through
GraphParams; the condition names of routing_impedance.ist_mapping are evaluated here
(config/schema/cycling_model.py IMPEDANCE_CONDITIONS). Resistance is in metres:
length x factor + delay seconds x cycling speed. Geometries in EPSG:25832.
"""

import json
import math
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd

from config.schema.cycling_model import DELAY_KEYS, CyclingRuleSet
from pipeline.lib.network import segment_id, segments_from_edges

EDGE_ID_PREFIX = "ce_"
TRACK_VALUES = {"track", "opposite_track"}  # cycleway=separate is its own OSM way, so not a track here
LANE_VALUES = {"lane", "opposite_lane"}
YES = {"yes", "true", "1"}


@dataclass(frozen=True)
class GraphParams:
    exclude_highways: frozenset
    exclude_motorroad: bool
    bicycle_forbidden: frozenset
    path_highways: frozenset
    bicycle_allowed: frozenset
    ferry_bicycle_allowed: frozenset
    ferry_wait_s: float
    ferry_snap_m: float
    priority_categories: frozenset
    priority_highways: frozenset
    sidepath_buffer_m: float
    sidepath_max_angle_deg: float
    sidepath_min_overlap: float
    cycling_speed_kmh: float
    signal_delay_s: float
    give_way_delay_s: float
    factors: dict
    imp_rules: tuple  # (id, when, factor key, is_multiplier)
    low_speed_max_kmh: float
    access_categories: frozenset
    access_highways: frozenset
    unpaved_surfaces: frozenset

    @classmethod
    def from_rules(cls, cyc: CyclingRuleSet) -> "GraphParams":
        g = {r["id"]: r for r in cyc.cycle_graph["rules"]}
        imp = cyc.routing_impedance
        m = imp["ist_mapping"]
        factors = {k: float(v) for k, v in imp["factors"].items() if k not in DELAY_KEYS}
        return cls(
            exclude_highways=frozenset(g["C-GRAPH-01"]["exclude_highways"]),
            exclude_motorroad=bool(g["C-GRAPH-01"]["exclude_motorroad"]),
            bicycle_forbidden=frozenset(g["C-GRAPH-01"]["bicycle_forbidden"]),
            path_highways=frozenset(g["C-GRAPH-01"]["path_highways"]),
            bicycle_allowed=frozenset(g["C-GRAPH-01"]["bicycle_allowed"]),
            ferry_bicycle_allowed=frozenset(g["C-GRAPH-03"]["ferry_bicycle_allowed"]),
            ferry_wait_s=float(g["C-GRAPH-03"]["ferry_wait_s"]),
            ferry_snap_m=float(g["C-GRAPH-03"]["ferry_snap_m"]),
            priority_categories=frozenset(g["C-GRAPH-05"]["priority_categories"]),
            priority_highways=frozenset(g["C-GRAPH-05"]["priority_highways_without_category"]),
            sidepath_buffer_m=float(g["C-GRAPH-06"]["buffer_m"]),
            sidepath_max_angle_deg=float(g["C-GRAPH-06"]["max_angle_deg"]),
            sidepath_min_overlap=float(g["C-GRAPH-06"]["min_overlap"]),
            cycling_speed_kmh=float(cyc.cycle_graph["cycling_speed_kmh"]),
            signal_delay_s=float(imp["factors"]["signal_delay_s"]),
            give_way_delay_s=float(imp["factors"]["give_way_delay_s"]),
            factors=factors,
            imp_rules=tuple((r["id"], r["when"], r.get("factor", r.get("multiply")), "multiply" in r) for r in m["rules"]),
            low_speed_max_kmh=float(m["low_speed_max_kmh"]),
            access_categories=frozenset(m["access_categories"]),
            access_highways=frozenset(m["access_highways"]),
            unpaved_surfaces=frozenset(m["unpaved_surfaces"]),
        )

    @property
    def m_per_s(self) -> float:
        return self.cycling_speed_kmh / 3.6


def _known(v) -> bool:
    if v is None or v is pd.NA:
        return False
    return not (isinstance(v, float) and math.isnan(v))


def _side_values(tags: dict, prefix: str) -> set[str]:
    keys = (prefix, f"{prefix}:both", f"{prefix}:left", f"{prefix}:right")
    return {tags[k] for k in keys if isinstance(tags.get(k), str)}


# --- C-GRAPH-01 / C-GRAPH-02 -------------------------------------------------------------------


def way_kind(highway: str, tags: dict, in_segments: bool, params: GraphParams) -> str | None:
    """'road' (a road segment usable by bike), 'path' (own cycle or shared path) or None (not in the graph)."""
    bike = tags.get("bicycle")
    if bike in params.bicycle_forbidden:
        return None
    if in_segments:
        if highway in params.exclude_highways:
            return None
        if params.exclude_motorroad and tags.get("motorroad") == "yes":
            return None
        if highway in params.path_highways and bike not in params.bicycle_allowed:
            return None
        return "road"
    if highway == "cycleway":
        return "path"
    if highway in params.path_highways and bike in params.bicycle_allowed:
        return "path"
    return None


def allowed_directions(tags: dict) -> tuple[bool, bool]:
    """(along digitisation, against digitisation) for cyclists; contraflow only with oneway:bicycle=no."""
    ob = tags.get("oneway:bicycle")
    if ob == "no":
        return True, True
    if ob in YES:
        return True, False
    if ob == "-1":
        return False, True
    ow = tags.get("oneway")
    if ow == "-1":
        return False, True
    if ow in YES or (tags.get("junction") in ("roundabout", "circular") and ow != "no"):
        return True, False
    return True, True


# --- C-IMP-01..08 -------------------------------------------------------------------------------


def is_priority(cat, highway: str, params: GraphParams) -> bool:
    """Main road for C-GRAPH-05: cat_final in priority_categories, without cat_final by highway class."""
    if _known(cat):
        return cat in params.priority_categories
    return highway in params.priority_highways


def impedance(kind: str, highway: str, tags: dict, cat, speed, fahrradstrasse: bool,
              params: GraphParams) -> tuple[float, str, dict]:
    """Ist factor, the rule that chose it and a trace (rule ids, factor keys, inputs)."""
    cat = cat if _known(cat) else None
    speed = float(speed) if _known(speed) else None
    low = speed is not None and speed <= params.low_speed_max_kmh
    cyc = _side_values(tags, "cycleway")
    surface = tags.get("surface") if isinstance(tags.get("surface"), str) else None
    access = cat in params.access_categories if cat is not None else highway in params.access_highways
    road = kind == "road"
    conditions = {
        "cycle_street": bool(fahrradstrasse) or tags.get("bicycle_road") == "yes" or tags.get("cyclestreet") == "yes",
        "own_path": kind == "path",
        "separated_track": road and bool(cyc & TRACK_VALUES),
        "low_speed_access_road": road and low and access,
        "low_speed_with_lane": road and low and bool(cyc & LANE_VALUES),
        "low_speed_mixed": road and low,
        "other": True,
        "unpaved_or_cobbles": surface in params.unpaved_surfaces,
    }
    factor, chosen, rules, keys = None, None, [], []
    for rule_id, when, key, multiply in params.imp_rules:
        if multiply or factor is not None or not conditions[when]:
            continue
        factor, chosen = params.factors[key], rule_id
        rules.append(rule_id)
        keys.append(key)
    for rule_id, when, key, multiply in params.imp_rules:
        if multiply and conditions[when]:
            factor *= params.factors[key]
            rules.append(rule_id)
            keys.append(key)
    trace = {"rules": rules, "factor_keys": keys, "factor": round(factor, 4),
             "inputs": {"kind": kind, "highway": highway, "cat_final": cat, "speed_kmh": speed,
                        "fahrradstrasse_official": bool(fahrradstrasse), "cycleway": sorted(cyc) or None,
                        "bicycle_road": tags.get("bicycle_road"), "surface": surface}}
    return factor, chosen, trace


# --- C-GRAPH-04 / C-GRAPH-05 --------------------------------------------------------------------


def node_delays(u: np.ndarray, v: np.ndarray, priority: np.ndarray, signal_nodes: set,
                params: GraphParams) -> tuple[np.ndarray, np.ndarray]:
    """Delay in metres for travelling an edge into its v end (at_v) and into its u end (at_u).

    Signal node: signal_delay_s. Otherwise give_way_delay_s if the edge is not a priority road and
    the node touches a priority road.
    """
    u, v, priority = np.asarray(u), np.asarray(v), np.asarray(priority, dtype=bool)
    priority_nodes = set(u[priority].tolist()) | set(v[priority].tolist())
    sig_m = params.signal_delay_s * params.m_per_s
    gw_m = params.give_way_delay_s * params.m_per_s

    def delay(nodes: np.ndarray) -> np.ndarray:
        is_sig = np.fromiter((n in signal_nodes for n in nodes.tolist()), bool, len(nodes))
        at_prio = np.fromiter((n in priority_nodes for n in nodes.tolist()), bool, len(nodes))
        return np.where(is_sig, sig_m, np.where(~priority & at_prio, gw_m, 0.0))

    return delay(v), delay(u)


# --- merging into cycle edges ------------------------------------------------------------------


DIFFER = ["segment_ref", "kind", "highway", "imp_rule"]


def merge_edges(edges: gpd.GeoDataFrame, carry: tuple[str, ...] = ()) -> gpd.GeoDataFrame:
    """Merge node-to-node edges into cycle edges (chains between junctions and attribute changes).

    edges: u, v, way_id, name, highway, kind, imp_rule, factor, fwd_ok, bwd_ok, segment_id, delay_v,
    delay_u (metres), geometry, plus `carry` columns taken from the longest member edge.
    Output: edge_id (stable hash, prefix ce_), segment_id, cost_fwd / cost_bwd from node_u to node_v
    and back (NaN = not allowed), factor (length-weighted), and the carried columns.
    """
    e = edges.reset_index(drop=True).rename(columns={"segment_id": "segment_ref"})
    e["_const"] = None
    merged = segments_from_edges(e, differ=DIFFER, split_attribute="_const", min_length_m=math.inf,
                                 split_rule_id="", prefix=EDGE_ID_PREFIX, return_members=True)
    lengths = e.geometry.length.to_numpy()
    factor = e["factor"].to_numpy(dtype="float64")
    fwd_ok, bwd_ok = e["fwd_ok"].to_numpy(bool), e["bwd_ok"].to_numpy(bool)
    d_v, d_u = e["delay_v"].to_numpy(dtype="float64"), e["delay_u"].to_numpy(dtype="float64")
    out: dict[str, list] = {"cost_fwd": [], "cost_bwd": [], "factor": [], **{c: [] for c in carry}}
    for rows, forward in zip(merged["member_rows"], merged["member_forward"]):
        rows, forward = np.asarray(rows), np.asarray(forward, dtype=bool)
        base = lengths[rows] * factor[rows]
        ok_f = np.where(forward, fwd_ok[rows], bwd_ok[rows]).all()
        ok_b = np.where(forward, bwd_ok[rows], fwd_ok[rows]).all()
        out["cost_fwd"].append(float((base + np.where(forward, d_v[rows], d_u[rows])).sum()) if ok_f else np.nan)
        out["cost_bwd"].append(float((base + np.where(forward, d_u[rows], d_v[rows])).sum()) if ok_b else np.nan)
        out["factor"].append(float(base.sum() / lengths[rows].sum()) if lengths[rows].sum() > 0 else float(factor[rows[0]]))
        longest = rows[int(np.argmax(lengths[rows]))]
        for c in carry:
            out[c].append(e.at[longest, c])
    for c, vals in out.items():
        merged[c] = vals
    merged = merged.rename(columns={"segment_id": "edge_id", "segment_ref": "segment_id"})
    merged["segment_id"] = merged["segment_id"].where(merged["segment_id"].notna(), None)
    return merged.drop(columns=["maxspeed_osm", "split_rule", "member_rows", "member_forward"])


# --- C-GRAPH-03 ferries ------------------------------------------------------------------------


def ferry_edges(ferries: gpd.GeoDataFrame, nodes: gpd.GeoDataFrame, params: GraphParams) -> gpd.GeoDataFrame:
    """One edge per ferry way with bicycle in ferry_bicycle_allowed; ends snapped to the nearest graph
    node within ferry_snap_m; cost = length + ferry_wait_s x cycling speed + both snap distances
    (pier access, often pontoons not tagged for bikes), both directions.

    nodes: column `node` (id) and point geometry. Ferries that cannot be snapped at both ends are dropped.
    """
    columns = ["edge_id", "osm_way_ids", "kind", "highway", "imp_rule", "node_u", "node_v", "length_m",
               "factor", "cost_fwd", "cost_bwd", "snap_m", "geometry"]
    f = ferries[ferries["bicycle"].isin(params.ferry_bicycle_allowed)].reset_index(drop=True)
    if f.empty:
        return gpd.GeoDataFrame(columns=columns, geometry="geometry", crs=ferries.crs)
    starts = gpd.GeoDataFrame(geometry=f.geometry.map(lambda g: g.interpolate(0)), crs=f.crs)
    ends = gpd.GeoDataFrame(geometry=f.geometry.map(lambda g: g.interpolate(1, normalized=True)), crs=f.crs)

    def snap(points):
        j = gpd.sjoin_nearest(points, nodes[["node", "geometry"]], max_distance=params.ferry_snap_m, how="left",
                              distance_col="_d")
        j = j[~j.index.duplicated()]
        return j["node"].reindex(points.index), j["_d"].reindex(points.index)

    (nu, du), (nv, dv) = snap(starts), snap(ends)
    wait_m = params.ferry_wait_s * params.m_per_s
    records = []
    for i, r in f.iterrows():
        if pd.isna(nu[i]) or pd.isna(nv[i]) or nu[i] == nv[i]:
            continue
        geom = r.geometry
        length = float(geom.length)
        coords = [geom.coords[0], geom.coords[-1]]
        records.append({"edge_id": segment_id([int(r["way_id"])], coords, prefix=EDGE_ID_PREFIX),
                        "osm_way_ids": [int(r["way_id"])], "kind": "ferry", "highway": "ferry", "imp_rule": "C-GRAPH-03",
                        "node_u": int(nu[i]), "node_v": int(nv[i]), "length_m": length, "factor": 1.0,
                        "cost_fwd": length + wait_m + du[i] + dv[i], "cost_bwd": length + wait_m + du[i] + dv[i],
                        "snap_m": float(du[i] + dv[i]), "geometry": geom})
    return gpd.GeoDataFrame(records, columns=columns, geometry="geometry", crs=ferries.crs)


def ferry_trace(params: GraphParams) -> str:
    return json.dumps({"rules": ["C-GRAPH-03"], "factor": 1.0, "inputs": {"ferry_wait_s": params.ferry_wait_s,
                                                                           "cycling_speed_kmh": params.cycling_speed_kmh}})


# --- directed arcs -------------------------------------------------------------------------------


def arcs(edges: pd.DataFrame) -> pd.DataFrame:
    """Directed arcs: tail, head, cost, edge (row position in edges), forward (True = node_u -> node_v)."""
    pos = np.arange(len(edges))
    fwd = edges["cost_fwd"].notna().to_numpy()
    bwd = edges["cost_bwd"].notna().to_numpy()
    nu, nv = edges["node_u"].to_numpy(), edges["node_v"].to_numpy()
    a = pd.DataFrame({"tail": nu[fwd], "head": nv[fwd], "cost": edges["cost_fwd"].to_numpy()[fwd],
                      "edge": pos[fwd], "forward": True})
    b = pd.DataFrame({"tail": nv[bwd], "head": nu[bwd], "cost": edges["cost_bwd"].to_numpy()[bwd],
                      "edge": pos[bwd], "forward": False})
    return pd.concat([a, b], ignore_index=True)
