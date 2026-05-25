"""Plot official EvoClawBench suite distribution figures for the paper."""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib_tasks import Task, TaskLoader  # noqa: E402

OFFICIAL_TASK_COUNT = 100
OFFICIAL_SUBPROBLEM_COUNT = 502
OFFICIAL_FIXTURE_COUNT = 512
FIGURE_BASENAME = "fig_suite_distribution"


def _task_number(task: Task) -> int:
    try:
        return int(task.task_id.split("_")[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Task id does not contain a numeric index: {task.task_id}") from exc


def _official_tasks(tasks_dir: Path) -> list[Task]:
    tasks = TaskLoader(tasks_dir).load_all_tasks()
    official = [task for task in tasks if task.task_id != "task_00_sanity"]
    official.sort(key=lambda task: _task_number(task))
    return official


def _suite_family(task: Task) -> str:
    if _task_number(task) <= 21:
        return "Seed workflows"
    family = str(task.frontmatter.get("task_family", "")).strip()
    if not family:
        raise ValueError(f"Generated task is missing task_family: {task.task_id}")
    return family


def _family_distribution(tasks: Iterable[Task]) -> tuple[list[str], dict[str, int], dict[str, int]]:
    task_counts: Counter[str] = Counter()
    subproblem_counts: defaultdict[str, int] = defaultdict(int)
    first_seen: dict[str, int] = {}

    for task in tasks:
        family = _suite_family(task)
        task_counts[family] += 1
        subproblem_counts[family] += task.num_sub_problems
        first_seen.setdefault(family, _task_number(task))

    ordered_families = sorted(task_counts, key=lambda family: first_seen[family])
    return ordered_families, dict(task_counts), dict(subproblem_counts)


def _fixture_group(file_spec: object) -> str:
    suffix = Path(str(file_spec)).suffix.lower().lstrip(".")
    if suffix == "json":
        return "JSON"
    if suffix in {"csv", "tsv"}:
        return "CSV/TSV"
    if suffix in {"yaml", "yml"}:
        return "YAML"
    if suffix in {"txt", "log"}:
        return "Text/log"
    if suffix == "html":
        return "HTML"
    if suffix in {"py", "sh", "sql", "js", "go", "mod"}:
        return "Code/script/SQL"
    return "Other"


def _fixture_distribution(tasks: Iterable[Task]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for task in tasks:
        for file_spec in task.workspace_files:
            counts[_fixture_group(file_spec)] += 1
    return dict(counts)


def _validate_counts(
    tasks: list[Task],
    family_counts: dict[str, int],
    subproblem_counts: dict[str, int],
    fixture_counts: dict[str, int],
) -> None:
    task_total = sum(family_counts.values())
    subproblem_total = sum(subproblem_counts.values())
    fixture_total = sum(fixture_counts.values())

    if len(tasks) != OFFICIAL_TASK_COUNT or task_total != OFFICIAL_TASK_COUNT:
        raise ValueError(
            f"Expected {OFFICIAL_TASK_COUNT} official tasks, got {len(tasks)} / {task_total}"
        )
    if subproblem_total != OFFICIAL_SUBPROBLEM_COUNT:
        raise ValueError(
            f"Expected {OFFICIAL_SUBPROBLEM_COUNT} sub-problems, got {subproblem_total}"
        )
    if fixture_total != OFFICIAL_FIXTURE_COUNT:
        raise ValueError(f"Expected {OFFICIAL_FIXTURE_COUNT} fixture files, got {fixture_total}")


def _plot(
    ordered_families: list[str],
    family_counts: dict[str, int],
    subproblem_counts: dict[str, int],
    fixture_counts: dict[str, int],
    output_dir: Path,
) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.labelcolor": "#333333",
            "axes.edgecolor": "#333333",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "text.color": "#333333",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    blue = "#3f73c4"
    light_blue = "#9bb7e5"
    grid = "#e5e5e5"
    gray = "#6f6f6f"

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(11.6, 4.8),
        gridspec_kw={"width_ratios": [1.55, 1.0], "wspace": 0.28},
    )

    ax_family, ax_fixture = axes

    family_labels = list(ordered_families)
    family_values = [family_counts[label] for label in family_labels]
    family_subproblems = [subproblem_counts[label] for label in family_labels]
    family_colors = [light_blue if label == "Seed workflows" else blue for label in family_labels]
    family_positions = list(range(len(family_labels)))

    ax_family.bar(
        family_positions,
        family_values,
        color=family_colors,
        edgecolor="white",
        width=0.76,
    )
    ax_family.set_ylabel("Number of tasks", fontsize=10)
    ax_family.set_ylim(0, 23.5)
    ax_family.set_xticks(family_positions)
    ax_family.set_xticklabels(
        family_labels,
        rotation=88,
        ha="right",
        rotation_mode="anchor",
        fontsize=6.4,
    )
    ax_family.grid(axis="y", color=grid, linewidth=0.8)
    ax_family.set_axisbelow(True)
    ax_family.tick_params(axis="x", length=0, pad=1)
    ax_family.tick_params(axis="y", labelsize=8.8)
    ax_family.spines["top"].set_visible(False)
    ax_family.spines["right"].set_visible(False)

    for index, (tasks, subproblems) in enumerate(zip(family_values, family_subproblems)):
        ax_family.text(
            index,
            tasks + 0.38,
            f"{tasks}",
            va="bottom",
            ha="center",
            fontsize=8.1,
        )
        ax_family.text(
            index,
            tasks + 1.28,
            f"{subproblems} sub.",
            va="bottom",
            ha="center",
            fontsize=5.8,
            color=gray,
        )

    fixture_order = ["JSON", "CSV/TSV", "YAML", "Text/log", "HTML", "Code/script/SQL", "Other"]
    fixture_labels = list(fixture_order)
    fixture_values = [fixture_counts[label] for label in fixture_labels]
    fixture_positions = list(range(len(fixture_labels)))

    ax_fixture.bar(fixture_positions, fixture_values, color=blue, edgecolor="white", width=0.76)
    ax_fixture.set_ylabel("Number of fixture files", fontsize=10)
    ax_fixture.set_ylim(0, 248)
    ax_fixture.set_xticks(fixture_positions)
    ax_fixture.set_xticklabels(
        fixture_labels,
        rotation=88,
        ha="right",
        rotation_mode="anchor",
        fontsize=7.2,
    )
    ax_fixture.grid(axis="y", color=grid, linewidth=0.8)
    ax_fixture.set_axisbelow(True)
    ax_fixture.tick_params(axis="x", length=0, pad=1)
    ax_fixture.tick_params(axis="y", labelsize=8.8)
    ax_fixture.spines["top"].set_visible(False)
    ax_fixture.spines["right"].set_visible(False)

    for index, value in enumerate(fixture_values):
        ax_fixture.text(index, value + 3.5, f"{value}", va="bottom", ha="center", fontsize=8.3)

    fig.text(
        0.24,
        0.025,
        "(a) Official tasks across benchmark families",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
    fig.text(
        0.74,
        0.025,
        "(b) Repository-local fixture files across formats",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

    fig.subplots_adjust(left=0.06, right=0.985, top=0.96, bottom=0.38)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{FIGURE_BASENAME}.pdf", bbox_inches="tight")
    fig.savefig(output_dir / f"{FIGURE_BASENAME}.png", dpi=260, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    bench_dir = SCRIPT_DIR.parent
    repo_dir = bench_dir.parent
    tasks = _official_tasks(bench_dir / "tasks")
    ordered_families, family_counts, subproblem_counts = _family_distribution(tasks)
    fixture_counts = _fixture_distribution(tasks)
    _validate_counts(tasks, family_counts, subproblem_counts, fixture_counts)
    _plot(
        ordered_families,
        family_counts,
        subproblem_counts,
        fixture_counts,
        repo_dir / "paper" / "Figures",
    )

    print(f"Official tasks: {sum(family_counts.values())}")
    print(f"Official sub-problems: {sum(subproblem_counts.values())}")
    print(f"Official fixture files: {sum(fixture_counts.values())}")
    print(f"Wrote paper/Figures/{FIGURE_BASENAME}.pdf")
    print(f"Wrote paper/Figures/{FIGURE_BASENAME}.png")


if __name__ == "__main__":
    main()
