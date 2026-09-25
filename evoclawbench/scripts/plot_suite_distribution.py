"""Plot official EvoClawBench suite distribution figures for the paper."""

from __future__ import annotations

import argparse
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


def _default_output_dir(repo_dir: Path) -> Path:
    standard_dir = repo_dir / "paper" / "Figures"
    if standard_dir.exists():
        return standard_dir

    nested_figure_dirs = sorted((repo_dir / "paper").glob("*/Figures"))
    if len(nested_figure_dirs) == 1:
        return nested_figure_dirs[0]

    return standard_dir


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

    # Horizontal bars keep the 17 family names upright and legible at column width.
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10.0, 4.4),
        gridspec_kw={"width_ratios": [1.25, 1.0], "wspace": 0.55},
    )

    ax_family, ax_fixture = axes
    label_size = 12.5
    value_size = 12.0

    family_labels = list(ordered_families)
    family_values = [family_counts[label] for label in family_labels]
    family_colors = [light_blue if label == "Seed workflows" else blue for label in family_labels]
    family_positions = list(range(len(family_labels)))

    ax_family.barh(
        family_positions,
        family_values,
        color=family_colors,
        edgecolor="white",
        height=0.78,
    )
    ax_family.set_xlabel("Number of tasks", fontsize=label_size)
    ax_family.set_xlim(0, 24.5)
    ax_family.set_yticks(family_positions)
    ax_family.set_yticklabels(family_labels, fontsize=label_size)
    ax_family.invert_yaxis()
    ax_family.grid(axis="x", color=grid, linewidth=0.8)
    ax_family.set_axisbelow(True)
    ax_family.tick_params(axis="y", length=0, pad=3)
    ax_family.tick_params(axis="x", labelsize=label_size - 1)
    ax_family.spines["top"].set_visible(False)
    ax_family.spines["right"].set_visible(False)
    ax_family.set_title("(a) Official tasks by family", fontsize=label_size + 1, fontweight="bold")

    for index, tasks in enumerate(family_values):
        ax_family.text(tasks + 0.35, index, f"{tasks}", va="center", ha="left", fontsize=value_size)

    fixture_order = ["JSON", "CSV/TSV", "YAML", "Text/log", "HTML", "Code/script/SQL", "Other"]
    fixture_labels = list(fixture_order)
    fixture_values = [fixture_counts[label] for label in fixture_labels]
    fixture_positions = list(range(len(fixture_labels)))

    ax_fixture.barh(fixture_positions, fixture_values, color=blue, edgecolor="white", height=0.72)
    ax_fixture.set_xlabel("Number of fixture files", fontsize=label_size)
    ax_fixture.set_xlim(0, 262)
    ax_fixture.set_yticks(fixture_positions)
    ax_fixture.set_yticklabels(fixture_labels, fontsize=label_size)
    ax_fixture.invert_yaxis()
    ax_fixture.grid(axis="x", color=grid, linewidth=0.8)
    ax_fixture.set_axisbelow(True)
    ax_fixture.tick_params(axis="y", length=0, pad=3)
    ax_fixture.tick_params(axis="x", labelsize=label_size - 1)
    ax_fixture.spines["top"].set_visible(False)
    ax_fixture.spines["right"].set_visible(False)
    ax_fixture.set_title("(b) Fixture files by format", fontsize=label_size + 1, fontweight="bold")

    for index, value in enumerate(fixture_values):
        ax_fixture.text(value + 3.5, index, f"{value}", va="center", ha="left", fontsize=value_size)

    fig.subplots_adjust(left=0.2, right=0.985, top=0.92, bottom=0.12)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{FIGURE_BASENAME}.pdf", bbox_inches="tight")
    fig.savefig(output_dir / f"{FIGURE_BASENAME}.png", dpi=260, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot official EvoClawBench suite distribution figures for the paper."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for fig_suite_distribution.pdf and fig_suite_distribution.png.",
    )
    args = parser.parse_args()

    bench_dir = SCRIPT_DIR.parent
    repo_dir = bench_dir.parent
    output_dir = args.output_dir or _default_output_dir(repo_dir)
    tasks = _official_tasks(bench_dir / "tasks")
    ordered_families, family_counts, subproblem_counts = _family_distribution(tasks)
    fixture_counts = _fixture_distribution(tasks)
    _validate_counts(tasks, family_counts, subproblem_counts, fixture_counts)
    _plot(
        ordered_families,
        family_counts,
        subproblem_counts,
        fixture_counts,
        output_dir,
    )

    print(f"Official tasks: {sum(family_counts.values())}")
    print(f"Official sub-problems: {sum(subproblem_counts.values())}")
    print(f"Official fixture files: {sum(fixture_counts.values())}")
    print(f"Wrote {output_dir / f'{FIGURE_BASENAME}.pdf'}")
    print(f"Wrote {output_dir / f'{FIGURE_BASENAME}.png'}")


if __name__ == "__main__":
    main()
