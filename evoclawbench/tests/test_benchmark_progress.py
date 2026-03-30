"""Tests for scripts/benchmark_progress.py."""

import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from benchmark_progress import BenchmarkBatchProgress, shorten_str


@pytest.fixture
def manager():
    return BenchmarkBatchProgress(num_instances=5)


@pytest.mark.parametrize(
    ("text", "max_len", "shorten_left", "expected"),
    [
        ("hello", 10, False, "hello     "),
        ("hello world", 8, False, "hello..."),
        ("hello world", 8, True, "...world"),
        ("hello", 5, False, "hello"),
        ("hi", 5, False, "hi   "),
    ],
)
def test_shorten_str(text, max_len, shorten_left, expected):
    assert shorten_str(text, max_len, shorten_left) == expected


def test_manager_initialization(manager):
    assert manager.n_completed == 0
    assert manager.instances_by_exit_status == {}


def test_instance_lifecycle(manager):
    manager.on_instance_start("task_1")
    assert "task_1" in manager._spinner_tasks
    assert manager.n_completed == 0

    manager.on_instance_end("task_1", "success", 0.0)
    assert manager.n_completed == 1
    assert manager.instances_by_exit_status["success"] == ["task_1"]


@pytest.mark.parametrize(
    "statuses",
    [
        ["success", "failed", "success", "timeout"],
        ["error", "error", "error"],
        ["success"] * 5,
    ],
)
def test_multiple_instances(manager, statuses):
    for i, status in enumerate(statuses, 1):
        instance_id = f"task_{i}"
        manager.on_instance_start(instance_id)
        manager.on_instance_end(instance_id, status, 0.0)

    assert manager.n_completed == len(statuses)
    for status in set(statuses):
        expected_count = statuses.count(status)
        assert len(manager.instances_by_exit_status[status]) == expected_count


def test_uncaught_exception(manager):
    manager.on_instance_start("task_1")
    manager.on_uncaught_exception("task_1", ValueError("test error"))

    assert manager.n_completed == 1
    assert "Uncaught ValueError" in manager.instances_by_exit_status


def test_update_instance_status(manager):
    manager.on_instance_start("task_1")
    manager.update_instance_status("task_1", "Processing files...")


def test_cost_accumulation(manager):
    manager.on_instance_start("a")
    manager.on_instance_end("a", "success", 1.25)
    assert manager.total_cost_usd == pytest.approx(1.25)

    manager.on_instance_start("b")
    manager.on_instance_end("b", "success", 0.75)
    assert manager.total_cost_usd == pytest.approx(2.0)


def test_eta_empty_until_one_complete(manager):
    manager.on_instance_start("task_1")
    assert manager.eta_text() == ""

    manager.on_instance_end("task_1", "success", 0.0)
    assert manager.eta_text().startswith("eta:")


def test_eta_after_partial_progress():
    m = BenchmarkBatchProgress(num_instances=10)
    m.on_instance_start("x")
    time.sleep(0.05)
    m.on_instance_end("x", "success", 0.0)
    eta = m.eta_text()
    assert eta.startswith("eta:")


def test_concurrent_operations():
    mgr = BenchmarkBatchProgress(num_instances=10)
    instance_ids = [f"task_{i}" for i in range(10)]
    statuses = ["success", "failed", "timeout"] * 4
    statuses = statuses[:10]

    def work(i: int):
        instance_id = instance_ids[i]
        mgr.on_instance_start(instance_id)
        mgr.update_instance_status(instance_id, f"step {i}")
        mgr.on_instance_end(instance_id, statuses[i], 0.01 * i)

    threads = [threading.Thread(target=work, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert mgr.n_completed == 10
    assert sum(len(v) for v in mgr.instances_by_exit_status.values()) == 10


def test_print_report(manager, capsys):
    manager.on_instance_start("task_1")
    manager.on_instance_end("task_1", "success", 0.0)
    manager.on_instance_start("task_2")
    manager.on_instance_end("task_2", "failed", 0.0)

    manager.print_report()

    captured = capsys.readouterr()
    assert "success: 1" in captured.out
    assert "failed: 1" in captured.out
    assert "task_1" in captured.out
    assert "task_2" in captured.out
