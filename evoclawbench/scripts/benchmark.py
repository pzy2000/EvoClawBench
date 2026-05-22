#!/usr/bin/env python3
"""
EvoClawBench - Skill Evolution Benchmarking System

Evaluates LLM agents' ability to create and reuse skills (auto-evolution)
at runtime. Supports OpenClaw and nanobot runtimes.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.7",
#     "pyyaml>=6.0.1",
#     "openai>=1.0",
#     "openpyxl>=3.1",
#     "python-docx>=1.1",
#     "beautifulsoup4>=4.12",
#     "pandas>=2.0",
# ]
# ///

import argparse
import concurrent.futures
import contextlib
import copy
import json
import logging
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from benchmark_progress import BenchmarkBatchProgress
from lib_agent import (
    SEEDED_SKILL_NAMES,
    ensure_openclaw_agent,
    execute_task,
    slugify_model,
)
from lib_environment import DockerEnvironment, LocalEnvironment
from lib_grading import GradeResult, grade_skill_quality, grade_task
from lib_metrics import aggregate_three_mode_metrics, scan_created_skills
from lib_tasks import Task, TaskLoader
from lib_trajectory import (
    end_recording,
    get_recorder,
    record_error,
    record_grading,
    record_transcript,
    record_workspace_files,
    save_trajectories,
    start_recording,
)
from rich.live import Live

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("benchmark.log")],
)
logger = logging.getLogger("evoclawbench")

_OUTPUT_FILE_LOCK = threading.Lock()


@contextlib.contextmanager
def _suppress_stdout_info_for_rich_live() -> Iterator[None]:
    """Raise log level on stdout StreamHandlers so Rich Live can redraw without mixing with INFO.

    FileHandler (e.g. benchmark.log) is unchanged. Full INFO remains in the log file.
    Use --no-progress for live INFO on the terminal (including with -v).
    """
    touched: list[tuple[logging.Handler, int]] = []
    for h in logging.root.handlers:
        if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout:
            touched.append((h, h.level))
            h.setLevel(logging.WARNING)
    try:
        yield
    finally:
        for h, prev in touched:
            h.setLevel(prev)


# ThreadPoolExecutor gives each worker thread a stable identity; assign 0..workers-1 once per thread
# so parallel OpenClaw runs use distinct agent ids (avoid shared ~/.openclaw agent dirs and races).
_OPENCLAW_PARALLEL_SLOT = threading.local()
_OPENCLAW_SLOT_LOCK = threading.Lock()
_OPENCLAW_NEXT_THREAD_SLOT: list[int] = [0]


def _openclaw_agent_id_for_parallel_worker(base_id: str, workers: int) -> str:
    """Map benchmark base agent id to the real OpenClaw agent id for this worker thread."""
    if workers <= 1:
        return base_id
    if getattr(_OPENCLAW_PARALLEL_SLOT, "value", None) is None:
        with _OPENCLAW_SLOT_LOCK:
            slot = _OPENCLAW_NEXT_THREAD_SLOT[0]
            _OPENCLAW_NEXT_THREAD_SLOT[0] += 1
        _OPENCLAW_PARALLEL_SLOT.value = slot
    return f"{base_id}-w{_OPENCLAW_PARALLEL_SLOT.value}"


def _reset_openclaw_parallel_worker_slots_for_testing() -> None:
    """Reset slot counter for pytest (one benchmark run per process resets in main if needed)."""
    _OPENCLAW_NEXT_THREAD_SLOT[0] = 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EvoClawBench - Skill Evolution Benchmark")
    parser.add_argument(
        "--model", required=True, help="Model identifier (e.g., anthropic/claude-sonnet-4)"
    )
    parser.add_argument(
        "--runtime", default="nanobot", choices=["openclaw", "nanobot"], help="Agent runtime"
    )
    parser.add_argument(
        "--mode",
        default="all",
        choices=["all", "baseline", "preskill", "postskill"],
        help="Evaluation mode (all = baseline + preskill + postskill)",
    )
    parser.add_argument("--suite", default="all", help='Tasks: "all" or comma-separated IDs')
    parser.add_argument("--output-dir", default="results", help="Results directory")
    parser.add_argument(
        "--timeout-multiplier", type=float, default=1.0, help="Scale all task timeouts"
    )
    parser.add_argument("--runs", type=int, default=1, help="Runs per task per mode")
    parser.add_argument("--judge", default=None, help="Judge model for LLM grading")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--no-fail-fast", action="store_true", help="Continue even if sanity check fails"
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="Number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--environment",
        default="local",
        choices=["local", "docker"],
        help="Execution environment: local (subprocess) or docker (isolated container)",
    )
    parser.add_argument(
        "--docker-image", default="evoclawbench/runtime", help="Docker image for isolated execution"
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable Rich live progress UI (default: on when stdout is a TTY)",
    )
    return parser.parse_args()


def _select_task_ids(tasks: List[Task], suite: str) -> Optional[List[str]]:
    if suite == "all":
        return None
    return [tid.strip() for tid in suite.split(",") if tid.strip()]


def _next_run_id(run_root: Path) -> str:
    run_root.mkdir(parents=True, exist_ok=True)
    existing = [int(e.name) for e in run_root.iterdir() if e.is_dir() and e.name.isdigit()]
    next_id = (max(existing) + 1) if existing else 1
    return f"{next_id:04d}"


class TaskRunContext:
    """Encapsulates all context needed to execute a single task run."""

    def __init__(
        self,
        task: Task,
        mode: str,
        run_idx: int,
        args: argparse.Namespace,
        run_id: str,
        skill_dir: Path,
        agent_id: Optional[str],
        environment: Optional[LocalEnvironment | DockerEnvironment] = None,
        progress: Optional[BenchmarkBatchProgress] = None,
        workspace_root: Optional[Path] = None,
    ):
        self.task = task
        self.mode = mode
        self.run_idx = run_idx
        self.args = copy.deepcopy(args)
        self.run_id = run_id
        self.skill_dir = skill_dir
        self.agent_id = agent_id
        self.environment = environment
        self.progress = progress
        self.workspace_root = workspace_root
        self.trajectory_run_id = f"{run_id}-{mode}-{run_idx + 1}"


def _progress_instance_id(ctx: TaskRunContext) -> str:
    return f"{ctx.task.task_id}#r{ctx.run_idx + 1}"


def _effective_agent_id(ctx: TaskRunContext) -> Optional[str]:
    args = ctx.args
    agent_id = ctx.agent_id
    try:
        workers_n = max(1, int(getattr(args, "workers", 1)))
    except (TypeError, ValueError):
        workers_n = 1
    if agent_id is not None and getattr(args, "runtime", None) == "openclaw":
        return _openclaw_agent_id_for_parallel_worker(agent_id, workers_n)
    return agent_id


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


def _usage_from_exec_result(exec_result: Dict[str, Any]) -> Dict[str, Any]:
    merged = _empty_usage()
    usage = exec_result.get("usage") or {}
    for key in (
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "request_count",
    ):
        merged[key] += int(usage.get(key, 0) or 0)
    cost_usd = float(usage.get("cost_usd", usage.get("total_cost_usd", 0.0)) or 0.0)
    merged["cost_usd"] += cost_usd
    merged["total_cost_usd"] += cost_usd
    merged["total_execution_time_seconds"] += float(exec_result.get("execution_time", 0.0) or 0.0)
    return merged


def _merge_usage(*items: Dict[str, Any]) -> Dict[str, Any]:
    merged = _empty_usage()
    for usage in items:
        for key in merged:
            merged[key] += usage.get(key, 0) or 0
    return merged


def _output_file_summaries(workspace_path: str, *, max_files: int = 40) -> List[Dict[str, Any]]:
    workspace = Path(workspace_path)
    outputs_dir = workspace / "outputs"
    if not outputs_dir.is_dir():
        return []
    summaries: List[Dict[str, Any]] = []
    for path in sorted(p for p in outputs_dir.rglob("*") if p.is_file())[:max_files]:
        rel = path.relative_to(workspace)
        item: Dict[str, Any] = {"path": str(rel), "size_bytes": path.stat().st_size}
        try:
            item["content_preview"] = path.read_text(encoding="utf-8", errors="ignore")[:1000]
        except OSError as exc:
            item["error"] = str(exc)
        summaries.append(item)
    return summaries


def _transcript_summary(transcript: List[Dict[str, Any]], *, max_messages: int = 12) -> List[str]:
    lines: List[str] = []
    for entry in transcript:
        if entry.get("type") != "message":
            continue
        msg = entry.get("message", {})
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if isinstance(content, list):
            text = " ".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
        else:
            text = str(content)
        text = " ".join(text.split())
        if text:
            lines.append(f"{role}: {text[:600]}")
        if len(lines) >= max_messages:
            break
    return lines


def _write_first_run_context(task: Task, grade: GradeResult, exec_result: Dict[str, Any]) -> None:
    workspace_s = exec_result.get("workspace", "")
    if not workspace_s:
        return
    workspace = Path(workspace_s)
    context_path = workspace / ".evoclawbench" / "first_run_context.json"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "task_id": task.task_id,
        "task_name": task.name,
        "prompt": task.prompt,
        "expected_behavior": task.expected_behavior,
        "grading_criteria": task.grading_criteria,
        "grade": grade.to_dict(),
        "outputs": _output_file_summaries(str(workspace)),
        "transcript_summary": _transcript_summary(exec_result.get("transcript", [])),
    }
    context_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _execute_phase(
    ctx: TaskRunContext,
    *,
    phase_mode: str,
    workspace_root: Optional[Path],
    grade_result: bool,
    source_skills_workspace: Optional[Path] = None,
    context_source_workspace: Optional[Path] = None,
    manage_progress: bool = True,
    progress_label: Optional[str] = None,
) -> tuple[Optional[GradeResult], Dict[str, Any]]:
    """Execute one benchmark phase, optionally grading the result."""
    task = ctx.task
    run_idx = ctx.run_idx
    args = ctx.args
    effective_agent_id = _effective_agent_id(ctx)

    logger.info(
        "\n%s\n  Task %s [%s mode] (Run %s)\n%s",
        "=" * 70,
        task.task_id,
        phase_mode,
        run_idx + 1,
        "=" * 70,
    )

    recorder = get_recorder()

    start_recording(
        task_id=task.task_id,
        mode=phase_mode,
        run_number=run_idx + 1,
        agent_id=effective_agent_id or "unknown",
        model_id=args.model,
        runtime=getattr(args, "runtime", "unknown"),
        workspace="",
    )

    instance_id = _progress_instance_id(ctx)
    prog = ctx.progress
    if manage_progress and prog is not None:
        prog.on_instance_start(instance_id)

    exec_start_time = time.time()
    if prog is not None:
        prog.update_instance_status(instance_id, progress_label or phase_mode)
    try:
        exec_result = execute_task(
            task=task,
            runtime=args.runtime,
            model_id=args.model,
            run_id=f"{ctx.run_id}-{phase_mode}-{run_idx + 1}",
            timeout_multiplier=args.timeout_multiplier,
            skill_dir=ctx.skill_dir,
            mode=phase_mode,
            agent_id=effective_agent_id,
            verbose=args.verbose,
            environment=ctx.environment,
            workspace_root=workspace_root,
            source_skills_workspace=source_skills_workspace,
            context_source_workspace=context_source_workspace,
        )
        exec_time = time.time() - exec_start_time
        exec_status = "success" if exec_result.get("exit_code", -1) == 0 else "error"
    except Exception as exc:
        exec_time = time.time() - exec_start_time
        logger.warning("Task execution failed for %s: %s", task.task_id, exc)
        exec_result = {
            "agent_id": effective_agent_id or "unknown",
            "task_id": task.task_id,
            "status": "error",
            "transcript": [],
            "usage": {},
            "workspace": "",
            "exit_code": -1,
            "timed_out": False,
            "execution_time": exec_time,
            "stdout": "",
            "stderr": str(exc),
            "mode": phase_mode,
        }
        exec_status = "error"
        record_error(
            error_type="execution_failed",
            message=str(exc),
            component="agent",
        )

    if prog is not None and grade_result:
        prog.update_instance_status(instance_id, "Grading")

    workspace = exec_result.get("workspace", "")
    record_transcript(exec_result.get("transcript", []))

    if workspace:
        expected_files = [f"outputs/data_{i}.json" for i in range(1, 20)]
        record_workspace_files(workspace, expected_files)

    grade: Optional[GradeResult] = None
    grading_error = None
    if grade_result:
        try:
            grade = grade_task(
                task=task,
                execution_result=exec_result,
                skill_dir=ctx.skill_dir,
                judge_model=args.judge or "openrouter/anthropic/claude-opus-4.5",
                verbose=args.verbose,
                runtime=args.runtime,
            )
        except Exception as exc:
            logger.warning("Grading failed for %s: %s", task.task_id, exc)
            grade = GradeResult(
                task_id=task.task_id,
                score=0.0,
                max_score=1.0,
                grading_type=task.grading_type,
                breakdown={},
                notes=f"Grading failed: {exc}",
            )
            grading_error = str(exc)
            record_error(
                error_type="grading_failed",
                message=str(exc),
                component="grading",
            )

        record_grading(
            executed=grading_error is None,
            execution_time=0.0,
            input_shape={
                "transcript_length": len(exec_result.get("transcript", [])),
                "workspace": workspace,
            },
            output=grade.breakdown if grade else {},
            error=grading_error,
            notes=grade.notes if grade else None,
        )

    trajectory = end_recording(
        status=exec_status,
        exit_code=exec_result.get("exit_code", -1),
        timed_out=exec_result.get("timed_out", False),
        execution_time=exec_time,
    )

    if recorder.current_trajectory is None:
        trajectory.execution.workspace = workspace

    if grade is not None:
        score_pct = grade.score / grade.max_score * 100 if grade.max_score > 0 else 0
        emoji = "+" if grade.score >= grade.max_score else "~" if grade.score > 0 else "x"
        logger.info(
            "  [%s] %s: %.1f/%.1f (%.0f%%) - %s",
            emoji,
            task.task_id,
            grade.score,
            grade.max_score,
            score_pct,
            grade.grading_type,
        )

    if phase_mode in ("preskill_author", "postskill_summary") and workspace:
        created_skills = scan_created_skills(workspace, exclude_names=SEEDED_SKILL_NAMES)
        if created_skills:
            logger.info("  Skills created: %s", [s["name"] for s in created_skills])

    if manage_progress and prog is not None:
        usage = exec_result.get("usage") or {}
        cost = float(usage.get("cost_usd", 0.0))
        if grading_error is not None:
            exit_label = "grading_error"
        elif exec_result.get("exit_code", -1) != 0:
            exit_label = "error"
        else:
            exit_label = "success"
        prog.on_instance_end(instance_id, exit_label, cost)

    return grade, exec_result


def _execute_single_task_run(ctx: TaskRunContext) -> tuple[Task, int, GradeResult, Dict[str, Any]]:
    """Execute and grade a single one-phase task run."""
    grade, exec_result = _execute_phase(
        ctx,
        phase_mode=ctx.mode,
        workspace_root=ctx.workspace_root,
        grade_result=True,
    )
    assert grade is not None
    return ctx.task, ctx.run_idx, grade, exec_result


def _run_single_mode(
    *,
    tasks_to_run: List[Task],
    mode: str,
    args: argparse.Namespace,
    run_id: str,
    skill_dir: Path,
    agent_id: Optional[str],
    run_start_ts: str,
) -> Dict[str, Dict[str, Any]]:
    """Run all tasks in one mode (baseline, evolution, or bench).

    Returns {task_id: result_dict}.
    """
    results = {}
    runs_per_task = max(1, args.runs)
    workers = max(1, args.workers)

    if args.environment == "docker":
        logger.info("Using Docker environment with image: %s", args.docker_image)
        logger.info("Note: Each task will run in its own Docker container")

    # Per-mode workspace root: workspaces/{timestamp}_{mode}/{run_id}/
    workspace_mode_root = Path("workspaces") / f"{run_start_ts}_{mode}" / run_id

    all_contexts = []
    for i, task in enumerate(tasks_to_run, 1):
        for run_idx in range(runs_per_task):
            environment = None
            if args.environment == "docker":
                environment = _create_environment(args.docker_image, task.task_id)

            trajectory_run_id = f"{run_id}-{mode}-{run_idx + 1}"
            if runs_per_task > 1:
                workspace_root = workspace_mode_root / trajectory_run_id
            else:
                workspace_root = workspace_mode_root

            ctx = TaskRunContext(
                task=task,
                mode=mode,
                run_idx=run_idx,
                args=args,
                run_id=run_id,
                skill_dir=skill_dir,
                agent_id=agent_id,
                environment=environment,
                workspace_root=workspace_root,
            )
            all_contexts.append(ctx)

    progress_mgr: Optional[BenchmarkBatchProgress] = None
    # Use `is True` so unittest.mock.MagicMock-based args in tests do not enable Rich Live.
    if getattr(args, "show_progress", False) is True and all_contexts:
        progress_mgr = BenchmarkBatchProgress(len(all_contexts))
        for c in all_contexts:
            c.progress = progress_mgr

    def _run_contexts() -> None:
        if workers == 1:
            for ctx in all_contexts:
                _, _, grade, exec_result = _execute_single_task_run(ctx)
                _store_task_result(results, ctx.task.task_id, grade, exec_result)
        else:
            logger.info(
                "  Running %d task runs in parallel (workers=%d)",
                len(all_contexts),
                workers,
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(_execute_single_task_run, ctx): ctx for ctx in all_contexts
                }
                try:
                    for future in concurrent.futures.as_completed(futures):
                        ctx = futures[future]
                        try:
                            _, _, grade, exec_result = future.result()
                            _store_task_result(results, ctx.task.task_id, grade, exec_result)
                        except Exception as exc:
                            logger.error("Task run failed for %s: %s", ctx.task.task_id, exc)
                            if progress_mgr is not None:
                                progress_mgr.on_uncaught_exception(_progress_instance_id(ctx), exc)
                except KeyboardInterrupt:
                    logger.info("Cancelling pending tasks...")
                    for future in futures:
                        if not future.done():
                            future.cancel()

    if progress_mgr is not None:
        with _suppress_stdout_info_for_rich_live():
            with Live(progress_mgr.render_group, refresh_per_second=4):
                _run_contexts()
    else:
        _run_contexts()

    for task in tasks_to_run:
        task_results = results.get(task.task_id, {})
        task_grades = task_results.get("grades", [])
        task_results_list = task_results.get("results", [])

        task_scores = [g.get("score", 0) for g in task_grades]
        if not task_scores:
            task_scores = [0]

        created_skills = []
        skill_quality = 0.0
        if mode in ("preskill_author", "postskill_summary") and task_results_list:
            last_workspace = task_results_list[-1].get("workspace", "") if task_results_list else ""
            if last_workspace:
                excludes = SEEDED_SKILL_NAMES
                created_skills = scan_created_skills(last_workspace, exclude_names=excludes)
                if created_skills:
                    logger.info("  Skills created: %s", [s["name"] for s in created_skills])

        if created_skills:
            skill_quality = grade_skill_quality(created_skills, task)

        if task.task_id in results:
            results[task.task_id]["mode"] = mode
            results[task.task_id]["mean_score"] = statistics.mean(task_scores)
            results[task.task_id]["std_score"] = (
                statistics.stdev(task_scores) if len(task_scores) > 1 else 0.0
            )
            results[task.task_id]["created_skills"] = created_skills
            results[task.task_id]["skill_quality_score"] = skill_quality

    return results


def _build_mode_contexts(
    *,
    tasks_to_run: List[Task],
    mode: str,
    args: argparse.Namespace,
    run_id: str,
    skill_dir: Path,
    agent_id: Optional[str],
    run_start_ts: str,
) -> List[TaskRunContext]:
    runs_per_task = max(1, args.runs)
    workspace_mode_root = Path("workspaces") / f"{run_start_ts}_{mode}" / run_id
    contexts: List[TaskRunContext] = []
    for task in tasks_to_run:
        for run_idx in range(runs_per_task):
            environment = None
            if args.environment == "docker":
                environment = _create_environment(args.docker_image, task.task_id)
            trajectory_run_id = f"{run_id}-{mode}-{run_idx + 1}"
            workspace_root = (
                workspace_mode_root / trajectory_run_id
                if runs_per_task > 1
                else workspace_mode_root
            )
            contexts.append(
                TaskRunContext(
                    task=task,
                    mode=mode,
                    run_idx=run_idx,
                    args=args,
                    run_id=run_id,
                    skill_dir=skill_dir,
                    agent_id=agent_id,
                    environment=environment,
                    workspace_root=workspace_root,
                )
            )
    return contexts


def _store_phase_payload(
    entry: Dict[str, Any],
    *,
    phase: str,
    exec_result: Dict[str, Any],
) -> None:
    entry.setdefault("phase_results", []).append({"phase": phase, "result": exec_result})
    entry.setdefault("phase_usage", {})[phase] = _merge_usage(
        entry.setdefault("phase_usage", {}).get(phase, _empty_usage()),
        _usage_from_exec_result(exec_result),
    )


def _store_preskill_result(
    results: Dict[str, Dict[str, Any]],
    *,
    task: Task,
    primary_grade: GradeResult,
    primary_exec: Dict[str, Any],
    author_exec: Dict[str, Any],
    created_skills: List[Dict[str, Any]],
) -> None:
    _store_task_result(results, task.task_id, primary_grade, primary_exec)
    entry = results[task.task_id]
    _store_phase_payload(entry, phase="skill_generation", exec_result=author_exec)
    _store_phase_payload(entry, phase="execution", exec_result=primary_exec)
    entry.setdefault("skill_generation_results", []).append(author_exec)
    entry.setdefault("created_skills", []).extend(created_skills)
    entry.setdefault("skill_quality_scores", []).append(
        grade_skill_quality(created_skills, task) if created_skills else 0.0
    )
    entry.setdefault("skill_mutation_violations", []).append(
        bool(primary_exec.get("skill_mutation_violation", False))
    )
    entry["end_to_end_usage"] = _merge_usage(
        entry.get("end_to_end_usage", _empty_usage()),
        _usage_from_exec_result(author_exec),
        _usage_from_exec_result(primary_exec),
    )


def _store_postskill_result(
    results: Dict[str, Dict[str, Any]],
    *,
    task: Task,
    first_grade: GradeResult,
    first_exec: Dict[str, Any],
    summary_exec: Dict[str, Any],
    second_grade: GradeResult,
    second_exec: Dict[str, Any],
    created_skills: List[Dict[str, Any]],
) -> None:
    _store_task_result(results, task.task_id, second_grade, second_exec)
    entry = results[task.task_id]
    _store_phase_payload(entry, phase="first_execution", exec_result=first_exec)
    _store_phase_payload(entry, phase="skill_summary", exec_result=summary_exec)
    _store_phase_payload(entry, phase="second_execution", exec_result=second_exec)
    entry.setdefault("first_pass_grades", []).append(first_grade.to_dict())
    entry.setdefault("first_pass_results", []).append(first_exec)
    entry.setdefault("skill_summary_results", []).append(summary_exec)
    entry.setdefault("created_skills", []).extend(created_skills)
    entry.setdefault("skill_quality_scores", []).append(
        grade_skill_quality(created_skills, task) if created_skills else 0.0
    )
    entry.setdefault("skill_mutation_violations", []).append(
        bool(second_exec.get("skill_mutation_violation", False))
    )
    entry["end_to_end_usage"] = _merge_usage(
        entry.get("end_to_end_usage", _empty_usage()),
        _usage_from_exec_result(first_exec),
        _usage_from_exec_result(summary_exec),
        _usage_from_exec_result(second_exec),
    )


def _finalize_phase_mode_results(
    results: Dict[str, Dict[str, Any]],
    *,
    tasks_to_run: List[Task],
    mode: str,
) -> None:
    for task in tasks_to_run:
        if task.task_id not in results:
            continue
        entry = results[task.task_id]
        task_scores = [g.get("score", 0) for g in entry.get("grades", [])] or [0]
        entry["mode"] = mode
        entry["mean_score"] = statistics.mean(task_scores)
        entry["std_score"] = statistics.stdev(task_scores) if len(task_scores) > 1 else 0.0
        quality_scores = entry.get("skill_quality_scores", [])
        entry["skill_quality_score"] = statistics.mean(quality_scores) if quality_scores else 0.0
        entry["skill_mutation_violation"] = any(entry.get("skill_mutation_violations", []))
        if mode == "postskill":
            first_scores = [g.get("score", 0) for g in entry.get("first_pass_grades", [])] or [0]
            first_mean = statistics.mean(first_scores)
            entry["first_pass_mean_score"] = first_mean
            entry["second_pass_mean_score"] = entry["mean_score"]
            entry["second_vs_first_delta"] = entry["mean_score"] - first_mean
            if first_mean > 0:
                entry["second_vs_first_ratio"] = entry["mean_score"] / first_mean
            elif entry["mean_score"] > 0:
                entry["second_vs_first_ratio"] = "inf"
            else:
                entry["second_vs_first_ratio"] = 1.0


def _run_contexts_with_progress(
    *,
    contexts: List[TaskRunContext],
    args: argparse.Namespace,
    runner,
) -> List[Dict[str, Any]]:
    progress_mgr: Optional[BenchmarkBatchProgress] = None
    if getattr(args, "show_progress", False) is True and contexts:
        progress_mgr = BenchmarkBatchProgress(len(contexts))
        for ctx in contexts:
            ctx.progress = progress_mgr

    def _run_all() -> List[Dict[str, Any]]:
        if max(1, args.workers) == 1:
            return [runner(ctx) for ctx in contexts]
        logger.info(
            "  Running %d task pipelines in parallel (workers=%d)", len(contexts), args.workers
        )
        outputs: List[Dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            futures = {executor.submit(runner, ctx): ctx for ctx in contexts}
            for future in concurrent.futures.as_completed(futures):
                ctx = futures[future]
                try:
                    outputs.append(future.result())
                except Exception as exc:
                    logger.error("Task pipeline failed for %s: %s", ctx.task.task_id, exc)
                    if progress_mgr is not None:
                        progress_mgr.on_uncaught_exception(_progress_instance_id(ctx), exc)
        return outputs

    if progress_mgr is not None:
        with _suppress_stdout_info_for_rich_live():
            with Live(progress_mgr.render_group, refresh_per_second=4):
                return _run_all()
    return _run_all()


def _run_preskill_pipeline(ctx: TaskRunContext) -> Dict[str, Any]:
    prog = ctx.progress
    instance_id = _progress_instance_id(ctx)
    if prog is not None:
        prog.on_instance_start(instance_id)
    total_cost = 0.0
    try:
        author_grade, author_exec = _execute_phase(
            ctx,
            phase_mode="preskill_author",
            workspace_root=ctx.workspace_root / "preskill_author" if ctx.workspace_root else None,
            grade_result=False,
            manage_progress=False,
            progress_label="Skill generation",
        )
        del author_grade
        total_cost += float((author_exec.get("usage") or {}).get("cost_usd", 0.0) or 0.0)
        author_workspace_s = author_exec.get("workspace", "")
        author_workspace = Path(author_workspace_s) if author_workspace_s else None
        created_skills = (
            scan_created_skills(str(author_workspace), exclude_names=SEEDED_SKILL_NAMES)
            if author_workspace
            else []
        )
        primary_grade, primary_exec = _execute_phase(
            ctx,
            phase_mode="preskill_execute",
            workspace_root=ctx.workspace_root / "preskill_execute" if ctx.workspace_root else None,
            source_skills_workspace=author_workspace,
            grade_result=True,
            manage_progress=False,
            progress_label="Skill reuse",
        )
        assert primary_grade is not None
        total_cost += float((primary_exec.get("usage") or {}).get("cost_usd", 0.0) or 0.0)
        return {
            "task": ctx.task,
            "primary_grade": primary_grade,
            "primary_exec": primary_exec,
            "author_exec": author_exec,
            "created_skills": created_skills,
        }
    finally:
        if prog is not None:
            prog.on_instance_end(instance_id, "success", total_cost)


def _run_postskill_pipeline(ctx: TaskRunContext) -> Dict[str, Any]:
    prog = ctx.progress
    instance_id = _progress_instance_id(ctx)
    if prog is not None:
        prog.on_instance_start(instance_id)
    total_cost = 0.0
    try:
        first_grade, first_exec = _execute_phase(
            ctx,
            phase_mode="postskill_first",
            workspace_root=ctx.workspace_root / "postskill_first" if ctx.workspace_root else None,
            grade_result=True,
            manage_progress=False,
            progress_label="First execution",
        )
        assert first_grade is not None
        total_cost += float((first_exec.get("usage") or {}).get("cost_usd", 0.0) or 0.0)
        _write_first_run_context(ctx.task, first_grade, first_exec)
        first_workspace_s = first_exec.get("workspace", "")
        first_workspace = Path(first_workspace_s) if first_workspace_s else None
        summary_grade, summary_exec = _execute_phase(
            ctx,
            phase_mode="postskill_summary",
            workspace_root=ctx.workspace_root / "postskill_summary" if ctx.workspace_root else None,
            context_source_workspace=first_workspace,
            grade_result=False,
            manage_progress=False,
            progress_label="Skill summary",
        )
        del summary_grade
        total_cost += float((summary_exec.get("usage") or {}).get("cost_usd", 0.0) or 0.0)
        summary_workspace_s = summary_exec.get("workspace", "")
        summary_workspace = Path(summary_workspace_s) if summary_workspace_s else None
        created_skills = (
            scan_created_skills(str(summary_workspace), exclude_names=SEEDED_SKILL_NAMES)
            if summary_workspace
            else []
        )
        second_grade, second_exec = _execute_phase(
            ctx,
            phase_mode="postskill_second",
            workspace_root=ctx.workspace_root / "postskill_second" if ctx.workspace_root else None,
            source_skills_workspace=summary_workspace,
            grade_result=True,
            manage_progress=False,
            progress_label="Second execution",
        )
        assert second_grade is not None
        total_cost += float((second_exec.get("usage") or {}).get("cost_usd", 0.0) or 0.0)
        return {
            "task": ctx.task,
            "first_grade": first_grade,
            "first_exec": first_exec,
            "summary_exec": summary_exec,
            "second_grade": second_grade,
            "second_exec": second_exec,
            "created_skills": created_skills,
        }
    finally:
        if prog is not None:
            prog.on_instance_end(instance_id, "success", total_cost)


def _run_preskill_mode(
    *,
    tasks_to_run: List[Task],
    args: argparse.Namespace,
    run_id: str,
    skill_dir: Path,
    agent_id: Optional[str],
    run_start_ts: str,
) -> Dict[str, Dict[str, Any]]:
    contexts = _build_mode_contexts(
        tasks_to_run=tasks_to_run,
        mode="preskill",
        args=args,
        run_id=run_id,
        skill_dir=skill_dir,
        agent_id=agent_id,
        run_start_ts=run_start_ts,
    )
    results: Dict[str, Dict[str, Any]] = {}
    for payload in _run_contexts_with_progress(
        contexts=contexts, args=args, runner=_run_preskill_pipeline
    ):
        _store_preskill_result(results, **payload)
    _finalize_phase_mode_results(results, tasks_to_run=tasks_to_run, mode="preskill")
    return results


def _run_postskill_mode(
    *,
    tasks_to_run: List[Task],
    args: argparse.Namespace,
    run_id: str,
    skill_dir: Path,
    agent_id: Optional[str],
    run_start_ts: str,
) -> Dict[str, Dict[str, Any]]:
    contexts = _build_mode_contexts(
        tasks_to_run=tasks_to_run,
        mode="postskill",
        args=args,
        run_id=run_id,
        skill_dir=skill_dir,
        agent_id=agent_id,
        run_start_ts=run_start_ts,
    )
    results: Dict[str, Dict[str, Any]] = {}
    for payload in _run_contexts_with_progress(
        contexts=contexts, args=args, runner=_run_postskill_pipeline
    ):
        _store_postskill_result(results, **payload)
    _finalize_phase_mode_results(results, tasks_to_run=tasks_to_run, mode="postskill")
    return results


def _create_environment(
    docker_image: str, task_id: str
) -> Optional[LocalEnvironment | DockerEnvironment]:
    """Create an execution environment for a task."""
    try:
        return DockerEnvironment(image=docker_image)
    except Exception as exc:
        logger.warning("Failed to create Docker environment for %s: %s", task_id, exc)
        return None


def _store_task_result(
    results: Dict[str, Dict[str, Any]],
    task_id: str,
    grade: GradeResult,
    exec_result: Dict[str, Any],
) -> None:
    """Thread-safe storage of task results."""
    if task_id not in results:
        results[task_id] = {
            "task_id": task_id,
            "grades": [],
            "results": [],
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "request_count": 0,
                "cost_usd": 0.0,
                "total_cost_usd": 0.0,
                "total_execution_time_seconds": 0.0,
            },
            "execution_time": 0.0,
            "workspace": "",
            "sub_problem_scores": [],
        }
    results[task_id]["grades"].append(grade.to_dict())
    results[task_id]["results"].append(exec_result)
    execution_time = float(exec_result.get("execution_time", 0.0) or 0.0)
    results[task_id]["execution_time"] += execution_time
    results[task_id]["usage"]["total_execution_time_seconds"] += execution_time
    usage = exec_result.get("usage") or {}
    for key in (
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "request_count",
    ):
        results[task_id]["usage"][key] += int(usage.get(key, 0) or 0)
    cost_usd = float(usage.get("cost_usd", 0.0) or 0.0)
    results[task_id]["usage"]["cost_usd"] += cost_usd
    results[task_id]["usage"]["total_cost_usd"] += cost_usd
    results[task_id]["sub_problem_scores"] = list(grade.sub_problem_scores)
    if exec_result.get("workspace"):
        results[task_id]["workspace"] = exec_result.get("workspace")


def main():
    script_dir = Path(__file__).parent
    skill_root = script_dir.parent
    tasks_dir = skill_root / "tasks"

    print("\n" + "=" * 70)
    print("  EvoClawBench - Three-Mode Agent Skill Benchmark")
    print("  Evaluating baseline, preskill, and postskill performance")
    print("=" * 70 + "\n")

    if not tasks_dir.exists():
        logger.error("Tasks directory not found: %s", tasks_dir)
        sys.exit(1)

    args = _parse_args()
    args.show_progress = bool(sys.stdout.isatty() and not args.no_progress)

    logger.info("Runtime: %s", args.runtime)
    logger.info("Model: %s", args.model)
    logger.info("Mode: %s", args.mode)
    logger.info("Workers: %d", args.workers)
    logger.info("Environment: %s", args.environment)

    loader = TaskLoader(tasks_dir)
    all_tasks = loader.load_all_tasks()

    task_ids = _select_task_ids(all_tasks, args.suite)
    if task_ids is not None:
        tasks_to_run = [t for t in all_tasks if t.task_id in task_ids]
    else:
        tasks_to_run = all_tasks

    if not tasks_to_run:
        logger.error("No tasks to run")
        sys.exit(1)

    logger.info("Tasks to run: %d", len(tasks_to_run))

    model_slug = slugify_model(args.model)
    run_start_ts = time.strftime("%Y_%m_%d_%H_%M_%S")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = _next_run_id(output_dir)

    agent_id = None
    if args.runtime == "openclaw":
        agent_id = f"evobench-{model_slug}"
        workspace_base = Path("workspaces") / "init" / run_id / "agent_workspace"
        workers_n = max(1, args.workers)
        _OPENCLAW_NEXT_THREAD_SLOT[0] = 0
        if workers_n <= 1:
            ensure_openclaw_agent(agent_id, args.model, workspace_base)
        else:
            for k in range(workers_n):
                ensure_openclaw_agent(
                    f"{agent_id}-w{k}",
                    args.model,
                    workspace_base / f"w{k}",
                )

    baseline_results: Dict[str, Dict[str, Any]] = {}
    preskill_results: Dict[str, Dict[str, Any]] = {}
    postskill_results: Dict[str, Dict[str, Any]] = {}

    if args.mode in ("all", "baseline"):
        logger.info("\n%s\n  BASELINE MODE (no skill creation)\n%s", "=" * 70, "=" * 70)
        baseline_results = _run_single_mode(
            tasks_to_run=tasks_to_run,
            mode="baseline",
            args=args,
            run_id=run_id,
            skill_dir=skill_root,
            agent_id=agent_id,
            run_start_ts=run_start_ts,
        )

    if args.mode in ("all", "preskill"):
        logger.info(
            "\n%s\n  PRESKILL MODE (generate skill first, then execute with it)\n%s",
            "=" * 70,
            "=" * 70,
        )
        preskill_results = _run_preskill_mode(
            tasks_to_run=tasks_to_run,
            args=args,
            run_id=run_id,
            skill_dir=skill_root,
            agent_id=agent_id,
            run_start_ts=run_start_ts,
        )

    if args.mode in ("all", "postskill"):
        logger.info(
            "\n%s\n  POSTSKILL MODE (execute, summarize skill, execute again)\n%s",
            "=" * 70,
            "=" * 70,
        )
        postskill_results = _run_postskill_mode(
            tasks_to_run=tasks_to_run,
            args=args,
            run_id=run_id,
            skill_dir=skill_root,
            agent_id=agent_id,
            run_start_ts=run_start_ts,
        )

    metrics = aggregate_three_mode_metrics(
        baseline_results=baseline_results,
        preskill_results=preskill_results,
        postskill_results=postskill_results,
    )
    _log_metrics_summary(metrics)

    aggregate = {
        "benchmark": "evoclawbench",
        "version": "0.1.0",
        "model": args.model,
        "runtime": args.runtime,
        "mode": args.mode,
        "run_id": run_id,
        "timestamp": time.time(),
        "runs_per_task": max(1, args.runs),
        "workers": args.workers,
        "environment": args.environment,
        "baseline_results": baseline_results,
        "preskill_results": preskill_results,
        "postskill_results": postskill_results,
        "metrics": metrics,
    }

    output_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.json"
    with _OUTPUT_FILE_LOCK:
        output_path.write_text(json.dumps(aggregate, indent=2, default=str), encoding="utf-8")
    logger.info("Results saved to %s", output_path)

    trajectories_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.trajectories.json"
    save_trajectories(trajectories_path)
    logger.info("Trajectories saved to %s", trajectories_path)


def _log_metrics_summary(metrics: Dict[str, Any]) -> None:
    execution = metrics.get("execution_only", {})
    end_to_end = metrics.get("end_to_end", {})
    postskill = metrics.get("postskill", {})
    skill_info = metrics.get("created_skills", {})

    print("\n" + "=" * 70)
    print("  EVOCLAWBENCH RESULTS SUMMARY")
    print("=" * 70)

    scores = execution.get("mean_scores", {})
    print(f"\n  Baseline score:  {scores.get('baseline', 0):.2%}")
    print(f"  Preskill score:  {scores.get('preskill', 0):.2%}")
    print(f"  Postskill score: {scores.get('postskill', 0):.2%}")

    ratios = execution.get("ratios_vs_baseline", {})
    print(f"\n  Preskill / baseline:  {ratios.get('preskill', 'N/A')}")
    print(f"  Postskill / baseline: {ratios.get('postskill', 'N/A')}")

    end_usage = end_to_end.get("usage", {})
    if end_usage:
        print("\n  End-to-end tokens:")
        print(f"    baseline:  {int(end_usage.get('baseline', {}).get('total_tokens', 0))}")
        print(f"    preskill:  {int(end_usage.get('preskill', {}).get('total_tokens', 0))}")
        print(f"    postskill: {int(end_usage.get('postskill', {}).get('total_tokens', 0))}")

    if postskill:
        print(f"\n  Postskill first pass:  {postskill.get('first_pass_mean', 0):.2%}")
        print(f"  Postskill second pass: {postskill.get('second_pass_mean', 0):.2%}")
        print(f"  Second-first delta:    {postskill.get('second_vs_first_delta', 0):.2%}")

    print(f"\n  Preskill skills created:  {skill_info.get('preskill_count', 0)}")
    print(f"  Postskill skills created: {skill_info.get('postskill_count', 0)}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
