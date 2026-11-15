"""Junction arm filter (design_rules J-M-01, redesign 2026-11 package 5).

A node cluster is a junction only if it has at least `min_arms` arms after the directional carriageways are merged
(J-M-02 arm_merge), or if a standalone cycle path meets it. Other clusters are pseudo-junctions, typically points where
a street splits into two carriageways. A pseudo-junction within `pseudo_join_m` of a member node of a real junction
that one of its streets meets joins that junction (the nearest one; its node_id stays). Otherwise it is dropped.
"""

from dataclasses import dataclass

from shapely import STRtree

from pipeline.lib.junctions import CYCLE_PATH


@dataclass(frozen=True)
class FilterParams:
    min_arms: int
    join_m: float

    @classmethod
    def from_rule(cls, m01: dict) -> "FilterParams":
        return cls(min_arms=int(m01["min_arms"]["value"]), join_m=float(m01["pseudo_join_m"]["value"]))


def is_real(d: dict, min_arms: int) -> bool:
    """d: describe_legs entry of one cluster (legs, arms)."""
    return len(d["arms"]) >= min_arms or any(leg["cat"] == CYCLE_PATH for leg in d["legs"])


def _names(d: dict) -> set:
    return {leg["name"] for leg in d["legs"] if leg.get("name")}


def filter_pseudo(clusters: dict, legs: dict, pts: dict, p: FilterParams) -> tuple[dict, dict]:
    """-> ({root: members} of the real junctions with joined pseudo nodes, {"joined": [roots], "dropped": [roots]})."""
    real = [r for r in clusters if is_real(legs[r], p.min_arms)]
    pseudo = [r for r in clusters if r not in set(real)]
    out = {r: list(clusters[r]) for r in real}
    nodes = [(n, r) for r in real for n in clusters[r]]
    tree = STRtree([pts[n] for n, _ in nodes]) if nodes else None
    real_names = {r: _names(legs[r]) for r in real}
    joined, dropped = [], []
    for r in sorted(pseudo):
        names = _names(legs[r])
        best = None
        if tree is not None and names:
            for n in clusters[r]:
                for i in tree.query(pts[n].buffer(p.join_m)):
                    node, root = nodes[int(i)]
                    d = pts[n].distance(pts[node])
                    if d <= p.join_m and names & real_names[root] and (best is None or (d, root) < best):
                        best = (d, root)
        if best is None:
            dropped.append(r)
        else:
            out[best[1]] += clusters[r]
            joined.append(r)
    return {r: sorted(m) for r, m in out.items()}, {"joined": joined, "dropped": dropped}
