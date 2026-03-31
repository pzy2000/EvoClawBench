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
    BENCH_SEEDED_SKILL_NAMES,
    ensure_openclaw_agent,
    execute_task,
    slugify_model,
)
from lib_bench_report import (
    build_bench_report,
    print_bench_report_summary,
    render_bench_report_html,
    render_bench_report_markdown,
)
from lib_environment import DockerEnvironment, LocalEnvironment
from lib_grading import GradeResult, grade_skill_quality, grade_task
from lib_metrics import aggregate_metrics, scan_created_skills
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
        default="both",
        choices=["both", "baseline", "evolution", "bench"],
        help="Evaluation mode",
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
    parser.add_argument(
        "--no-bench-report",
        action="store_true",
        help="In bench mode, skip Markdown/HTML report and terminal summary",
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


def _create_environment(
    environment_type: str,
    docker_image: str,
    task_id: str,
) -> Optional[LocalEnvironment | DockerEnvironment]:
    """Create an execution environment based on type."""
    if environment_type == "docker":
        return DockerEnvironment(image=docker_image)
    return LocalEnvironment()


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


def _execute_single_task_run(ctx: TaskRunContext) -> tuple[Task, int, GradeResult, Dict[str, Any]]:
    """Execute a single task run (one task, one mode, one iteration).

    Returns: (task, run_idx, grade, exec_result)
    """
    task = ctx.task
    mode = ctx.mode
    run_idx = ctx.run_idx
    args = ctx.args
    agent_id = ctx.agent_id
    environment = ctx.environment

    try:
        workers_n = max(1, int(getattr(args, "workers", 1)))
    except (TypeError, ValueError):
        workers_n = 1
    if agent_id is not None and args.runtime == "openclaw":
        effective_agent_id = _openclaw_agent_id_for_parallel_worker(agent_id, workers_n)
    else:
        effective_agent_id = agent_id

    task_grades = []
    task_results = []
    created_skills = []

    logger.info(
        "\n%s\n  Task %s [%s mode] (Run %s)\n%s",
        "=" * 70,
        task.task_id,
        mode,
        run_idx + 1,
        "=" * 70,
    )

    recorder = get_recorder()

    start_recording(
        task_id=task.task_id,
        mode=mode,
        run_number=run_idx + 1,
        agent_id=effective_agent_id or "unknown",
        model_id=args.model,
        runtime=args.runtime,
        workspace="",
    )

    instance_id = _progress_instance_id(ctx)
    prog = ctx.progress
    if prog is not None:
        prog.on_instance_start(instance_id)

    exec_start_time = time.time()
    if prog is not None:
        prog.update_instance_status(instance_id, "Agent")
    try:
        exec_result = execute_task(
            task=task,
            runtime=args.runtime,
            model_id=args.model,
            run_id=ctx.trajectory_run_id,
            timeout_multiplier=args.timeout_multiplier,
            skill_dir=ctx.skill_dir,
            mode=mode,
            agent_id=effective_agent_id,
            verbose=args.verbose,
            environment=environment,
            workspace_root=ctx.workspace_root,
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
            "mode": mode,
        }
        exec_status = "error"
        record_error(
            error_type="execution_failed",
            message=str(exc),
            component="agent",
        )

    if prog is not None:
        prog.update_instance_status(instance_id, "Grading")

    workspace = exec_result.get("workspace", "")
    record_transcript(exec_result.get("transcript", []))

    if workspace:
        expected_files = [f"outputs/data_{i}.json" for i in range(1, 20)]
        record_workspace_files(workspace, expected_files)

    try:
        grade = grade_task(
            task=task,
            execution_result=exec_result,
            skill_dir=ctx.skill_dir,
            judge_model=args.judge or "openrouter/anthropic/claude-opus-4.5",
            verbose=args.verbose,
            runtime=args.runtime,
        )
        grading_error = None
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

    task_grades.append(grade)
    task_results.append(exec_result)

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

    if mode in ("evolution", "bench") and task_results:
        last_workspace = task_results[-1].get("workspace", "")
        if last_workspace:
            excludes = BENCH_SEEDED_SKILL_NAMES if mode == "bench" else None
            created_skills = scan_created_skills(last_workspace, exclude_names=excludes)
            if created_skills:
                logger.info("  Skills created: %s", [s["name"] for s in created_skills])

    if prog is not None:
        usage = exec_result.get("usage") or {}
        cost = float(usage.get("cost_usd", 0.0))
        if grading_error is not None:
            exit_label = "grading_error"
        elif exec_result.get("exit_code", -1) != 0:
            exit_label = "error"
        else:
            exit_label = "success"
        prog.on_instance_end(instance_id, exit_label, cost)

    return task, run_idx, grade, exec_result


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
        if mode in ("evolution", "bench") and task_results_list:
            last_workspace = task_results_list[-1].get("workspace", "") if task_results_list else ""
            if last_workspace:
                excludes = BENCH_SEEDED_SKILL_NAMES if mode == "bench" else None
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
            "usage": {},
            "execution_time": 0.0,
            "workspace": "",
        }
    results[task_id]["grades"].append(grade.to_dict())
    results[task_id]["results"].append(exec_result)
    results[task_id]["execution_time"] += exec_result.get("execution_time", 0)
    if exec_result.get("workspace"):
        results[task_id]["workspace"] = exec_result.get("workspace")


def main():
    script_dir = Path(__file__).parent
    skill_root = script_dir.parent
    tasks_dir = skill_root / "tasks"

    print("\n" + "=" * 70)
    print("  EvoClawBench - Skill Evolution Benchmark")
    print("  Evaluating agent auto-evolution capabilities")
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
    loader.load_all_tasks()
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

    baseline_results = {}
    evolution_results = {}
    bench_results: Dict[str, Dict[str, Any]] = {}

    if args.mode in ("both", "baseline"):
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

    if args.mode in ("both", "evolution"):
        logger.info("\n%s\n  EVOLUTION MODE (skill creation encouraged)\n%s", "=" * 70, "=" * 70)
        evolution_results = _run_single_mode(
            tasks_to_run=tasks_to_run,
            mode="evolution",
            args=args,
            run_id=run_id,
            skill_dir=skill_root,
            agent_id=agent_id,
            run_start_ts=run_start_ts,
        )

    if args.mode == "bench":
        logger.info(
            "\n%s\n  BENCH MODE (no prompt prefix; skills/skill-creator seeded)\n%s",
            "=" * 70,
            "=" * 70,
        )
        bench_results = _run_single_mode(
            tasks_to_run=tasks_to_run,
            mode="bench",
            args=args,
            run_id=run_id,
            skill_dir=skill_root,
            agent_id=agent_id,
            run_start_ts=run_start_ts,
        )

    if args.mode == "both" and baseline_results and evolution_results:
        combined_task_results = []
        for task_id in baseline_results:
            b = baseline_results[task_id]
            e = evolution_results.get(task_id, {})
            combined_task_results.append(
                {
                    "task_id": task_id,
                    "baseline_grade": {"score": b.get("mean_score", 0.0)},
                    "evolution_grade": {"score": e.get("mean_score", 0.0)},
                    "baseline_usage": b.get("usage", {}),
                    "evolution_usage": e.get("usage", {}),
                    "sub_problem_scores_baseline": b.get("sub_problem_scores", []),
                    "sub_problem_scores_evolution": e.get("sub_problem_scores", []),
                    "created_skills": e.get("created_skills", []),
                    "skill_quality_score": e.get("skill_quality_score", 0.0),
                }
            )

        metrics = aggregate_metrics(combined_task_results)
        _log_metrics_summary(metrics, baseline_results, evolution_results)
    else:
        metrics = {}

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
        "evolution_results": evolution_results,
        "bench_results": bench_results,
        "metrics": metrics,
    }

    output_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.json"
    with _OUTPUT_FILE_LOCK:
        output_path.write_text(json.dumps(aggregate, indent=2, default=str), encoding="utf-8")
    logger.info("Results saved to %s", output_path)

    trajectories_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.trajectories.json"
    save_trajectories(trajectories_path)
    logger.info("Trajectories saved to %s", trajectories_path)

    if args.mode == "bench" and not args.no_bench_report:
        report = build_bench_report(
            aggregate,
            artifact_filenames={
                "results_json": output_path.name,
                "trajectories_json": trajectories_path.name,
            },
        )
        print_bench_report_summary(report)
        md_report_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.bench-report.md"
        html_report_path = output_dir / f"{run_id}_{model_slug}_{args.runtime}.bench-report.html"
        md_report_path.write_text(render_bench_report_markdown(report), encoding="utf-8")
        html_report_path.write_text(render_bench_report_html(report), encoding="utf-8")
        logger.info("Bench report saved to %s", md_report_path)
        logger.info("Bench report saved to %s", html_report_path)


def _log_metrics_summary(
    metrics: Dict[str, Any],
    baseline_results: Dict[str, Dict[str, Any]],
    evolution_results: Dict[str, Dict[str, Any]],
) -> None:
    f2p = metrics.get("fail2pass", {}).get("overall", {})
    consistency = metrics.get("consistency", {})
    efficiency = metrics.get("efficiency", {})
    skill_info = metrics.get("created_skills", {})

    print("\n" + "=" * 70)
    print("  EVOCLAWBENCH RESULTS SUMMARY")
    print("=" * 70)

    print(f"\n  EvoScore: {metrics.get('evoscore', 0.0):.4f}")

    print(f"\n  Baseline pass rate:  {f2p.get('baseline_mean', 0):.2%}")
    print(f"  Evolution pass rate: {f2p.get('evolution_mean', 0):.2%}")
    print(f"  fail2pass ratio:    {f2p.get('fail2pass', 'N/A')}")

    print(f"\n  Consistency (baseline):  {consistency.get('baseline', 0):.4f}")
    print(f"  Consistency (evolution): {consistency.get('evolution', 0):.4f}")

    token_eff = efficiency.get("token_efficiency_gain")
    if token_eff is not None:
        print(f"\n  Token efficiency gain: {token_eff:.2f}x")

    print(f"\n  Skills created: {skill_info.get('total_count', 0)}")
    print(f"  Skill quality:  {metrics.get('skill_quality', {}).get('mean', 0):.4f}")

    per_task = metrics.get("fail2pass", {}).get("per_task", {})
    if per_task:
        print(f"\n  {'TASK':<35} {'BASELINE':>10} {'EVOLUTION':>10} {'F2P':>8}")
        print("  " + "-" * 65)
        for task_id, data in sorted(per_task.items()):
            print(
                f"  {task_id:<35} {data['baseline_score']:>10.2%} "
                f"{data['evolution_score']:>10.2%} {data['fail2pass']:>8}"
            )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
