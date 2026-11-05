"""Provenance check for the cycling and design rule files.

source / source_type / status may sit on any entry and apply to everything below it
(e.g. widths_m.de.source_type covers widths_m.de.separated_oneway.standard).
An entry needs an effective source_type when it is a rule (has an `id`) or holds a number;
a source is required unless the source_type is 'assumption'. Rules need a status.
"""

from typing import Any

from config.schema.rules_model import SourceType, Status

# Keys that describe an entry instead of holding a value.
META_KEYS = {"source", "source_type", "status", "note", "unit", "description", "label_de", "nl", "url", "title"}


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _holds_number(x: Any) -> bool:
    if _is_number(x):
        return True
    return isinstance(x, list) and any(_holds_number(v) for v in x)


def _as_list(source: Any) -> list[str]:
    if source is None:
        return []
    return [source] if isinstance(source, str) else list(source)


def check_provenance(node: Any, path: str, source_ids: set[str], source_type: str | None = None,
                     sources: tuple[str, ...] = ()) -> None:
    """Raise ValueError at the first entry without valid provenance."""
    if isinstance(node, list):
        for i, item in enumerate(node):
            check_provenance(item, f"{path}[{i}]", source_ids, source_type, sources)
        return
    if not isinstance(node, dict):
        return

    own = _as_list(node.get("source"))
    unknown = [s for s in own if s not in source_ids]
    if unknown:
        raise ValueError(f"{path}: unknown source reference(s) {unknown}")
    if "source_type" in node:
        source_type = node["source_type"]
        if source_type not in SourceType.__args__:
            raise ValueError(f"{path}: invalid source_type {source_type!r}")
    if own:
        sources = tuple(own)

    holds_number = any(_holds_number(v) for k, v in node.items() if k not in META_KEYS)
    if "id" in node or holds_number:
        if source_type is None:
            raise ValueError(f"{path}: source_type missing (on the entry or a parent entry)")
        if source_type != "assumption" and not sources:
            raise ValueError(f"{path}: source missing (required unless source_type is assumption)")
    if "id" in node and node.get("status") not in Status.__args__:
        raise ValueError(f"{path} ({node['id']}): status missing or invalid ({node.get('status')!r})")

    for key, val in node.items():
        if key not in META_KEYS:
            check_provenance(val, f"{path}.{key}", source_ids, source_type, sources)


def collect_ids(node: Any) -> list[str]:
    """All rule ids in a nested structure, in document order."""
    if isinstance(node, list):
        return [i for item in node for i in collect_ids(item)]
    if not isinstance(node, dict):
        return []
    ids = [node["id"]] if "id" in node else []
    return ids + [i for k, v in node.items() if k != "id" for i in collect_ids(v)]
