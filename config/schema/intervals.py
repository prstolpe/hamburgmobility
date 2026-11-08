"""Half-open interval convention for class tables (review 2026-11, structural recommendation 4, F27).

Every class covers [min, max): a value equal to a boundary belongs to the upper class. A missing min is -inf,
a missing max is +inf. A class table must be free of gaps and overlaps; the schemas call check_class_table for
rules.yaml feasibility_classes and cycling_rules.yaml demand.intensity_classes_peak_h.
"""

import math
from collections.abc import Iterable


def _lo(x: float | None) -> float:
    return -math.inf if x is None else float(x)


def _hi(x: float | None) -> float:
    return math.inf if x is None else float(x)


def check_class_table(classes: Iterable[tuple[str, float | None, float | None]], path: str) -> None:
    """Raise ValueError if the classes (name, min, max) overlap, leave a gap or have min >= max."""
    rows = sorted(((name, _lo(lo), _hi(hi)) for name, lo, hi in classes), key=lambda r: r[1])
    if not rows:
        raise ValueError(f"{path}: empty class table")
    for name, lo, hi in rows:
        if lo >= hi:
            raise ValueError(f"{path}.{name}: min must be below max ([min, max))")
    for (n1, _, hi1), (n2, lo2, _) in zip(rows, rows[1:]):
        if hi1 > lo2:
            raise ValueError(f"{path}: classes {n1} and {n2} overlap ([min, max))")
        if hi1 < lo2:
            raise ValueError(f"{path}: gap between classes {n1} and {n2} ([min, max))")


def in_class(value: float, lo: float | None, hi: float | None) -> bool:
    """value in [lo, hi)."""
    return _lo(lo) <= value < _hi(hi)
