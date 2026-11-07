"""pipeline/lib/parallel.py: parallel map with results in input order (same output as a serial run)."""

import numpy as np
import pytest

from pipeline.lib import parallel


def test_pmap_matches_serial_and_keeps_order(monkeypatch):
    data = np.arange(50)
    offset = 7  # closure state is inherited by the forked workers

    def task(i):
        return int(data[i] * data[i] + offset)

    monkeypatch.setenv("SFP_WORKERS", "4")
    par = parallel.pmap(task, len(data))
    monkeypatch.setenv("SFP_WORKERS", "1")
    ser = parallel.pmap(task, len(data))
    assert par == ser == [int(x * x + offset) for x in data]


def test_workers_from_env_and_bounded(monkeypatch):
    monkeypatch.setenv("SFP_WORKERS", "3")
    assert parallel.workers(10) == 3
    assert parallel.workers(2) == 2
    assert parallel.workers(0) == 1
    monkeypatch.delenv("SFP_WORKERS")
    assert parallel.workers(1000) >= 1


def test_nested_pmap_runs_serially_inside_a_worker(monkeypatch):
    monkeypatch.setenv("SFP_WORKERS", "2")

    def inner(i):
        return parallel.in_worker()

    def outer(i):
        return parallel.pmap(inner, 2)

    assert parallel.pmap(outer, 2) == [[True, True], [True, True]]


def test_progress_called_once_per_item(monkeypatch):
    monkeypatch.setenv("SFP_WORKERS", "2")
    seen = []
    parallel.pmap(lambda i: i, 5, progress=seen.append)
    assert seen == list(range(5))


def test_worker_error_is_raised(monkeypatch):
    monkeypatch.setenv("SFP_WORKERS", "2")

    def task(i):
        if i == 3:
            raise ValueError("boom")
        return i

    with pytest.raises(ValueError, match="boom"):
        parallel.pmap(task, 5)
