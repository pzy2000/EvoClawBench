"""Rich-based batch progress UI (mini-swe-agent style) for parallel benchmark runs."""

from __future__ import annotations

import collections
import time
from datetime import timedelta
from threading import Lock
from typing import Dict, List

from rich.console import Group
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table


def shorten_str(s: str, max_len: int, shorten_left: bool = False) -> str:
    if not shorten_left:
        s = s[: max_len - 3] + "..." if len(s) > max_len else s
    else:
        s = "..." + s[-max_len + 3 :] if len(s) > max_len else s
    return f"{s:<{max_len}}"


class BenchmarkBatchProgress:
    """Thread-safe progress display: overall bar, exit status table, active tasks."""

    def __init__(self, num_instances: int) -> None:
        self._spinner_tasks: Dict[str, TaskID] = {}
        self._lock = Lock()
        self._start_time = time.time()
        self._total_instances = num_instances
        self._total_cost_usd = 0.0
        self._instances_by_exit_status: Dict[str, List[str]] = collections.defaultdict(list)

        self._main_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("[progress.description]{task.description} (${task.fields[total_cost]})"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn("[cyan]{task.fields[eta]}[/cyan]"),
            speed_estimate_period=60 * 5,
        )
        self._task_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("{task.fields[instance_id]}"),
            TextColumn("{task.fields[status]}"),
            TimeElapsedColumn(),
        )

        self._main_task_id = self._main_progress_bar.add_task(
            "[cyan]Overall Progress", total=num_instances, total_cost="0.00", eta=""
        )

        placeholder_table = Table()
        self.render_group = Group(
            self._main_progress_bar,
            placeholder_table,
            self._task_progress_bar,
        )

    @property
    def n_completed(self) -> int:
        with self._lock:
            return sum(len(instances) for instances in self._instances_by_exit_status.values())

    @property
    def instances_by_exit_status(self) -> Dict[str, List[str]]:
        with self._lock:
            return {k: list(v) for k, v in self._instances_by_exit_status.items()}

    @property
    def total_cost_usd(self) -> float:
        with self._lock:
            return self._total_cost_usd

    def eta_text(self) -> str:
        """Estimated time remaining (empty until at least one instance completes)."""
        with self._lock:
            return self._get_eta_text_unlocked()

    def _get_eta_text_unlocked(self) -> str:
        n_done = sum(len(instances) for instances in self._instances_by_exit_status.values())
        try:
            elapsed = time.time() - self._start_time
            estimated_remaining = elapsed / n_done * (self._total_instances - n_done)
            return f"eta: {timedelta(seconds=int(estimated_remaining))}"
        except ZeroDivisionError:
            return ""

    def update_exit_status_table(self) -> None:
        t = Table()
        t.add_column("Exit Status")
        t.add_column("Count", justify="right", style="bold cyan")
        t.add_column("Most recent instances")
        with self._lock:
            t.show_header = True
            sorted_items = sorted(
                self._instances_by_exit_status.items(), key=lambda x: len(x[1]), reverse=True
            )
            for status, instances in sorted_items:
                instances_str = shorten_str(", ".join(reversed(instances)), 55)
                t.add_row(status, str(len(instances)), instances_str)
        self.render_group.renderables[1] = t

    def _update_total_costs(self) -> None:
        with self._lock:
            self._main_progress_bar.update(
                self._main_task_id,
                total_cost=f"{self._total_cost_usd:.2f}",
                eta=self._get_eta_text_unlocked(),
            )

    def update_instance_status(self, instance_id: str, message: str) -> None:
        with self._lock:
            tid = self._spinner_tasks.get(instance_id)
            if tid is None:
                return
            self._task_progress_bar.update(
                tid,
                status=shorten_str(message, 30),
                instance_id=shorten_str(instance_id, 35, shorten_left=True),
            )
        self._update_total_costs()

    def on_instance_start(self, instance_id: str) -> None:
        with self._lock:
            self._spinner_tasks[instance_id] = self._task_progress_bar.add_task(
                description=f"Task {instance_id}",
                status="initialized",
                total=None,
                instance_id=instance_id,
            )

    def on_instance_end(
        self, instance_id: str, exit_status: str | None, cost_usd_delta: float
    ) -> None:
        with self._lock:
            key = exit_status if exit_status is not None else "unknown"
            self._instances_by_exit_status[key].append(instance_id)
            self._total_cost_usd += float(cost_usd_delta)
            tid = self._spinner_tasks.pop(instance_id, None)
            if tid is not None:
                self._task_progress_bar.remove_task(tid)
            self._main_progress_bar.update(
                self._main_task_id,
                advance=1,
                total_cost=f"{self._total_cost_usd:.2f}",
                eta=self._get_eta_text_unlocked(),
            )
        self.update_exit_status_table()

    def on_uncaught_exception(self, instance_id: str, exception: BaseException) -> None:
        self.on_instance_end(instance_id, f"Uncaught {type(exception).__name__}", 0.0)

    def print_report(self) -> None:
        for status, instances in self.instances_by_exit_status.items():
            print(f"{status}: {len(instances)}")
            for instance in instances:
                print(f"  {instance}")
