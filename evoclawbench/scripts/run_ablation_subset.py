#!/usr/bin/env python3
"""Run a small skill-content ablation subset."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark import (  # noqa: E402
    TaskRunContext,
    _execute_phase,
    _merge_usage,
    _next_run_id,
    _usage_from_exec_result,
    _write_first_run_context,
)
from lib_agent import SEEDED_SKILL_NAMES, ensure_openclaw_agent, slugify_model  # noqa: E402
from lib_grading import GradeResult, grade_skill_quality  # noqa: E402
from lib_metrics import scan_created_skills  # noqa: E402
from lib_tasks import Task, TaskLoader  # noqa: E402

DEFAULT_ABLATION_SUBSET = (
    "task_02_log_analysis",
    "task_07_doc_extraction",
    "task_15_shell_automation",
    "task_21_metrics_anomaly",
)
DEFAULT_SKILL_DIR = Path(__file__).resolve().parent.parent


def _empty_usage() -> Dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "request_count": 0,
        "cost_usd": 0.0,
        "total_cost_usd": 0.0,
        "total_execution_time_seconds": 0.0,
    }


def _make_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        model=args.model,
        runtime=args.runtime,
        mode="ablation",
        suite=args.tasks,
        output_dir=str(args.output_dir),
        timeout_multiplier=args.timeout_multiplier,
        runs=1,
        judge=args.judge,
        verbose=args.verbose,
        no_fail_fast=True,
        workers=1,
        environment="local",
        docker_image="evoclawbench/runtime",
        no_progress=True,
    )


def _select_tasks(tasks_dir: Path, task_ids: Iterable[str]) -> List[Task]:
    all_tasks = {task.task_id: task for task in TaskLoader(tasks_dir).load_all_tasks()}
    selected = []
    for task_id in task_ids:
        if task_id not in all_tasks:
            raise ValueError(f"Unknown task id: {task_id}")
        selected.append(all_tasks[task_id])
    return selected


def _skill_source(root: Path, task_id: str, name: str, body: str) -> Path:
    workspace = root / task_id / name
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return workspace


def _empty_skill_source(root: Path, task: Task) -> Path:
    return _skill_source(
        root,
        task.task_id,
        "empty-skill",
        "# Empty Skill\n\nThis placeholder intentionally contains no task guidance.\n",
    )


def _irrelevant_skill_source(root: Path, task: Task) -> Path:
    return _skill_source(
        root,
        task.task_id,
        "irrelevant-skill",
        "# Irrelevant Skill\n\nUse this skill only for writing a casual travel packing list.\n",
    )


def _record_variant(
    rows: List[Dict[str, Any]],
    *,
    task: Task,
    variant: str,
    grade: GradeResult,
    usage: Dict[str, Any],
    created_skills: Optional[List[Dict[str, Any]]] = None,
    notes: str = "",
) -> None:
    rows.append(
        {
            "task_id": task.task_id,
            "variant": variant,
            "score": round(float(grade.score), 4),
            "usage": usage,
            "created_skill_count": len(created_skills or []),
            "skill_quality_score": (
                round(grade_skill_quality(created_skills or [], task), 4) if created_skills else 0.0
            ),
            "notes": notes,
        }
    )


def summarize_ablation(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    variants = sorted({row["variant"] for row in rows})
    by_variant: Dict[str, Dict[str, Any]] = {}
    baseline_by_task = {
        row["task_id"]: row["score"] for row in rows if row["variant"] == "baseline"
    }
    for variant in variants:
        selected = [row for row in rows if row["variant"] == variant]
        usage = _merge_usage(*(row["usage"] for row in selected)) if selected else _empty_usage()
        deltas = [
            row["score"] - baseline_by_task[row["task_id"]]
            for row in selected
            if row["task_id"] in baseline_by_task and variant != "baseline"
        ]
        by_variant[variant] = {
            "task_count": len(selected),
            "mean_score_pct": (
                round(sum(row["score"] for row in selected) / len(selected) * 100.0, 2)
                if selected
                else 0.0
            ),
            "mean_delta_vs_baseline_pct": (
                round(sum(deltas) / len(deltas) * 100.0, 2) if deltas else 0.0
            ),
            "total_tokens": int(usage.get("total_tokens", 0) or 0),
            "total_cost_usd": round(float(usage.get("total_cost_usd", 0.0) or 0.0), 6),
            "total_time_hours": round(
                float(usage.get("total_execution_time_seconds", 0.0) or 0.0) / 3600.0,
                3,
            ),
            "request_count": int(usage.get("request_count", 0) or 0),
            "created_skill_count": sum(row.get("created_skill_count", 0) for row in selected),
        }
    return {"variants": by_variant, "task_rows": rows}


def render_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Ablation Summary",
        "",
        "| Variant | Tasks | Mean score | Delta vs baseline | Tokens | Cost USD | Time h | "
        "Requests | Skills |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, row in summary["variants"].items():
        lines.append(
            "| {variant} | {task_count} | {mean_score_pct:.2f} | "
            "{mean_delta_vs_baseline_pct:.2f} | {total_tokens} | {total_cost_usd:.6f} | "
            "{total_time_hours:.3f} | {request_count} | {created_skill_count} |".format(
                variant=variant, **row
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _run_task_variants(
    *,
    task: Task,
    bench_args: SimpleNamespace,
    run_id: str,
    skill_dir: Path,
    agent_id: str,
    workspace_root: Path,
    source_root: Path,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    ctx = TaskRunContext(
        task=task,
        mode="ablation",
        run_idx=0,
        args=bench_args,
        run_id=run_id,
        skill_dir=skill_dir,
        agent_id=agent_id,
        workspace_root=workspace_root,
    )

    baseline_grade, baseline_exec = _execute_phase(
        ctx,
        phase_mode="baseline",
        workspace_root=workspace_root / "baseline",
        grade_result=True,
    )
    assert baseline_grade is not None
    _record_variant(
        rows,
        task=task,
        variant="baseline",
        grade=baseline_grade,
        usage=_usage_from_exec_result(baseline_exec),
    )

    author_grade, author_exec = _execute_phase(
        ctx,
        phase_mode="preskill_author",
        workspace_root=workspace_root / "preskill_author",
        grade_result=False,
    )
    del author_grade
    author_workspace = Path(str(author_exec.get("workspace") or ""))
    created = scan_created_skills(str(author_workspace), exclude_names=SEEDED_SKILL_NAMES)
    normal_grade, normal_exec = _execute_phase(
        ctx,
        phase_mode="preskill_execute",
        workspace_root=workspace_root / "preskill_normal",
        grade_result=True,
        source_skills_workspace=author_workspace,
    )
    assert normal_grade is not None
    _record_variant(
        rows,
        task=task,
        variant="preskill_normal",
        grade=normal_grade,
        usage=_merge_usage(
            _usage_from_exec_result(author_exec), _usage_from_exec_result(normal_exec)
        ),
        created_skills=created,
    )

    for variant, source in (
        ("empty_skill_reuse", _empty_skill_source(source_root, task)),
        ("irrelevant_skill_reuse", _irrelevant_skill_source(source_root, task)),
    ):
        grade, exec_result = _execute_phase(
            ctx,
            phase_mode="preskill_execute",
            workspace_root=workspace_root / variant,
            grade_result=True,
            source_skills_workspace=source,
        )
        assert grade is not None
        _record_variant(
            rows,
            task=task,
            variant=variant,
            grade=grade,
            usage=_usage_from_exec_result(exec_result),
            created_skills=scan_created_skills(str(source), exclude_names=SEEDED_SKILL_NAMES),
        )

    first_grade, first_exec = _execute_phase(
        ctx,
        phase_mode="postskill_first",
        workspace_root=workspace_root / "postskill_first",
        grade_result=True,
    )
    assert first_grade is not None
    _write_first_run_context(task, first_grade, first_exec)
    first_workspace = Path(str(first_exec.get("workspace") or ""))
    summary_grade, summary_exec = _execute_phase(
        ctx,
        phase_mode="postskill_summary",
        workspace_root=workspace_root / "postskill_summary",
        grade_result=False,
        context_source_workspace=first_workspace,
    )
    del summary_grade
    summary_workspace = Path(str(summary_exec.get("workspace") or ""))
    post_created = scan_created_skills(str(summary_workspace), exclude_names=SEEDED_SKILL_NAMES)
    second_grade, second_exec = _execute_phase(
        ctx,
        phase_mode="postskill_second",
        workspace_root=workspace_root / "postskill_normal",
        grade_result=True,
        source_skills_workspace=summary_workspace,
    )
    assert second_grade is not None
    _record_variant(
        rows,
        task=task,
        variant="postskill_normal",
        grade=second_grade,
        usage=_merge_usage(
            _usage_from_exec_result(first_exec),
            _usage_from_exec_result(summary_exec),
            _usage_from_exec_result(second_exec),
        ),
        created_skills=post_created,
    )

    no_skill_grade, no_skill_exec = _execute_phase(
        ctx,
        phase_mode="postskill_second",
        workspace_root=workspace_root / "postskill_summary_no_skill",
        grade_result=True,
        source_skills_workspace=None,
    )
    assert no_skill_grade is not None
    _record_variant(
        rows,
        task=task,
        variant="postskill_summary_no_skill",
        grade=no_skill_grade,
        usage=_merge_usage(
            _usage_from_exec_result(first_exec),
            _usage_from_exec_result(summary_exec),
            _usage_from_exec_result(no_skill_exec),
        ),
        created_skills=[],
        notes="Ran postskill first and summary phases, then discarded generated skills.",
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--runtime", default="openclaw", choices=["openclaw", "nanobot"])
    parser.add_argument("--judge", default="openai/MiniMax/MiniMax-M2.7")
    parser.add_argument("--tasks", default=",".join(DEFAULT_ABLATION_SUBSET))
    parser.add_argument("--tasks-dir", type=Path, default=Path("tasks"))
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper_subset_experiments"))
    parser.add_argument("--timeout-multiplier", type=float, default=1.0)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_id = _next_run_id(args.output_dir)
    model_slug = slugify_model(args.model)
    bench_args = _make_args(args)
    agent_id = f"evobench-ablation-{model_slug}"
    workspace_root = Path("workspaces") / f"{time.strftime('%Y_%m_%d_%H_%M_%S')}_ablation" / run_id
    source_root = workspace_root / "ablation_skill_sources"

    if args.runtime == "openclaw":
        ensure_openclaw_agent(agent_id, args.model, Path("workspaces") / "init" / run_id)

    rows: List[Dict[str, Any]] = []
    tasks = _select_tasks(
        args.tasks_dir, [item.strip() for item in args.tasks.split(",") if item.strip()]
    )
    for task in tasks:
        rows.extend(
            _run_task_variants(
                task=task,
                bench_args=bench_args,
                run_id=run_id,
                skill_dir=args.skill_dir,
                agent_id=agent_id,
                workspace_root=workspace_root / task.task_id,
                source_root=source_root,
            )
        )

    payload = {
        "benchmark": "evoclawbench",
        "experiment": "skill_content_ablation_subset",
        "model": args.model,
        "runtime": args.runtime,
        "judge_model": args.judge,
        "run_id": run_id,
        "tasks": [task.task_id for task in tasks],
        "summary": summarize_ablation(rows),
    }
    json_path = args.output_dir / "ablation_summary.json"
    md_path = args.output_dir / "ablation_summary.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload["summary"]), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
