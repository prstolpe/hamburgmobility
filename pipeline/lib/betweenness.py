"""Edge betweenness on the segment graph (rule S-FEAT-02)."""

import igraph
import numpy as np


def edge_betweenness(node_u: np.ndarray, node_v: np.ndarray, weight: np.ndarray,
                     sources: list[int] | None = None) -> np.ndarray:
    """Undirected, weighted edge betweenness per edge (u[i], v[i]); unordered node pairs count once.

    Edges with NaN weight are not part of the graph and get NaN. sources: optional node ids for a
    sampled estimate (None = exact).
    """
    weight = np.asarray(weight, dtype="float64")
    keep = ~np.isnan(weight)
    nodes = np.unique(np.concatenate([node_u[keep], node_v[keep]]))
    index = {n: i for i, n in enumerate(nodes.tolist())}
    edges = [(index[u], index[v]) for u, v in zip(node_u[keep].tolist(), node_v[keep].tolist())]
    graph = igraph.Graph(n=len(nodes), edges=edges, directed=False)
    src = None if sources is None else [index[s] for s in sources if s in index]
    values = graph.edge_betweenness(directed=False, weights=weight[keep].tolist(), sources=src)
    out = np.full(len(weight), np.nan)
    out[keep] = values
    return out
