"""Network coherence rules N1–N7 (guide 1.5 and 3.2 Stufe 6, prompts/09).

All functions read the proposed categories and return flags; they never change a category.
A flag is a dict {"id": rule id, "flag": code, "inputs": {...}}; results are dicts
{segment_id: [flag, ...]}. Parameters come from rules.yaml (section coherence).

The graph is an undirected networkx.MultiGraph: nodes are OSM node ids (node_u/node_v), edges are
segments (key = segment_id). Geometries start at node_u (as written by s02_network).
"""

import heapq
import math
from collections import defaultdict
from collections.abc import Iterable

import geopandas as gpd
import networkx as nx
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union

Flags = dict[str, list[dict]]

# Technical tolerances for geometry operations (not rule thresholds): snapping lines to polygon
# boundaries and ignoring touching slivers when deciding whether an area meets the work-area edge.
_SNAP_M = 0.01
_MIN_SHARED_EDGE_M = 1.0


def _flag(rule_id: str, flag: str, **inputs) -> dict:
    return {"id": rule_id, "flag": flag, "inputs": inputs}


def _add(flags: Flags, sid: str, entry: dict) -> None:
    flags.setdefault(sid, []).append(entry)


def merge_flags(*parts: Flags) -> Flags:
    out: Flags = {}
    for part in parts:
        for sid, entries in part.items():
            out.setdefault(sid, []).extend(entries)
    return out


# --- graph -----------------------------------------------------------------------------------


def segment_speed_kmh(cat: str, travel_speed_kmh, rules) -> float | None:
    """Soll speed of the category; categories without one (SW) use the segment's travel speed (N4)."""
    speed = rules.categories[cat].speed_kmh
    if speed is not None:
        return float(speed)
    fallback = travel_speed_kmh
    return None if fallback is None or fallback != fallback else float(fallback)


def build_graph(seg: gpd.GeoDataFrame, rules) -> nx.MultiGraph:
    """Graph of classified segments. seg needs segment_id, node_u, node_v, cat, length_m, highway,
    travel_speed_kmh, geometry. Rows are added in segment_id order so results are reproducible."""
    g = nx.MultiGraph()
    for r in seg.sort_values("segment_id").itertuples(index=False):
        geom = r.geometry
        u, v = int(r.node_u), int(r.node_v)
        g.add_node(u, point=Point(geom.coords[0]))
        g.add_node(v, point=Point(geom.coords[-1]))
        g.add_edge(u, v, key=r.segment_id, cat=r.cat, length_m=float(r.length_m), highway=r.highway,
                   speed_kmh=segment_speed_kmh(r.cat, r.travel_speed_kmh, rules), geometry=geom, node_u=u)
    return g


def _incident(g: nx.MultiGraph, node) -> list[tuple]:
    """(segment_id, other node, data) per incident edge; a self-loop appears once."""
    out, seen = [], set()
    for _, other, key, data in g.edges(node, keys=True, data=True):
        if key in seen:
            continue
        seen.add(key)
        out.append((key, other, data))
    return out


# --- N1 Durchgängigkeit ----------------------------------------------------------------------


def n1_dead_ends(g: nx.MultiGraph, rules, area_edge_nodes: set, city_boundary) -> tuple[Flags, list[dict]]:
    """Ends of GOW runs (nodes with exactly one GOW segment) and their status:
    ok_sw (an end_ok category meets there), ok_city_boundary, unknown_area_edge or dead_end (flagged)."""
    rule = rules.coherence_rule("N1")
    gow, ok_cats = set(rule.gow_categories), set(rule.end_ok_categories)
    tol = rule.param("boundary_tolerance_m")
    flags: Flags = {}
    ends = []
    for node in sorted(g.nodes):
        inc = _incident(g, node)
        gow_edges = [(sid, d) for sid, _, d in inc if d["cat"] in gow]
        if len(gow_edges) != 1:
            continue
        sid, data = gow_edges[0]
        point = g.nodes[node]["point"]
        if any(d["cat"] in ok_cats for _, _, d in inc):
            status = "ok_sw"
        elif city_boundary is not None and point.distance(city_boundary) <= tol:
            status = "ok_city_boundary"
        elif node in area_edge_nodes:
            status = "unknown_area_edge"
        else:
            status = "dead_end"
            _add(flags, sid, _flag("N1", "N1_dead_end", node=int(node), cat=data["cat"],
                                   other_cats=sorted({d["cat"] for _, _, d in inc if d["cat"] not in gow})))
        ends.append({"node": int(node), "segment_id": sid, "cat": data["cat"], "status": status})
    return flags, ends


# --- N2 / N7 Inseln --------------------------------------------------------------------------


def _bearing_out(geom: LineString, at_start: bool, sample_m: float) -> float:
    """Direction (radians) leaving the segment end (start or end of geom), over its first sample_m."""
    dist = min(sample_m, geom.length / 2)
    origin = geom.coords[0] if at_start else geom.coords[-1]
    p = geom.interpolate(dist if at_start else geom.length - dist)
    return math.atan2(p.y - origin[1], p.x - origin[0])


def _deflection_deg(b1: float, b2: float) -> float:
    """0° = straight on (bearings leaving the node point in opposite directions)."""
    diff = abs(math.degrees(b1 - b2)) % 360
    diff = min(diff, 360 - diff)
    return 180.0 - diff


def strokes(g: nx.MultiGraph, rules) -> list[list[str]]:
    """Streets as ordered segment lists: degree-2 nodes always continue, junctions continue to the mutually
    best partner within max_deflection_deg (N2 note in rules.yaml)."""
    rule = rules.coherence_rule("N2")
    max_def, sample = rule.param("max_deflection_deg"), rule.param("bearing_sample_m")
    partner: dict[tuple, tuple] = {}  # (segment_id, end) -> (segment_id, end); end = 0 at node_u, 1 at node_v
    for node in sorted(g.nodes):
        ends = []
        for _, other, key, data in g.edges(node, keys=True, data=True):
            if other == node:  # self-loop: both ends at this node
                ends += [(key, 0, data), (key, 1, data)]
            else:
                ends.append((key, 0 if data["node_u"] == node else 1, data))
        ends = list({(k, e): (k, e, d) for k, e, d in ends}.values())
        if len(ends) < 2:
            continue
        if len(ends) == 2:
            (k1, e1, _), (k2, e2, _) = ends
            if k1 != k2:
                partner[(k1, e1)], partner[(k2, e2)] = (k2, e2), (k1, e1)
            continue
        bearings = {(k, e): _bearing_out(d["geometry"], e == 0, sample) for k, e, d in ends}
        best = {}
        for a in bearings:
            cands = [(_deflection_deg(bearings[a], bearings[b]), b) for b in bearings if b[0] != a[0]]
            if cands:
                best[a] = min(cands)
        for a, (deflection, b) in best.items():
            if deflection <= max_def and best.get(b, (None, None))[1] == a:
                partner[a] = b

    out, used = [], set()

    def walk(sid: str, entry_end: int) -> list[str]:
        seq = []
        while sid not in used:
            used.add(sid)
            seq.append(sid)
            nxt = partner.get((sid, 1 - entry_end))
            if nxt is None:
                break
            sid, entry_end = nxt
        return seq

    keys = sorted(k for _, _, k in g.edges(keys=True))
    for sid in keys:  # open strokes start at an end without partner
        if sid in used:
            continue
        for end in (0, 1):
            if (sid, end) not in partner:
                out.append(walk(sid, end))
                break
    for sid in keys:  # remaining closed loops
        if sid not in used:
            out.append(walk(sid, 0))
    return out


def n2_islands(g: nx.MultiGraph, rules) -> Flags:
    """N2: run of one category shorter than min_run_m between two runs of the same other category.
    N7: smoothing proposal (that other category) as a separate flag."""
    min_run = rules.coherence_rule("N2").param("min_run_m")
    edge = {k: d for _, _, k, d in g.edges(keys=True, data=True)}
    flags: Flags = {}
    for stroke in strokes(g, rules):
        runs: list[tuple[str, list[str], float]] = []
        for sid in stroke:
            cat, length = edge[sid]["cat"], edge[sid]["length_m"]
            if runs and runs[-1][0] == cat:
                runs[-1] = (cat, runs[-1][1] + [sid], runs[-1][2] + length)
            else:
                runs.append((cat, [sid], length))
        for i in range(1, len(runs) - 1):
            cat, sids, length = runs[i]
            before, after = runs[i - 1][0], runs[i + 1][0]
            if before == after != cat and length < min_run:
                for sid in sids:
                    _add(flags, sid, _flag("N2", "N2_island", cat=cat, neighbour_cat=before,
                                           run_m=round(length, 1), min_run_m=min_run))
                    _add(flags, sid, _flag("N7", f"N7_smooth:{before}", proposed=before, current=cat))
    return flags


# --- N3 Aufenthaltsbereiche ------------------------------------------------------------------


def _polygonal(geom):
    """Only the polygon parts of a geometry (intersections can add lines and points)."""
    parts = [g for g in getattr(geom, "geoms", [geom]) if g.geom_type in ("Polygon", "MultiPolygon")]
    return shapely.union_all(parts) if parts else shapely.Polygon()


def n3_areas(seg: gpd.GeoDataFrame, rules, work_area, city_area) -> tuple[gpd.GeoDataFrame, Flags]:
    """Areas enclosed by GOW/SW lines (and the city boundary) inside the work area.

    complete = the area does not reach the work-area edge inside the city; has_etw = at least one ETW segment
    has its midpoint inside (areas without are junction islands or green space, not Aufenthaltsbereiche);
    small = has_etw and area < min_area_ha. ETW segments in small, complete areas get N3_small_area."""
    rule = rules.coherence_rule("N3")
    min_ha = rule.param("min_area_ha")
    etw = set(rules.coherence_rule("N4").etw_categories)
    network = set(rules.coherence_rule("N4").restricted_categories)
    region = _polygonal(work_area if city_area is None else work_area.intersection(city_area))
    open_edge = region.boundary if city_area is None else region.boundary.difference(
        city_area.boundary.buffer(_SNAP_M * 10))
    lines = list(seg.loc[seg["cat"].isin(network), "geometry"].intersection(region)) + [region.boundary]
    polys = [p for p in polygonize(unary_union([ln for ln in lines if not ln.is_empty])) if region.covers(
        p.representative_point())]
    rows = []
    for p in polys:
        shared = p.boundary.intersection(open_edge.buffer(_SNAP_M)).length
        area_ha = p.area / 10_000
        rows.append({"area_ha": area_ha, "perimeter_m": p.length,
                     "compactness": 4 * math.pi * p.area / p.length ** 2 if p.length else None,
                     "complete": shared <= _MIN_SHARED_EDGE_M, "geometry": p})
    areas = gpd.GeoDataFrame(rows, columns=["area_ha", "perimeter_m", "compactness", "complete", "geometry"],
                             geometry="geometry", crs=seg.crs)
    areas.insert(0, "area_id", range(1, len(areas) + 1))
    cand = seg[seg["cat"].isin(etw)]
    mids = gpd.GeoSeries(shapely.line_interpolate_point(cand.geometry.to_numpy(), 0.5, normalized=True),
                         index=cand.index, crs=seg.crs)
    inside = gpd.sjoin(gpd.GeoDataFrame(geometry=mids), areas[["area_id", "area_ha", "complete", "geometry"]],
                       predicate="within")
    n_etw = inside["area_id"].value_counts()
    areas["n_etw_segments"] = areas["area_id"].map(n_etw).fillna(0).astype(int)
    areas["has_etw"] = areas["n_etw_segments"] > 0
    areas["small"] = areas["has_etw"] & (areas["area_ha"] < min_ha)
    flags: Flags = {}
    small_ids = set(areas.loc[areas["small"] & areas["complete"], "area_id"])
    hits = inside[inside["area_id"].isin(small_ids)]
    for idx, r in hits.iterrows():
        _add(flags, cand.loc[idx, "segment_id"], _flag("N3", "N3_small_area", area_id=int(r["area_id"]),
                                                        area_ha=round(float(r["area_ha"]), 2), min_area_ha=min_ha))
    return areas, flags


# --- N4 Schleichverkehr ----------------------------------------------------------------------


def _drive_adjacency(g: nx.MultiGraph, rules, cats: set | None):
    """node -> [(other, seconds, segment_id, etw_m)], cheapest parallel edge only, sorted for determinism."""
    rule = rules.coherence_rule("N4")
    etw, excluded = set(rule.etw_categories), set(rule.exclude_highway)
    best: dict[tuple, tuple] = {}
    for u, v, k, d in g.edges(keys=True, data=True):
        if u == v or d["highway"] in excluded or not d["speed_kmh"] or (cats is not None and d["cat"] not in cats):
            continue
        sec = d["length_m"] / (d["speed_kmh"] / 3.6)
        etw_m = d["length_m"] if d["cat"] in etw else 0.0
        pair = (min(u, v), max(u, v))
        if pair not in best or (sec, k) < best[pair][:2]:
            best[pair] = (sec, k, etw_m)
    adj: dict = defaultdict(list)
    for (u, v), (sec, k, etw_m) in sorted(best.items()):
        adj[u].append((v, sec, k, etw_m))
        adj[v].append((u, sec, k, etw_m))
    return adj


def _dijkstra(adj, source):
    """Returns settle order, time, etw metres along the path, predecessor (node, segment_id)."""
    dist, etw_m, pred, order = {source: 0.0}, {source: 0.0}, {}, []
    heap, done = [(0.0, 0, source)], set()
    counter = 1
    while heap:
        d, _, node = heapq.heappop(heap)
        if node in done:
            continue
        done.add(node)
        order.append(node)
        for other, sec, sid, e in adj.get(node, ()):
            nd = d + sec
            if other not in done and nd < dist.get(other, math.inf):
                dist[other], etw_m[other], pred[other] = nd, etw_m[node] + e, (node, sid)
                heapq.heappush(heap, (nd, counter, other))
                counter += 1
    return order, dist, etw_m, pred


def n4_shortcuts(g: nx.MultiGraph, rules) -> tuple[Flags, dict]:
    """N4: for every pair of nodes of the GOW/SW network, the time-shortest path at Soll speed is compared with
    the path restricted to GOW/SW; if the shortest path uses more than max_etw_m of ETW while a GOW/SW path
    exists, its ETW segments get N4_shortcut with the number of such OD pairs. Pairs without any GOW/SW path
    are a network gap (see N1), not a shortcut; they are only counted."""
    rule = rules.coherence_rule("N4")
    max_etw = rule.param("max_etw_m")
    restricted = set(rule.restricted_categories)
    free_adj = _drive_adjacency(g, rules, None)
    gow_adj = _drive_adjacency(g, rules, restricted)
    od = sorted(n for n in gow_adj if gow_adj[n])
    rank = {n: i for i, n in enumerate(od)}
    pair_count: dict[str, int] = defaultdict(int)
    n_pairs = n_flagged = n_no_gow = 0
    detours = []
    for s in od:
        order, dist, etw_m, pred = _dijkstra(free_adj, s)
        _, gdist, _, _ = _dijkstra(gow_adj, s)
        below: dict = defaultdict(int)
        for node in reversed(order):
            if node in rank and rank[node] > rank[s]:
                n_pairs += 1
                if etw_m[node] > max_etw:
                    if node not in gdist:
                        n_no_gow += 1
                    else:
                        n_flagged += 1
                        below[node] += 1
                        detours.append(gdist[node] / dist[node])
            if node in pred and below[node]:
                parent, sid = pred[node]
                below[parent] += below[node]
                if g.edges[parent, node, sid]["cat"] in set(rule.etw_categories):
                    pair_count[sid] += below[node]
    flags: Flags = {}
    for sid in sorted(pair_count):
        _add(flags, sid, _flag("N4", "N4_shortcut", n_od_pairs=pair_count[sid], max_etw_m=max_etw))
    detours.sort()
    stats = {"od_nodes": len(od), "od_pairs": n_pairs, "flagged_pairs": n_flagged, "etw_only_pairs": n_no_gow,
             "median_detour_factor": detours[len(detours) // 2] if detours else None}
    return flags, stats


# --- N5 Übergänge ----------------------------------------------------------------------------


def n5_transitions(g: nx.MultiGraph, rules) -> tuple[Flags, list[dict]]:
    """N5: gate transitions per node (listed, the presence of a gate is not in the data) and direct
    transitions from >= min_speed_kmh to a 30 category (flagged on the 30 side)."""
    rule = rules.coherence_rule("N5")
    vmin, v30 = rule.param("min_speed_kmh"), rule.param("target_speed_kmh")
    flags: Flags = {}
    nodes = []
    for node in sorted(g.nodes):
        inc = _incident(g, node)
        cats = {d["cat"] for _, _, d in inc}
        gates = [[a, b] for t in rule.gate_transitions for a in t.from_ for b in t.to if a in cats and b in cats]
        fast = [d for _, _, d in inc if d["speed_kmh"] is not None and d["speed_kmh"] >= vmin]
        slow = [(sid, d) for sid, _, d in inc if rules.categories[d["cat"]].speed_kmh == v30]
        direct = bool(fast and slow)
        if direct:
            top = max(d["speed_kmh"] for d in fast)
            for sid, d in slow:
                _add(flags, sid, _flag("N5", "N5_direct_to_30", node=int(node), from_speed_kmh=top, cat=d["cat"],
                                       min_speed_kmh=vmin))
        if gates or direct:
            nodes.append({"node": int(node), "gates": gates, "direct_to_30": direct})
    return flags, nodes


# --- N6 Knotentypen --------------------------------------------------------------------------


def node_category_pair(cats: Iterable[str], rules) -> tuple[str, str]:
    """Highest category (up to two of its segments = the through road) and highest of the rest."""
    rank = {c: i for i, c in enumerate(rules.coherence_rule("N6").category_rank)}
    ordered = sorted(cats, key=rank.__getitem__)
    top = ordered[0]
    rest = list(ordered)
    for _ in range(2):
        if top in rest:
            rest.remove(top)
    return (top, rest[0]) if rest else (top, top)


def soll_node_type(pair: tuple[str, str], rules) -> str:
    for entry in rules.coherence_rule("N6").node_types:
        if sorted(entry.pair) == sorted(pair):
            return entry.type
    return "not_defined"


def ist_node_types(points: gpd.GeoSeries, signals: gpd.GeoSeries, tables: gpd.GeoSeries,
                   roundabout_nodes: set, radius_m: float) -> dict:
    """Ist junction type per node from OSM: roundabout, signal_plateau, signal, plateau (else absent)."""

    def near(features: gpd.GeoSeries) -> set:
        if features is None or features.empty or points.empty:
            return set()
        hits = gpd.sjoin_nearest(gpd.GeoDataFrame(geometry=points), gpd.GeoDataFrame(geometry=features),
                                 max_distance=radius_m, how="inner")
        return set(hits.index)

    sig, tab = near(signals), near(tables)
    out = {}
    for node in points.index:
        if node in roundabout_nodes:
            out[node] = "roundabout"
        elif node in sig:
            out[node] = "signal_plateau" if node in tab else "signal"
        elif node in tab:
            out[node] = "plateau"
    return out


def n6_node_types(g: nx.MultiGraph, rules, ist_types: dict) -> tuple[Flags, list[dict]]:
    """N6: Soll junction type for nodes with degree >= 3 and comparison with the Ist type from OSM."""
    rule = rules.coherence_rule("N6")
    flags: Flags = {}
    nodes = []
    for node in sorted(g.nodes):
        if g.degree(node) < 3:
            continue
        inc = _incident(g, node)
        pair = node_category_pair([d["cat"] for _, _, d in inc], rules)
        soll = soll_node_type(pair, rules)
        ist = ist_types.get(node, "none_mapped")
        if soll == "not_defined":
            result = "not_defined"
        elif ist in rule.ist_check[soll].ok:
            result = "match"
        elif ist in rule.ist_check[soll].not_checkable:
            result = "not_checkable"
        else:
            result = "mismatch"
        if result == "mismatch":
            for sid, _, _ in inc:
                _add(flags, sid, _flag("N6", "N6_node_mismatch", node=int(node), pair=list(pair), soll=soll, ist=ist))
        nodes.append({"node": int(node), "pair": list(pair), "soll_type": soll, "ist_type": ist, "result": result})
    return flags, nodes
