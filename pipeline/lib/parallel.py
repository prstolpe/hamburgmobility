"""Run independent tasks on several cores.

pmap(task, n) returns [task(0), ..., task(n-1)] in input order, so the output is identical to a serial run.
Workers are forked: they inherit the task (closures allowed) and all data already in memory, nothing is pickled
on the way in. Number of workers: environment variable SFP_WORKERS (default: all cores); SFP_WORKERS=1 runs serially.
A pmap inside a worker runs serially (no nested pools).

Python 3.12 warns when forking a process with threads (numpy/Arrow thread pools). Workers only run Python and
GEOS code, no file I/O; if a run ever hangs, SFP_WORKERS=1 is the safe fallback.
"""

import multiprocessing as mp
import os
import warnings
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from typing import Any

_TASK: Callable[[int], Any] | None = None
_IN_WORKER = False


def workers(n_items: int) -> int:
    env = os.environ.get("SFP_WORKERS")
    n = int(env) if env else (os.cpu_count() or 1)
    return max(1, min(n, n_items))


def in_worker() -> bool:
    return _IN_WORKER


def _run(i: int):
    global _IN_WORKER
    _IN_WORKER = True
    return _TASK(i)


def pmap(task: Callable[[int], Any], n_items: int, chunksize: int = 1,
         progress: Callable[[int], None] | None = None) -> list:
    global _TASK
    n = workers(n_items)
    if n == 1 or _IN_WORKER or "fork" not in mp.get_all_start_methods():
        out = []
        for i in range(n_items):
            out.append(task(i))
            if progress:
                progress(i)
        return out
    _TASK = task
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*use of fork\\(\\) may lead to deadlocks.*", category=DeprecationWarning)
            return _pool_map(n, n_items, chunksize, progress)
    finally:
        _TASK = None


def _pool_map(n: int, n_items: int, chunksize: int, progress) -> list:
    with ProcessPoolExecutor(n, mp_context=mp.get_context("fork")) as ex:
        out = []
        for i, r in enumerate(ex.map(_run, range(n_items), chunksize=chunksize)):
            out.append(r)
            if progress:
                progress(i)
        return out
