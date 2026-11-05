"""Road network segmentation (guide 3.2 Stufe 2).

Input is a table of node-to-node edges (one row per pair of consecutive OSM nodes of a way).
Edges are merged into chains between segment ends (degree != 2 or a change of one of the
`differ` attributes); long chains are split where `split_attribute` changes. Each segment gets a
stable ID from its OSM way IDs and the rounded coordinates of its end nodes.
"""

import hashlib
import math
from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass

import geopandas as gpd
import networkx as nx
import pandas as pd
from pyproj import CRS
from shapely.geometry import LineString

from pipeline.lib.crs import WORK_CRS

ID_PREFIX = "seg_"
ID_HEX_LENGTH = 16
NAME_SEPARATOR = " / "


class DuplicateSegmentIdError(RuntimeError):
    """Two segments got the same ID; IDs are never renumbered, so the run stops."""


@dataclass
class _Chain:
    nodes: list[int]   # node ids along the chain, len(edges) + 1
    edges: list[int]   # row positions in the edge table, in walking order
    split: bool = False


def _round_m(value: float) -> int:
    """Round half up to 1 m (no banker's rounding, so the result does not depend on parity)."""
    return math.floor(value + 0.5)


def _rounded(points: Iterable[Sequence[float]]) -> list[tuple[int, int]]:
    return [(_round_m(x), _round_m(y)) for x, y, *_ in points]


def segment_id(way_ids: Iterable[int], end_coords: Iterable[Sequence[float]],
               path_coords: Sequence[Sequence[float]] | None = None, prefix: str = ID_PREFIX) -> str:
    """Stable ID: hash of sorted unique way IDs and sorted end coordinates rounded to 1 m.

    path_coords (all node coordinates in walking order) is only added for segments whose ways and
    end nodes are identical, e.g. the two arcs of a roundabout mapped as one closed way.
    """
    ways = ",".join(str(w) for w in sorted({int(w) for w in way_ids}))
    ends = ";".join(f"{x},{y}" for x, y in sorted(_rounded(end_coords)))
    key = f"{ways}|{ends}"
    if path_coords is not None:
        path = _rounded(path_coords)
        path = min(path, path[::-1])  # independent of walking direction
        key += "|" + ";".join(f"{x},{y}" for x, y in path)
    return prefix + hashlib.sha1(key.encode("utf-8")).hexdigest()[:ID_HEX_LENGTH]


def _check_crs(edges: gpd.GeoDataFrame) -> None:
    if edges.crs is None:
        raise ValueError("edges have no CRS; set it explicitly (expected EPSG:25832)")
    if CRS.from_user_input(edges.crs) != CRS.from_user_input(WORK_CRS):
        raise ValueError(f"edges must be in {WORK_CRS} (got {edges.crs}); use to_work_crs() first")


def _is_known(value) -> bool:
    return value is not None and value == value and str(value).strip() != ""


def _norm(value):
    return str(value).strip() if _is_known(value) else None


def _walk_chains(graph: nx.MultiGraph, is_end: dict[Hashable, bool]) -> list[_Chain]:
    visited: set[int] = set()
    chains: list[_Chain] = []

    def incident(node) -> list[tuple[int, int]]:
        return sorted((key, nbr) for nbr, keys in graph[node].items() for key in keys)

    def walk(start, key: int, nbr) -> _Chain:
        chain = _Chain(nodes=[start], edges=[key])
        visited.add(key)
        current = nbr
        while not is_end[current]:
            nxt = [(k, o) for k, o in incident(current) if k not in visited]
            if not nxt:
                break
            k, o = nxt[0]
            chain.nodes.append(current)
            chain.edges.append(k)
            visited.add(k)
            current = o
        chain.nodes.append(current)
        return chain

    for node in sorted(n for n, end in is_end.items() if end):
        for key, nbr in incident(node):
            if key not in visited:
                chains.append(walk(node, key, nbr))
    # What is left are closed rings without any segment end; start them at the smallest node id.
    for key in sorted(k for _, _, k in graph.edges(keys=True)):
        if key in visited:
            continue
        start = min(nx.node_connected_component(graph, graph.graph["edge_nodes"][key][0]))
        is_end[start] = True
        first = next((k, o) for k, o in incident(start) if k not in visited)
        chains.append(walk(start, *first))
    return chains


def _split_long(chain: _Chain, values: list, lengths: list[float], min_length_m: float) -> list[_Chain]:
    """Cut before every edge whose known value differs from the last known value."""
    if sum(lengths[k] for k in chain.edges) <= min_length_m:
        return [chain]
    cuts, last_known = [], None
    for pos, key in enumerate(chain.edges):
        value = values[key]
        if value is None:
            continue
        if last_known is not None and value != last_known:
            cuts.append(pos)
        last_known = value
    if not cuts:
        return [chain]
    pieces, bounds = [], [0, *cuts, len(chain.edges)]
    for a, b in zip(bounds, bounds[1:]):
        pieces.append(_Chain(nodes=chain.nodes[a:b + 1], edges=chain.edges[a:b], split=True))
    return pieces


def _unique_in_order(values: Iterable) -> list:
    seen, out = set(), []
    for v in values:
        if v is not None and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def segments_from_edges(edges: gpd.GeoDataFrame, differ: Sequence[str], split_attribute: str,
                        min_length_m: float, split_rule_id: str, prefix: str = ID_PREFIX,
                        return_members: bool = False) -> gpd.GeoDataFrame:
    """Merge node-to-node edges into segments.

    edges: columns u, v (node ids), way_id, name, the `differ` attributes, split_attribute and
    LineString geometry from u to v, in EPSG:25832.
    Returns one row per segment, sorted by segment_id. prefix: ID prefix (the cycle graph uses its
    own). return_members: add member_rows (row positions of `edges` in walking order from node_u)
    and member_forward (True where that edge runs u -> v in walking direction).
    """
    _check_crs(edges)
    e = edges.reset_index(drop=True)
    us, vs = e["u"].tolist(), e["v"].tolist()
    coords = [list(g.coords) for g in e.geometry]
    lengths = e.geometry.length.tolist()
    way_ids = [int(w) for w in e["way_id"]]
    names = [_norm(n) for n in e["name"]] if "name" in e else [None] * len(e)
    differ_values = {col: [_norm(x) for x in e[col]] for col in differ}
    split_values = [_norm(x) for x in e[split_attribute]]

    graph = nx.MultiGraph(edge_nodes={})
    node_xy: dict = {}
    for key, (u, v) in enumerate(zip(us, vs)):
        graph.add_edge(u, v, key=key)
        graph.graph["edge_nodes"][key] = (u, v)
        node_xy.setdefault(u, coords[key][0])
        node_xy.setdefault(v, coords[key][-1])

    is_end = {}
    for node in graph.nodes:
        keys = [k for nbr, ks in graph[node].items() for k in ks]
        if graph.degree(node) != 2 or graph.has_edge(node, node):
            is_end[node] = True
        else:
            is_end[node] = any(len({differ_values[c][k] for k in keys}) > 1 for c in differ)

    chains = []
    for chain in _walk_chains(graph, is_end):
        chains.extend(_split_long(chain, split_values, lengths, min_length_m))

    records = []
    for chain in chains:
        line: list = []
        for node, key in zip(chain.nodes, chain.edges):
            part = coords[key] if us[key] == node else coords[key][::-1]
            line.extend(part if not line else part[1:])
        record = {
            "osm_way_ids": _unique_in_order(way_ids[k] for k in chain.edges),
            "name": NAME_SEPARATOR.join(_unique_in_order(names[k] for k in chain.edges)) or None,
            "maxspeed_osm": NAME_SEPARATOR.join(_unique_in_order(split_values[k] for k in chain.edges)) or None,
            "node_u": chain.nodes[0],
            "node_v": chain.nodes[-1],
            "split_rule": split_rule_id if chain.split else None,
            "_path": [node_xy[n] for n in chain.nodes],
            "member_rows": list(chain.edges),
            "member_forward": [us[k] == node for node, k in zip(chain.nodes, chain.edges)],
            "geometry": LineString(line),
        }
        for col in differ:  # uniform by construction; longest value if differ is not enforced
            by_length: dict = {}
            for k in chain.edges:
                by_length[differ_values[col][k]] = by_length.get(differ_values[col][k], 0.0) + lengths[k]
            record[col] = max(by_length.items(), key=lambda kv: (kv[1], str(kv[0])))[0]
        records.append(record)

    seg = gpd.GeoDataFrame(records, geometry="geometry", crs=edges.crs)
    seg["length_m"] = seg.geometry.length
    seg = _assign_ids(seg, prefix)
    columns = ["segment_id", "osm_way_ids", *differ, "name", "maxspeed_osm", "length_m",
               "node_u", "node_v", "split_rule", "geometry"]
    if return_members:
        columns += ["member_rows", "member_forward"]
    return seg[columns].sort_values("segment_id").reset_index(drop=True)


def _assign_ids(seg: gpd.GeoDataFrame, prefix: str = ID_PREFIX) -> gpd.GeoDataFrame:
    ends = [[path[0], path[-1]] for path in seg["_path"]]
    ids = [segment_id(w, end, prefix=prefix) for w, end in zip(seg["osm_way_ids"], ends)]
    seen: dict[str, int] = {}
    for i in ids:
        seen[i] = seen.get(i, 0) + 1
    ids = [segment_id(w, end, path, prefix=prefix) if seen[i] > 1 else i
           for i, w, end, path in zip(ids, seg["osm_way_ids"], ends, seg["_path"])]
    duplicates = sorted({i for i in ids if ids.count(i) > 1}) if len(set(ids)) != len(ids) else []
    if duplicates:
        raise DuplicateSegmentIdError(f"{len(duplicates)} duplicate segment ids, e.g. {duplicates[:5]}")
    seg["segment_id"] = ids
    return seg.drop(columns="_path")


# --- S-NET-04 way selection ------------------------------------------------------------------


def _tags(v) -> dict:
    if isinstance(v, dict):
        return v
    if isinstance(v, str) and v:
        import json
        try:
            out = json.loads(v)
            return out if isinstance(out, dict) else {}
        except ValueError:
            return {}
    return {}


def _value(row: dict, key: str):
    v = row.get(key)
    if _is_known(v) and v != "":
        return v
    v = _tags(row.get("tags")).get(key)
    return v if _is_known(v) and v != "" else None


def select_ways(df: pd.DataFrame, rules) -> pd.Series:
    """True for ways in the network: highway_classes, plus the extra ways of S-NET-04 (named, filtered by tags)."""
    main = set(rules.network.highway_classes.values)
    extra = [r for r in rules.network.rules if r.include_highway]
    keep = []
    for row in df.to_dict("records"):
        hw = row.get("highway")
        if hw in main:
            keep.append(True)
            continue
        ok = False
        for r in extra:
            if hw not in r.include_highway:
                continue
            if r.require_name and not _value(row, "name"):
                break
            if hw == "service" and r.service_values is not None:
                svc = _value(row, "service")
                if svc is not None and svc not in r.service_values:
                    break
            if hw in r.motor_access_applies_to:
                access = next((v for v in (_value(row, k) for k in r.motor_access_keys) if v is not None), None)
                if access is not None and access not in r.motor_access_values:
                    break
            ok = True
            break
        keep.append(ok)
    return pd.Series(keep, index=df.index, dtype=bool)
