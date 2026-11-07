"""Cycle network design (prompts/16): Soll resistance, corridors, hierarchy, meshes, parallel rule, continuity.

Rules C-NET-01..13 in config/cycling_rules.yaml (network_design) plus the thresholds in cycle_categories
(RSV trigger and length, mesh widths) and principles (P-ATT-03, P-DIR-01, P-COH-03). Every value comes in
through NetworkParams. Costs are metres of perceived resistance (pipeline/lib/cycle_graph.py); the network
design is undirected.
"""

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import shapely
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

from config.schema.cycling_model import CyclingRuleSet

CATEGORY_ORDER = ("ERSCHL", "BASIS", "HAUPT", "RSV")
RANK = {c: i for i, c in enumerate(CATEGORY_ORDER)}
MIN_COST_M = 1e-6  # sparse graphs need positive weights
SEED_TRIES = 3  # start edges tried per mesh before it counts as not divisible (search effort, not a rule)
MAIN_PENALTY = 1000.0  # cost factor on high-volume edges in the P-ATT-03 search: use them only where unavoidable
GAP_NO_CANDIDATES = "keine Kandidatenkanten in der Masche"
GAP_NOT_DIVISIBLE = "keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand)"
GAP_MAX_ROUNDS = "max_rounds erreicht"


@dataclass(frozen=True)
class NetworkParams:
    innenstadt_label: str
    innenstadt_lonlat: tuple
    hub_min_modes: int
    hub_radius_m: float
    university_amenity: tuple
    job_cluster_quantile: float
    merge_m: float
    k_nearest: int
    max_pair_m: float
    soll_factors: dict       # key (road category or "path") -> numeric factor
    soll_factor_keys: dict   # key -> name in routing_impedance.factors
    max_reduction: float
    official_multiplier: float
    match_buffer_m: float
    min_overlap: float
    official_status: tuple
    planned_status: tuple
    rsv_trigger: float
    rsv_min_length_m: float
    rsv_gap_max_m: float
    mesh_max_m: dict
    mesh_ref_density: float | None     # residents per km² (C-NET-07 density_scaling), None = constant mesh
    mesh_density_levels: tuple
    barrier_lines: dict
    barrier_exclude_tunnel: bool
    exclude_areas: dict
    exclude_area_min_m2: float
    simplify_m: float
    seed_core_share: float
    max_rounds: int
    min_split_route_m: float
    binding_radius_m: float
    nahversorgung_shops: tuple
    patt_dtv: float
    patt_parallel_max_m: float
    patt_min_run_m: float
    patt_max_on_main_m: float
    detour_max: dict
    continuity_max_gap_m: float
    coverage_m: float
    compare_buffer_m: float

    @classmethod
    def from_rules(cls, cyc: CyclingRuleSet) -> "NetworkParams":
        r = {x["id"]: x for x in cyc.network_design["rules"]}
        factors = cyc.routing_impedance["factors"]
        cats = cyc.cycle_categories
        checks = {c["id"]: c for p in cyc.principles.values() for c in p["checks"]}
        soll = r["C-NET-03"]["soll_factors"]
        c01 = r["C-NET-01"]
        return cls(
            innenstadt_label=c01["innenstadt"]["label"],
            innenstadt_lonlat=(float(c01["innenstadt"]["lon"]), float(c01["innenstadt"]["lat"])),
            hub_min_modes=int(c01["hub_min_modes"]),
            hub_radius_m=float(c01["hub_radius_m"]),
            university_amenity=tuple(c01["university_amenity"]),
            job_cluster_quantile=float(c01["job_cluster_quantile"]),
            merge_m=float(c01["merge_m"]),
            k_nearest=int(r["C-NET-02"]["k_nearest"]),
            max_pair_m=float(r["C-NET-02"]["max_pair_km"]) * 1000,
            soll_factors={k: float(factors[v]) for k, v in soll.items()},
            soll_factor_keys=dict(soll),
            max_reduction=float(r["C-NET-04"]["max_reduction"]),
            official_multiplier=float(r["C-NET-05"]["multiplier"]),
            match_buffer_m=float(r["C-NET-05"]["match_buffer_m"]),
            min_overlap=float(r["C-NET-05"]["min_overlap"]),
            official_status=tuple(r["C-NET-05"]["official_status"]),
            planned_status=tuple(r["C-NET-05"]["planned_status"]),
            rsv_trigger=float(cats["RSV"]["demand_trigger_cyclists_weekday"]["value"]),
            rsv_min_length_m=float(cats["RSV"]["min_route_length_km"]["value"]) * 1000,
            rsv_gap_max_m=float(r["C-NET-06"]["gap_max_m"]),
            mesh_max_m={c: float(cats[c]["mesh_m"]["range"][1]) for c in ("HAUPT", "BASIS")},
            mesh_ref_density=(float(r["C-NET-07"]["density_scaling"]["reference_density_per_km2"]["value"])
                              if "density_scaling" in r["C-NET-07"] else None),
            mesh_density_levels=tuple(r["C-NET-07"].get("density_scaling", {}).get("levels", ())),
            barrier_lines={k: tuple(v) for k, v in r["C-NET-07"]["barrier_lines"].items()},
            barrier_exclude_tunnel=bool(r["C-NET-07"]["barrier_exclude_tunnel"]),
            exclude_areas={k: tuple(v) for k, v in r["C-NET-07"]["exclude_areas"].items()},
            exclude_area_min_m2=float(r["C-NET-07"]["exclude_area_min_m2"]),
            simplify_m=float(r["C-NET-07"]["simplify_m"]),
            seed_core_share=float(r["C-NET-08"]["seed_core_share"]),
            max_rounds=int(r["C-NET-08"]["max_rounds"]),
            min_split_route_m=float(r["C-NET-08"]["min_split_route_m"]),
            binding_radius_m=float(r["C-NET-09"]["binding_radius_m"]),
            nahversorgung_shops=tuple(r["C-NET-09"]["nahversorgung_shops"]),
            patt_dtv=float(checks["P-ATT-03"]["dtv"]),
            patt_parallel_max_m=float(checks["P-ATT-03"]["parallel_max_m"]),
            patt_min_run_m=float(r["C-NET-10"]["min_run_m"]),
            patt_max_on_main_m=float(r["C-NET-10"]["max_on_main_m"]),
            detour_max={k: float(v) for k, v in checks["P-DIR-01"]["thresholds"].items()},
            continuity_max_gap_m=float(r["C-NET-11"]["max_gap_m"]),
            coverage_m=float(checks["P-COH-03"]["coverage_m"]),
            compare_buffer_m=float(r["C-NET-13"]["compare_buffer_m"]),
        )


# --- C-NET-03..05 Soll resistance and bonuses -------------------------------------------------------


def soll_factor_for(kind: str, cat_final, ist_factor: float, p: NetworkParams) -> tuple[float, str]:
    """Length factor of the rule-conform facility (C-NET-03) and its factor name; "ist" keeps the Ist factor."""
    if kind == "path":
        key = "path"
    elif kind == "road" and isinstance(cat_final, str) and cat_final in p.soll_factors:
        key = cat_final
    else:
        return float(ist_factor), "ist"
    return p.soll_factors[key], p.soll_factor_keys[key]


def soll_costs(length, ist_factor, cost_fwd, cost_bwd, soll_factor) -> tuple[np.ndarray, np.ndarray]:
    """Soll cost per direction = length x Soll factor + the node delays contained in the Ist cost."""
    length, ist_factor, soll_factor = (np.asarray(x, dtype="float64") for x in (length, ist_factor, soll_factor))
    out = []
    for cost in (cost_fwd, cost_bwd):
        cost = np.asarray(cost, dtype="float64")
        delay = np.maximum(cost - length * ist_factor, 0.0)
        out.append(length * soll_factor + delay)  # NaN (direction not allowed) stays NaN
    return out[0], out[1]


def demand_multiplier(cyc, p: NetworkParams) -> np.ndarray:
    """C-NET-04: 1 - max_reduction x min(cyc / RSV trigger, 1); no value -> 1."""
    c = np.nan_to_num(np.asarray(cyc, dtype="float64"), nan=0.0)
    return 1.0 - p.max_reduction * np.clip(c / p.rsv_trigger, 0.0, 1.0)


def overlap_share(lines: np.ndarray, zones: np.ndarray) -> np.ndarray:
    """Share of each line's length inside the zones; overlapping zones count once (they are united per line,
    not as a whole, which would give one huge polygon for a connected network)."""
    lines = np.asarray(lines, dtype=object)
    zones = np.asarray(zones, dtype=object)
    share = np.zeros(len(lines))
    if len(lines) == 0 or len(zones) == 0:
        return share
    li, zi = shapely.STRtree(zones).query(lines, predicate="intersects")
    if len(li):
        counts = np.bincount(li, minlength=len(lines))
        single = counts[li] == 1
        share[li[single]] = shapely.length(shapely.intersection(lines[li[single]], zones[zi[single]]))
        multi = ~single
        if multi.any():
            order = np.argsort(li[multi], kind="stable")
            lm, zm = li[multi][order], zi[multi][order]
            starts = np.flatnonzero(np.r_[True, lm[1:] != lm[:-1]])
            for a, b in zip(starts, np.r_[starts[1:], len(lm)]):
                share[lm[a]] = shapely.length(shapely.intersection(lines[lm[a]], shapely.union_all(zones[zm[a:b]])))
    length = shapely.length(lines)
    return np.divide(share, length, out=np.zeros_like(share), where=length > 0)


def undirected_cost(cost_fwd, cost_bwd) -> np.ndarray:
    """Cheaper allowed direction (the network design is undirected); NaN if neither is allowed."""
    return np.fmin(np.asarray(cost_fwd, dtype="float64"), np.asarray(cost_bwd, dtype="float64"))


# --- graph -----------------------------------------------------------------------------------------------


class Graph:
    """Undirected graph over a set of edges (row positions); the cheapest edge per node pair carries paths."""

    def __init__(self, node_u, node_v, cost, edge_pos):
        u = np.asarray(node_u, dtype="int64")
        v = np.asarray(node_v, dtype="int64")
        c = np.maximum(np.asarray(cost, dtype="float64"), MIN_COST_M)
        e = np.asarray(edge_pos, dtype="int64")
        self._u, self._v, self._c, self._e = u, v, c, e
        self._ends = None
        self.nodes, inv = np.unique(np.concatenate([u, v]), return_inverse=True)
        n, m = len(self.nodes), len(u)
        tail = np.concatenate([inv[:m], inv[m:]])
        head = np.concatenate([inv[m:], inv[:m]])
        cc, ee = np.concatenate([c, c]), np.concatenate([e, e])
        order = np.lexsort((cc, head, tail))
        keys = tail[order] * n + head[order]
        first = np.ones(len(order), dtype=bool)
        first[1:] = keys[1:] != keys[:-1]
        sel = order[first]
        self._keys = keys[first]
        self._edge = ee[sel]
        self.n = n
        self.matrix = csr_matrix((cc[sel], (tail[sel], head[sel])), shape=(n, n))

    def without_nodes(self, node_ids) -> "Graph":
        """Copy without the given nodes (and their edges)."""
        drop = np.isin(self._u, node_ids) | np.isin(self._v, node_ids)
        return Graph(self._u[~drop], self._v[~drop], self._c[~drop], self._e[~drop])

    def index(self, node_ids) -> np.ndarray:
        """Graph index per node id; -1 if the node is not in the graph."""
        ids = np.asarray(node_ids, dtype="int64")
        if self.n == 0:
            return np.full(len(ids), -1)
        i = np.clip(np.searchsorted(self.nodes, ids), 0, self.n - 1)
        return np.where(self.nodes[i] == ids, i, -1)

    def ends(self, edge_pos: int) -> tuple[int, int]:
        """Node ids of an edge of this graph."""
        if self._ends is None:
            self._ends = {int(e): (int(u), int(v)) for e, u, v in zip(self._e, self._u, self._v)}
        return self._ends[int(edge_pos)]

    def edge_between(self, a: int, b: int) -> int:
        return int(self._edge[np.searchsorted(self._keys, a * self.n + b)])

    def dijkstra(self, sources, min_only: bool = False):
        return dijkstra(self.matrix, directed=True, indices=sources, return_predecessors=True, min_only=min_only)

    def path(self, pred_row: np.ndarray, source: int, target: int) -> list[int] | None:
        """Edge positions from source to target along a predecessor row; None if unreachable."""
        if target == source:
            return []
        if target < 0 or pred_row[target] < 0:
            return None
        seq, t = [], target
        while t != source:
            s = int(pred_row[t])
            if s < 0:
                return None
            seq.append(self.edge_between(s, t))
            t = s
        return seq[::-1]


@dataclass
class DesignInputs:
    """Arrays over all edges of the cycle graph used by the design steps (row positions = edge positions)."""
    geom: np.ndarray
    node_u: np.ndarray
    node_v: np.ndarray
    cost: np.ndarray        # undirected design cost (Soll x bonuses), NaN = not routable
    length: np.ndarray
    demand: np.ndarray      # cyc_calibrated, NaN -> 0
    routable: np.ndarray    # usable for new routes (main component, finite cost)
    mid: np.ndarray = field(default=None)
    mid_tree: shapely.STRtree = field(default=None)
    geom_tree: shapely.STRtree = field(default=None)
    node_ids: np.ndarray = field(default=None)
    node_xy: np.ndarray = field(default=None)

    @classmethod
    def build(cls, geom, node_u, node_v, cost, length, demand, routable) -> "DesignInputs":
        geom = np.asarray(geom, dtype=object)
        inp = cls(geom, np.asarray(node_u, dtype="int64"), np.asarray(node_v, dtype="int64"),
                  np.asarray(cost, dtype="float64"), np.asarray(length, dtype="float64"),
                  np.nan_to_num(np.asarray(demand, dtype="float64"), nan=0.0),
                  np.asarray(routable, dtype=bool) & np.isfinite(np.asarray(cost, dtype="float64")))
        inp.mid = shapely.line_interpolate_point(geom, 0.5, normalized=True)
        inp.mid_tree = shapely.STRtree(inp.mid)
        inp.geom_tree = shapely.STRtree(geom)
        ids = np.concatenate([inp.node_u, inp.node_v])
        pts = np.concatenate([shapely.get_coordinates(shapely.get_point(geom, 0)),
                              shapely.get_coordinates(shapely.get_point(geom, -1))])
        inp.node_ids, first = np.unique(ids, return_index=True)
        inp.node_xy = pts[first]
        return inp

    def graph(self, mask: np.ndarray) -> Graph:
        pos = np.flatnonzero(mask & self.routable)
        return Graph(self.node_u[pos], self.node_v[pos], self.cost[pos], pos)

    def net_nodes(self, net_mask: np.ndarray) -> np.ndarray:
        return np.unique(np.concatenate([self.node_u[net_mask], self.node_v[net_mask]]))


def route_nodes(route: list[int], node_u: np.ndarray, node_v: np.ndarray) -> list[int]:
    """Node sequence of an ordered edge list (len(route) + 1 nodes). Where two edges do not share a node
    (a branch), the next edge starts a new piece and its far end is taken."""
    if not route:
        return []
    a, b = int(node_u[route[0]]), int(node_v[route[0]])
    if len(route) > 1 and a in (node_u[route[1]], node_v[route[1]]):
        a, b = b, a
    nodes = [a, b]
    for e in route[1:]:
        u, v = int(node_u[e]), int(node_v[e])
        nodes.append(v if u == nodes[-1] else u)
    return nodes


def chain_ok(route: list[int], node_u: np.ndarray, node_v: np.ndarray, nodes: list[int]) -> np.ndarray:
    """Per route edge: True if it joins nodes[i] and nodes[i + 1] (False after a branch of the route)."""
    return np.array([{int(node_u[e]), int(node_v[e])} == {nodes[i], nodes[i + 1]} for i, e in enumerate(route)], dtype=bool)


def _runs(values) -> list[tuple[int, int, object]]:
    """Runs of equal consecutive values: (start, stop, value), stop exclusive."""
    out, start = [], 0
    for i in range(1, len(values) + 1):
        if i == len(values) or values[i] != values[start]:
            out.append((start, i, values[start]))
            start = i
    return out


# --- C-NET-01/02 corridors -------------------------------------------------------------------------------


def merge_points(xy: np.ndarray, merge_m: float) -> np.ndarray:
    """Keep mask: points in priority order, dropping each point within merge_m of an earlier kept point."""
    keep = np.zeros(len(xy), dtype=bool)
    kept: list[np.ndarray] = []
    for i, p in enumerate(np.asarray(xy, dtype="float64")):
        if not kept or np.min(np.hypot(*(np.array(kept) - p).T)) > merge_m:
            keep[i] = True
            kept.append(p)
    return keep


def hubs(xy: np.ndarray, types: list[set], radius_m: float, min_modes: int) -> np.ndarray:
    """C-NET-01: mask of stations where, together with the stations within radius_m, at least min_modes
    different route types stop."""
    xy = np.asarray(xy, dtype="float64")
    if len(xy) == 0:
        return np.zeros(0, dtype=bool)
    near = cKDTree(xy).query_ball_point(xy, radius_m)
    return np.array([len(set().union(*(types[j] for j in nb))) >= min_modes for nb in near])


def corridor_pairs(xy: np.ndarray, centre: int, k: int, max_m: float) -> list[tuple[int, int]]:
    """C-NET-02: each point with its k nearest points (up to max_m) and with the Innenstadt (centre)."""
    xy = np.asarray(xy, dtype="float64")
    pairs = set()
    if len(xy) > 1:
        d, j = cKDTree(xy).query(xy, k=min(k + 1, len(xy)))
        for i in range(len(xy)):
            for dd, jj in zip(np.atleast_1d(d[i]), np.atleast_1d(j[i])):
                if jj != i and dd <= max_m:
                    pairs.add((min(i, int(jj)), max(i, int(jj))))
    pairs |= {(min(i, centre), max(i, centre)) for i in range(len(xy)) if i != centre}
    return sorted(pairs)


def route_pairs(g: Graph, point_nodes: np.ndarray, pairs: list[tuple[int, int]]) -> dict[tuple[int, int], list[int]]:
    """Cheapest path (edge positions, ordered from the first to the second point) for each pair."""
    out = {}
    sources = sorted({a for a, _ in pairs})
    idx = g.index(point_nodes)
    for start in range(0, len(sources), 64):
        batch = sources[start:start + 64]
        _, pred = g.dijkstra(idx[batch])
        for row, a in enumerate(batch):
            for x, b in pairs:
                if x == a:
                    path = g.path(pred[row], idx[a], idx[b])
                    if path:
                        out[(a, b)] = path
    return out


# --- C-NET-06 RSV ---------------------------------------------------------------------------------------------


def rsv_mask(lengths: np.ndarray, demand: np.ndarray, p: NetworkParams) -> np.ndarray:
    """Along an ordered route: runs with demand >= trigger, gaps up to gap_max_m bridged, kept if the run
    is at least min_route_length_km long."""
    lengths = np.asarray(lengths, dtype="float64")
    hi = np.nan_to_num(np.asarray(demand, dtype="float64"), nan=0.0) >= p.rsv_trigger
    runs = _runs(hi.tolist())
    for k in range(1, len(runs) - 1):
        s, e, v = runs[k]
        if not v and lengths[s:e].sum() <= p.rsv_gap_max_m:
            hi[s:e] = True
    out = np.zeros(len(hi), dtype=bool)
    for s, e, v in _runs(hi.tolist()):
        if v and lengths[s:e].sum() >= p.rsv_min_length_m:
            out[s:e] = True
    return out


# --- C-NET-07 meshes ----------------------------------------------------------------------------------------------


def mesh_faces(lines: np.ndarray, barriers: np.ndarray, boundary) -> np.ndarray:
    """Faces of the network lines together with barrier lines and the boundary line, inside the boundary."""
    geoms = [g for g in list(lines) + list(barriers) if g is not None and not g.is_empty]
    geoms.append(shapely.boundary(boundary))
    merged = shapely.union_all(np.asarray(geoms, dtype=object))
    faces = shapely.get_parts(shapely.polygonize(shapely.get_parts(merged)))
    if len(faces) == 0:
        return faces
    return faces[shapely.within(shapely.point_on_surface(faces), boundary)]


def mesh_side(faces: np.ndarray, exclude: np.ndarray | None = None, only: np.ndarray | None = None) -> np.ndarray:
    """Side of the square with the face's area, without the area of the exclusion polygons (C-NET-07).
    only: mask of faces for which the exclusion is computed (the others keep their full area)."""
    faces = np.asarray(faces, dtype=object)
    area = shapely.area(faces).astype("float64")
    if exclude is not None and len(exclude) and len(faces):
        sel = np.flatnonzero(np.ones(len(faces), dtype=bool) if only is None else only)
        parts = shapely.get_parts(shapely.union_all(np.asarray(exclude, dtype=object)))
        fi, pi = shapely.STRtree(parts).query(faces[sel], predicate="intersects")
        if len(fi):
            cut = shapely.area(shapely.intersection(faces[sel][fi], parts[pi]))
            np.subtract.at(area, sel[fi], cut)
    return np.sqrt(np.maximum(area, 0.0))


# --- C-NET-08 densification -------------------------------------------------------------------------------------------


def split_face(sub: Graph, seed_edge: int, seed_u: int, seed_v: int, target_nodes: np.ndarray) -> list[int] | None:
    """Route through the seed edge between two different network nodes: cheapest path from one seed end to a
    target node, then from the other end to another target without touching the first path (so the route
    crosses the face instead of doubling back). Tries both ends first; ordered from the first target to the second."""
    for a, b in ((seed_u, seed_v), (seed_v, seed_u)):
        tgt = sub.index(target_nodes)
        tgt = tgt[tgt >= 0]
        sa, sb = sub.index(np.array([a, b]))
        if len(tgt) < 2 or sa < 0 or sb < 0:
            return None
        dist, pred = sub.dijkstra([sa])
        da = dist[0, tgt]
        if not np.isfinite(da).any():
            continue
        t1 = int(tgt[np.argmin(da)])
        p1 = sub.path(pred[0], sa, t1)
        used = {x for e in p1 for x in sub.ends(e)} | {int(sub.nodes[sa])}
        if int(b) in used:
            continue
        rest = sub.without_nodes(np.array(sorted(used)))
        tb = rest.index(np.array([b]))[0]
        tgt2 = rest.index(np.setdiff1d(target_nodes, list(used)))
        tgt2 = tgt2[tgt2 >= 0]
        if tb < 0 or len(tgt2) == 0:
            continue
        dist2, pred2 = rest.dijkstra([tb])
        db = dist2[0, tgt2]
        if not np.isfinite(db).any():
            continue
        t2 = int(tgt2[np.argmin(db)])
        p2 = rest.path(pred2[0], tb, t2)
        if p2 is None:
            continue
        return [int(e) for e in [*p1[::-1], seed_edge, *p2]]
    return _disjoint_split(sub, seed_edge, seed_u, seed_v, target_nodes)


def _disjoint_split(sub: Graph, seed_edge: int, seed_u: int, seed_v: int, target_nodes: np.ndarray) -> list[int] | None:
    """Fallback of split_face when the cheapest first half blocks the second: two node-disjoint paths from the
    seed ends to the targets (max flow, fewest edges), if they exist."""
    import networkx as nx

    g = nx.Graph()
    g.add_edges_from((int(u), int(v)) for u, v, e in zip(sub._u, sub._v, sub._e) if e != seed_edge)
    if seed_u not in g or seed_v not in g:
        return None
    g.add_edges_from((("src", int(seed_u)), ("src", int(seed_v))))
    g.add_edges_from(("dst", int(n)) for n in target_nodes if int(n) in g and int(n) not in (seed_u, seed_v))
    for n in (seed_u, seed_v):  # a seed end on the ring is a target itself
        if int(n) in set(int(x) for x in target_nodes):
            g.add_edge("dst", int(n))
    if "dst" not in g:
        return None
    paths = list(nx.node_disjoint_paths(g, "src", "dst", cutoff=2))
    if len(paths) < 2:
        return None
    halves = {}
    for path in paths:
        nodes = path[1:-1]
        halves[nodes[0]] = [sub.edge_between(*sub.index(np.array([a, b]))) for a, b in zip(nodes[:-1], nodes[1:])]
    if set(halves) != {int(seed_u), int(seed_v)}:
        return None
    return [int(e) for e in [*halves[int(seed_u)][::-1], seed_edge, *halves[int(seed_v)]]]


@dataclass
class DensifyResult:
    net_mask: np.ndarray
    routes: list = field(default_factory=list)
    gaps: list = field(default_factory=list)      # dicts: geometry, side_m, reason
    rounds: list = field(default_factory=list)    # dicts: round, faces_over, routes_added
    skipped_faces: int = 0


def _face_key(face) -> tuple:
    c = shapely.centroid(face)
    return round(shapely.area(face)), round(c.x), round(c.y)


@dataclass
class MeshLimit:
    """Largest allowed mesh side (C-NET-07). Without a reference density it is mesh_m.max everywhere; with one,
    mesh_m.max x sqrt(reference / residents per km² of the face), never below mesh_m.max (density_scaling)."""
    base: float
    pop_xy: np.ndarray | None = None
    pop: np.ndarray | None = None
    ref_density: float | None = None

    def limits(self, faces: np.ndarray, sides: np.ndarray) -> np.ndarray:
        out = np.full(len(faces), self.base, dtype="float64")
        if self.ref_density is None or len(faces) == 0:
            return out
        residents = np.zeros(len(faces))
        if self.pop is not None and len(self.pop):
            fi, pi = shapely.STRtree(shapely.points(self.pop_xy)).query(np.asarray(faces, dtype=object), predicate="contains")
            np.add.at(residents, fi, self.pop[pi])
        density = residents / np.maximum(np.asarray(sides, dtype="float64") ** 2, 1.0) * 1e6
        with np.errstate(divide="ignore"):
            scaled = self.base * np.sqrt(self.ref_density / density)
        return np.maximum(scaled, self.base)


def as_limit(max_side) -> MeshLimit:
    return max_side if isinstance(max_side, MeshLimit) else MeshLimit(float(max_side))


def face_limits(faces, sides, max_side) -> np.ndarray:
    """Allowed side per face; faces at or below mesh_m.max keep it (no density needed)."""
    lim = as_limit(max_side)
    out = np.full(len(faces), lim.base, dtype="float64")
    cand = np.asarray(sides) > lim.base
    if cand.any():
        out[cand] = lim.limits(np.asarray(faces, dtype=object)[cand], np.asarray(sides)[cand])
    return out


def oversized_faces(inp: DesignInputs, net_mask, max_side, barriers, boundary, exclude, skip_area):
    """Faces of the network with side > their limit (C-NET-07; max_side is a number or a MeshLimit):
    (faces, sides, skipped, limits); skipped = faces over the limit in skip_area (rural districts)."""
    faces = mesh_faces(inp.geom[net_mask], barriers, boundary)
    raw = np.sqrt(shapely.area(faces)) if len(faces) else np.array([])
    cand = raw > as_limit(max_side).base
    side = mesh_side(faces, exclude, only=cand) if exclude is not None else raw
    limit = face_limits(faces, side, max_side)
    over = side > limit
    skipped = 0
    if skip_area is not None and over.any():
        rural = shapely.within(shapely.point_on_surface(faces), skip_area)
        skipped = int((over & rural).sum())
        over &= ~rural
    return faces[over], side[over], skipped, limit[over]


BOUNDARY_TOL_M = 0.5  # a network node lies on a face's outer ring within this distance (geometry, not a rule)


def boundary_nodes(face, node_tree: shapely.STRtree, node_ids: np.ndarray) -> np.ndarray:
    """Network nodes on the outer ring of the face. Dead-end branches inside the face and islands (holes) are
    excluded: a route to them would not split the face."""
    return node_ids[node_tree.query(shapely.get_exterior_ring(face), predicate="dwithin", distance=BOUNDARY_TOL_M)]


def ring_connected(inp: DesignInputs, inside: np.ndarray, cand: np.ndarray, ring_nodes: np.ndarray) -> np.ndarray:
    """Mask over cand: edges in a biconnected component of the face network (outer-ring nodes joined to one
    virtual node) that contains the ring. Only from these edges two separate ways lead to two ring nodes
    (Menger); dead ends and loops hanging off a single junction cannot start a split."""
    import networkx as nx

    g = nx.Graph()
    g.add_edges_from((int(inp.node_u[e]), int(inp.node_v[e])) for e in inside)
    ring = "ring"
    g.add_edges_from((ring, int(n)) for n in ring_nodes if int(n) in g)
    if ring not in g:
        return np.zeros(len(cand), dtype=bool)
    ok = set()
    for comp in nx.biconnected_component_edges(g):
        comp = list(comp)
        if any(ring in e for e in comp):
            ok |= {frozenset(e) for e in comp if ring not in e}
    return np.array([frozenset((int(inp.node_u[e]), int(inp.node_v[e]))) in ok for e in cand], dtype=bool)


def _split_one(inp: DesignInputs, face, net: np.ndarray, blocked: np.ndarray, nodes: np.ndarray, p: NetworkParams):
    """Route splitting one face, or the gap reason. Start edges from the core of the face (C-NET-08: depth from
    the outer ring >= seed_core_share x largest depth) by demand (highest first), then depth; if none of them
    splits the face, from the rest of it."""
    inside = inp.mid_tree.query(face, predicate="contains")
    inside = inside[inp.routable[inside] & ~blocked[inside]]
    interior = inside[~net[inside]]  # new edges; network branches inside the face may carry the route too
    if len(interior) == 0:
        return GAP_NO_CANDIDATES
    sub = Graph(inp.node_u[inside], inp.node_v[inside], inp.cost[inside], inside)
    # only edges in a part of the face's network that reaches at least two outer-ring nodes can split it
    _, lab = connected_components(sub.matrix, directed=False)
    tgt = sub.index(nodes)
    tgt_lab = lab[tgt[tgt >= 0]]
    labs, n_tgt = np.unique(tgt_lab, return_counts=True)
    ok_lab = labs[n_tgt >= 2]
    if len(ok_lab) == 0:
        return GAP_NOT_DIVISIBLE
    interior = interior[np.isin(lab[sub.index(inp.node_u[interior])], ok_lab)]
    interior = interior[ring_connected(inp, inside, interior, nodes)]
    if len(interior) == 0:
        return GAP_NOT_DIVISIBLE
    depth = shapely.distance(inp.mid[interior], shapely.get_exterior_ring(face))
    core = depth >= p.seed_core_share * depth.max()
    for group in (core, ~core):  # core first; if no core edge splits the face, the rest of it
        cand = interior[group]
        for seed in cand[np.lexsort((-depth[group], -inp.demand[cand]))][:SEED_TRIES]:
            r = split_face(sub, int(seed), int(inp.node_u[seed]), int(inp.node_v[seed]), nodes)
            if r is not None and inp.length[r].sum() >= p.min_split_route_m:
                return r
    return GAP_NOT_DIVISIBLE


def densify(inp: DesignInputs, net_mask: np.ndarray, max_side: float, barriers, boundary, exclude, skip_area,
            p: NetworkParams, blocked: np.ndarray | None = None) -> DensifyResult:
    """C-NET-08: split meshes larger than max_side until none is too large, none can be split or max_rounds."""
    net = np.asarray(net_mask, dtype=bool).copy()
    blocked = np.zeros(len(net), dtype=bool) if blocked is None else blocked
    res = DensifyResult(net)
    failed: dict[tuple, str] = {}
    for rnd in range(1, p.max_rounds + 1):
        faces, _, _, _ = oversized_faces(inp, net, max_side, barriers, boundary, exclude, skip_area)
        if len(faces) == 0:
            break
        net_ids = inp.net_nodes(net)
        pos = np.searchsorted(inp.node_ids, net_ids)
        node_tree = shapely.STRtree(shapely.points(inp.node_xy[pos]))
        new = np.zeros(len(net), dtype=bool)
        added = 0
        for face in faces:
            key = _face_key(face)
            if key in failed:
                continue
            route = _split_one(inp, face, net | new, blocked, boundary_nodes(face, node_tree, net_ids), p)
            if isinstance(route, str):
                failed[key] = route
                continue
            new[route] = True
            res.routes.append(route)
            added += 1
        res.rounds.append({"round": rnd, "faces_over": len(faces), "routes_added": added})
        if added == 0:
            break
        net |= new
    faces, sides, res.skipped_faces, limits = oversized_faces(inp, net, max_side, barriers, boundary, exclude, skip_area)
    for face, side, lim in zip(faces, sides, limits):
        res.gaps.append({"geometry": face, "side_m": float(side), "max_m": float(lim),
                         "reason": failed.get(_face_key(face), GAP_MAX_ROUNDS)})
    res.net_mask = net
    return res


# --- C-NET-09 binding of schools and local shops ------------------------------------------------------------------------


def nearest_nodes(inp: DesignInputs, g: Graph, xy: np.ndarray) -> np.ndarray:
    """Nearest node of graph g for each point (node ids)."""
    in_g = g.index(inp.node_ids) >= 0
    ids, pts = inp.node_ids[in_g], inp.node_xy[in_g]
    _, j = cKDTree(pts).query(np.asarray(xy, dtype="float64"))
    return ids[j]


def attach_points(g: Graph, inp: DesignInputs, net_mask: np.ndarray, xy: np.ndarray, radius_m: float) -> list[list[int]]:
    """Cheapest path from the graph node nearest to each point farther than radius_m from the network to the
    network (ordered from the point to the network). Points already connected by an earlier path are skipped."""
    net = np.asarray(net_mask, dtype=bool).copy()
    xy = np.asarray(xy, dtype="float64")
    if len(xy) == 0 or not net.any():
        return []
    pts = shapely.points(xy)
    near = np.zeros(len(xy), dtype=bool)
    pi, ei = inp.geom_tree.query(pts, predicate="dwithin", distance=radius_m)
    near[np.unique(pi[net[ei]])] = True
    far = np.flatnonzero(~near)
    if len(far) == 0:
        return []
    src = g.index(inp.net_nodes(net))
    src = src[src >= 0]
    dist, pred, source = dijkstra(g.matrix, directed=True, indices=src, return_predecessors=True, min_only=True)
    starts = g.index(nearest_nodes(inp, g, xy[far]))
    routes, done = [], set()
    for t in starts:
        if t < 0 or t in done or not np.isfinite(dist[t]):
            continue
        done.add(t)
        path = g.path(pred, int(source[t]), int(t))
        if path:
            routes.append(path[::-1])
    return routes


# --- C-NET-10 parallel rule P-ATT-03 ----------------------------------------------------------------------------------------


def high_volume_runs(high: np.ndarray, lengths: np.ndarray, min_run_m: float) -> list[tuple[int, int]]:
    """Runs (start, stop) of consecutive high-volume edges along a route that are at least min_run_m long."""
    return [(s, e) for s, e, v in _runs(np.asarray(high, dtype=bool).tolist())
            if v and np.asarray(lengths)[s:e].sum() >= min_run_m]


@dataclass
class Alternative:
    accepted: bool
    edges: list
    detour: float
    run_m: float
    alt_m: float
    on_main_m: float = float("nan")


def parallel_alternative(inp: DesignInputs, run: list[int], start_node: int, end_node: int, high: np.ndarray,
                         buffer_m: float, detour_max: float, max_on_main_m: float) -> Alternative:
    """C-NET-10: cheapest path from start to end node over edges with their middle in the buffer around the run,
    high-volume edges only where unavoidable (cost x MAIN_PENALTY). Accepted if at most max_on_main_m of it lie
    on high-volume edges and its length / run length <= detour_max (P-DIR-01)."""
    run_m = float(inp.length[run].sum())
    none = Alternative(False, [], float("inf"), run_m, float("nan"))
    zone = shapely.buffer(shapely.union_all(inp.geom[run]), buffer_m)
    cand = inp.mid_tree.query(zone, predicate="contains")
    cand = cand[inp.routable[cand]]
    if len(cand) == 0:
        return none
    cost = inp.cost[cand] * np.where(high[cand], MAIN_PENALTY, 1.0)
    sub = Graph(inp.node_u[cand], inp.node_v[cand], cost, cand)
    s, t = sub.index(np.array([start_node, end_node]))
    if s < 0 or t < 0:
        return none
    _, pred = sub.dijkstra([s])
    path = sub.path(pred[0], s, t)
    if not path:
        return none
    alt_m = float(inp.length[path].sum())
    on_main = float(inp.length[path][high[path]].sum())
    detour = alt_m / run_m if run_m > 0 else float("inf")
    return Alternative(detour <= detour_max and on_main <= max_on_main_m, path, detour, run_m, alt_m, on_main)


# --- C-NET-11 continuity --------------------------------------------------------------------------------------------------


def smooth_sequence(ranks: np.ndarray, lengths: np.ndarray, locked: np.ndarray, max_gap_m: float) -> tuple[np.ndarray, int]:
    """Raise lower runs between two runs of the same higher category up to max_gap_m (not locked edges);
    returns the new ranks and the number of category changes left along the route."""
    ranks = np.asarray(ranks).copy()
    lengths = np.asarray(lengths, dtype="float64")
    locked = np.asarray(locked, dtype=bool)
    changed = True
    while changed:
        changed = False
        runs = _runs(ranks.tolist())
        for k in range(1, len(runs) - 1):
            (_, _, a), (s, e, b), (_, _, c) = runs[k - 1], runs[k], runs[k + 1]
            if a == c and b < a and lengths[s:e].sum() <= max_gap_m and not locked[s:e].any():
                ranks[s:e] = a
                changed = True
                break
    return ranks, len(_runs(ranks.tolist())) - 1


# --- ids and traces ---------------------------------------------------------------------------------------------------------


def route_id(kind: str, edge_ids) -> str:
    """Stable route id: hash of the route kind and its sorted edge ids."""
    key = kind + ":" + ",".join(sorted(set(edge_ids)))
    return "rt_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def trace_json(steps: list[dict]) -> str:
    return json.dumps(steps, ensure_ascii=False, default=float)
