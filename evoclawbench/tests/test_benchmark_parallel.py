"""Tests for parallel execution in benchmark.py."""

import concurrent.futures
import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_environment import LocalEnvironment


class TestOutputFileLock:
    """Test thread-safe file writing with _OUTPUT_FILE_LOCK."""

    def test_lock_exists(self):
        from benchmark import _OUTPUT_FILE_LOCK

        assert isinstance(_OUTPUT_FILE_LOCK, threading.Lock)

    def test_concurrent_file_write(self, tmp_path):
        from benchmark import _OUTPUT_FILE_LOCK

        output_file = tmp_path / "test_output.json"
        results = []
        errors = []

        def write_result(idx):
            try:
                data = {"idx": idx, "thread": threading.current_thread().name}
                with _OUTPUT_FILE_LOCK:
                    existing = {}
                    if output_file.exists():
                        existing = json.loads(output_file.read_text())
                    existing[f"key_{idx}"] = data
                    output_file.write_text(json.dumps(existing, indent=2))
                results.append(idx)
            except Exception as e:
                errors.append((idx, str(e)))

        threads = []
        for i in range(10):
            t = threading.Thread(target=write_result, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10

        final_data = json.loads(output_file.read_text())
        assert len(final_data) == 10


class TestTaskRunContext:
    """Test TaskRunContext dataclass."""

    def test_context_creation(self):
        from benchmark import TaskRunContext

        mock_task = MagicMock()
        mock_task.task_id = "task_01_test"

        ctx = TaskRunContext(
            task=mock_task,
            mode="baseline",
            run_idx=0,
            args=MagicMock(),
            run_id="run_001",
            skill_dir=Path("/tmp"),
            agent_id=None,
        )

        assert ctx.task == mock_task
        assert ctx.mode == "baseline"
        assert ctx.run_idx == 0
        assert ctx.run_id == "run_001"

    def test_context_with_environment(self):
        from benchmark import TaskRunContext

        mock_task = MagicMock()
        env = LocalEnvironment()

        ctx = TaskRunContext(
            task=mock_task,
            mode="preskill",
            run_idx=1,
            args=MagicMock(),
            run_id="run_002",
            skill_dir=Path("/tmp"),
            agent_id="test-agent",
            environment=env,
        )

        assert ctx.environment == env
        assert ctx.agent_id == "test-agent"


class TestOpenClawParallelAgentId:
    """OpenClaw agent id suffixes for ThreadPoolExecutor workers."""

    def setup_method(self):
        from benchmark import _reset_openclaw_parallel_worker_slots_for_testing

        _reset_openclaw_parallel_worker_slots_for_testing()

    def test_single_worker_unchanged(self):
        from benchmark import _openclaw_agent_id_for_parallel_worker

        base = "evobench-openai-foo"
        assert _openclaw_agent_id_for_parallel_worker(base, 1) == base

    def test_same_thread_stable_slot(self):
        from benchmark import _openclaw_agent_id_for_parallel_worker

        a = _openclaw_agent_id_for_parallel_worker("base", 4)
        b = _openclaw_agent_id_for_parallel_worker("base", 4)
        assert a == b == "base-w0"

    def test_three_threads_three_distinct_ids(self):
        from benchmark import (
            _openclaw_agent_id_for_parallel_worker,
            _reset_openclaw_parallel_worker_slots_for_testing,
        )

        _reset_openclaw_parallel_worker_slots_for_testing()
        barrier = threading.Barrier(3)
        ids: list[str] = []
        lock = threading.Lock()

        def run():
            barrier.wait()
            aid = _openclaw_agent_id_for_parallel_worker("evobench-model", 3)
            with lock:
                ids.append(aid)

        threads = [threading.Thread(target=run) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == 3
        assert len(set(ids)) == 3
        assert set(ids) == {"evobench-model-w0", "evobench-model-w1", "evobench-model-w2"}


class TestConcurrentFutures:
    """Test concurrent.futures patterns used in benchmark."""

    def test_thread_pool_execution(self):
        results = []
        lock = threading.Lock()

        def worker(n):
            time.sleep(0.01)
            with lock:
                results.append(n)
            return n * 2

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(worker, i): i for i in range(8)}
            completed = list(concurrent.futures.as_completed(futures))

        assert len(completed) == 8
        assert len(results) == 8

    def test_exception_handling_in_workers(self):
        def failing_worker(n):
            if n == 3:
                raise ValueError("Worker failed at n=3")
            return n

        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(failing_worker, i): i for i in range(5)}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except ValueError as e:
                    errors.append(str(e))

        assert len(errors) == 1
        assert "n=3" in errors[0]

    def test_cancellation_on_keyboard_interrupt(self):
        results = []

        def slow_worker(n):
            time.sleep(10)
            results.append(n)
            return n

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        futures = {executor.submit(slow_worker, i): i for i in range(5)}

        for future in futures:
            if not future.done():
                future.cancel()

        executor.shutdown(wait=False)
        assert len(results) == 0


class TestProgressTracking:
    """Test progress tracking in parallel execution."""

    def test_task_count_matches_submitted(self):
        submitted = []
        completed = []

        def tracked_worker(task_id):
            submitted.append(task_id)
            time.sleep(0.01)
            completed.append(task_id)
            return task_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(tracked_worker, f"task_{i}"): f"task_{i}" for i in range(12)}
            for future in concurrent.futures.as_completed(futures):
                future.result()

        assert len(submitted) == 12
        assert len(completed) == 12
        assert set(submitted) == set(completed)


class TestTaskResultAggregation:
    def test_store_task_result_rolls_up_usage_and_subscores(self):
        from benchmark import _store_task_result
        from lib_grading import GradeResult

        results = {}
        _store_task_result(
            results,
            "task_01_test",
            GradeResult(
                task_id="task_01_test",
                score=0.5,
                max_score=1.0,
                grading_type="automated",
                breakdown={},
                notes="",
                sub_problem_scores=[0.5, 1.0],
            ),
            {
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                    "cache_read_tokens": 2,
                    "cache_write_tokens": 1,
                    "request_count": 1,
                    "cost_usd": 0.1,
                },
                "execution_time": 1.5,
                "workspace": "/tmp/run1",
            },
        )
        _store_task_result(
            results,
            "task_01_test",
            GradeResult(
                task_id="task_01_test",
                score=1.0,
                max_score=1.0,
                grading_type="automated",
                breakdown={},
                notes="",
                sub_problem_scores=[1.0, 1.0],
            ),
            {
                "usage": {
                    "input_tokens": 4,
                    "output_tokens": 6,
                    "total_tokens": 10,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 3,
                    "request_count": 2,
                    "cost_usd": 0.25,
                },
                "execution_time": 2.0,
                "workspace": "/tmp/run2",
            },
        )

        task_result = results["task_01_test"]
        assert task_result["usage"]["input_tokens"] == 14
        assert task_result["usage"]["output_tokens"] == 11
        assert task_result["usage"]["total_tokens"] == 25
        assert task_result["usage"]["cache_read_tokens"] == 2
        assert task_result["usage"]["cache_write_tokens"] == 4
        assert task_result["usage"]["request_count"] == 3
        assert task_result["usage"]["cost_usd"] == 0.35
        assert task_result["usage"]["total_cost_usd"] == 0.35
        assert task_result["usage"]["total_execution_time_seconds"] == 3.5
        assert task_result["sub_problem_scores"] == [1.0, 1.0]
        assert task_result["workspace"] == "/tmp/run2"


class TestWorkerIsolation:
    """Test that workers don't interfere with each other."""

    def test_independent_file_writes(self, tmp_path):
        results_dir = tmp_path / "results"
        results_dir.mkdir()

        def write_isolated(task_id, value):
            task_file = results_dir / f"{task_id}.json"
            time.sleep(0.01)
            task_file.write_text(json.dumps({"task_id": task_id, "value": value}))
            return value

        expected = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(8):
                task_id = f"task_{i}"
                value = i * 10
                expected[task_id] = value
                futures.append(executor.submit(write_isolated, task_id, value))

            for future in concurrent.futures.as_completed(futures):
                future.result()

        written = {}
        for f in results_dir.glob("*.json"):
            data = json.loads(f.read_text())
            written[data["task_id"]] = data["value"]

        assert written == expected


class TestBenchmarkIntegration:
    """Integration tests for parallel benchmark functionality."""

    def test_worker_count_parameter(self):
        from benchmark import _parse_args

        with patch("sys.argv", ["benchmark.py", "--model", "test/model", "--workers", "8"]):
            args = _parse_args()
            assert args.workers == 8

    def test_environment_parameter(self):
        from benchmark import _parse_args

        with patch(
            "sys.argv", ["benchmark.py", "--model", "test/model", "--environment", "docker"]
        ):
            args = _parse_args()
            assert args.environment == "docker"

    def test_default_workers(self):
        from benchmark import _parse_args

        with patch("sys.argv", ["benchmark.py", "--model", "test/model"]):
            args = _parse_args()
            assert args.workers == 4

    def test_default_environment(self):
        from benchmark import _parse_args

        with patch("sys.argv", ["benchmark.py", "--model", "test/model"]):
            args = _parse_args()
            assert args.environment == "local"

    def test_no_progress_flag(self):
        from benchmark import _parse_args

        with patch("sys.argv", ["benchmark.py", "--model", "test/model", "--no-progress"]):
            args = _parse_args()
            assert args.no_progress is True

    def test_default_mode_all(self):
        from benchmark import _parse_args

        with patch("sys.argv", ["benchmark.py", "--model", "test/model"]):
            args = _parse_args()
            assert args.mode == "all"

    def test_mode_preskill(self):
        from benchmark import _parse_args

        with patch(
            "sys.argv",
            ["benchmark.py", "--model", "test/model", "--mode", "preskill"],
        ):
            args = _parse_args()
            assert args.mode == "preskill"

    def test_main_all_runs_baseline_preskill_postskill(self, tmp_path):
        from argparse import Namespace

        import benchmark
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )

        args = Namespace(
            model="test/model",
            runtime="nanobot",
            mode="all",
            suite="all",
            output_dir=str(tmp_path),
            timeout_multiplier=1.0,
            runs=1,
            judge=None,
            verbose=False,
            no_fail_fast=False,
            workers=1,
            environment="local",
            docker_image="evoclawbench/runtime",
            no_progress=True,
        )

        loader = MagicMock()
        loader.load_all_tasks.return_value = [task]
        run_modes = []

        def fake_run_single_mode(*, mode, **kwargs):
            run_modes.append(mode)
            return {"task_01_test": {"mean_score": 0.25, "usage": {"total_tokens": 10}}}

        def fake_run_preskill_mode(**kwargs):
            run_modes.append("preskill")
            return {
                "task_01_test": {
                    "mean_score": 0.75,
                    "usage": {"total_tokens": 8},
                    "end_to_end_usage": {"total_tokens": 18},
                    "created_skills": [{"name": "preskill-skill"}],
                }
            }

        def fake_run_postskill_mode(**kwargs):
            run_modes.append("postskill")
            return {
                "task_01_test": {
                    "mean_score": 0.8,
                    "first_pass_mean_score": 0.3,
                    "usage": {"total_tokens": 7},
                    "end_to_end_usage": {"total_tokens": 20},
                    "created_skills": [{"name": "postskill-skill"}],
                }
            }

        with patch("benchmark._parse_args", return_value=args):
            with patch("benchmark.TaskLoader", return_value=loader):
                with patch("benchmark._next_run_id", return_value="0001"):
                    with patch("benchmark._run_single_mode", side_effect=fake_run_single_mode):
                        with patch(
                            "benchmark._run_preskill_mode", side_effect=fake_run_preskill_mode
                        ):
                            with patch(
                                "benchmark._run_postskill_mode", side_effect=fake_run_postskill_mode
                            ):
                                with patch(
                                    "benchmark.aggregate_three_mode_metrics",
                                    return_value={"execution_only": {"mean_scores": {}}},
                                ) as mock_metrics:
                                    with patch("benchmark._log_metrics_summary") as mock_summary:
                                        with patch("benchmark.save_trajectories"):
                                            benchmark.main()

        assert run_modes == ["baseline", "preskill", "postskill"]
        mock_metrics.assert_called_once()
        kwargs = mock_metrics.call_args.kwargs
        assert set(kwargs) == {"baseline_results", "preskill_results", "postskill_results"}
        assert kwargs["preskill_results"]["task_01_test"]["created_skills"] == [
            {"name": "preskill-skill"}
        ]
        mock_summary.assert_called_once_with({"execution_only": {"mean_scores": {}}})

    def test_run_preskill_mode_uses_author_then_execution(self, tmp_path):
        from argparse import Namespace

        from benchmark import _run_preskill_mode
        from lib_grading import GradeResult
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )
        args = Namespace(
            model="test/model",
            runtime="nanobot",
            timeout_multiplier=1.0,
            runs=1,
            judge=None,
            verbose=False,
            workers=1,
            environment="local",
            docker_image="evoclawbench/runtime",
            show_progress=False,
        )
        modes = []

        def mock_execute_task(**kwargs):
            mode = kwargs["mode"]
            modes.append(mode)
            workspace = tmp_path / mode
            workspace.mkdir(parents=True, exist_ok=True)
            if mode == "preskill_author":
                skill = workspace / "skills" / "custom"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("---\nname: custom\n---\n\nBody.")
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {"total_tokens": 10, "cost_usd": 0.1},
                "workspace": str(workspace),
                "timed_out": False,
                "execution_time": 1.0,
                "skill_mutation_violation": False,
            }

        with patch("benchmark.execute_task", side_effect=mock_execute_task):
            with patch("benchmark.grade_task") as mock_grade:
                mock_grade.return_value = GradeResult(
                    task_id="task_01_test",
                    score=1.0,
                    max_score=1.0,
                    grading_type="automated",
                    breakdown={},
                    notes="",
                )
                with patch("benchmark.get_recorder"):
                    with patch("benchmark.start_recording"):
                        with patch("benchmark.end_recording"):
                            with patch("benchmark.record_transcript"):
                                with patch("benchmark.record_workspace_files"):
                                    with patch("benchmark.record_grading"):
                                        result = _run_preskill_mode(
                                            tasks_to_run=[task],
                                            args=args,
                                            run_id="0001",
                                            skill_dir=tmp_path,
                                            agent_id=None,
                                            run_start_ts="2026_01_01_00_00_00",
                                        )

        assert modes == ["preskill_author", "preskill_execute"]
        assert mock_grade.call_count == 1
        entry = result["task_01_test"]
        assert entry["mean_score"] == pytest.approx(1.0)
        assert entry["created_skills"][0]["name"] == "custom"
        assert entry["end_to_end_usage"]["total_tokens"] == 20

    def test_run_postskill_mode_uses_first_summary_second(self, tmp_path):
        from argparse import Namespace

        from benchmark import _run_postskill_mode
        from lib_grading import GradeResult
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )
        args = Namespace(
            model="test/model",
            runtime="nanobot",
            timeout_multiplier=1.0,
            runs=1,
            judge=None,
            verbose=False,
            workers=1,
            environment="local",
            docker_image="evoclawbench/runtime",
            show_progress=False,
        )
        modes = []

        def mock_execute_task(**kwargs):
            mode = kwargs["mode"]
            modes.append(mode)
            workspace = tmp_path / mode
            (workspace / "outputs").mkdir(parents=True, exist_ok=True)
            (workspace / "outputs" / "result.json").write_text("{}")
            if mode == "postskill_summary":
                skill = workspace / "skills" / "summary"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("---\nname: summary\n---\n\nBody.")
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {"total_tokens": 10, "cost_usd": 0.1},
                "workspace": str(workspace),
                "timed_out": False,
                "execution_time": 1.0,
                "skill_mutation_violation": False,
            }

        grades = [
            GradeResult(
                task_id="task_01_test",
                score=0.25,
                max_score=1.0,
                grading_type="automated",
                breakdown={"a": 0.25},
                notes="",
            ),
            GradeResult(
                task_id="task_01_test",
                score=0.75,
                max_score=1.0,
                grading_type="automated",
                breakdown={"a": 0.75},
                notes="",
            ),
        ]

        with patch("benchmark.execute_task", side_effect=mock_execute_task):
            with patch("benchmark.grade_task", side_effect=grades) as mock_grade:
                with patch("benchmark.get_recorder"):
                    with patch("benchmark.start_recording"):
                        with patch("benchmark.end_recording"):
                            with patch("benchmark.record_transcript"):
                                with patch("benchmark.record_workspace_files"):
                                    with patch("benchmark.record_grading"):
                                        result = _run_postskill_mode(
                                            tasks_to_run=[task],
                                            args=args,
                                            run_id="0001",
                                            skill_dir=tmp_path,
                                            agent_id=None,
                                            run_start_ts="2026_01_01_00_00_00",
                                        )

        assert modes == ["postskill_first", "postskill_summary", "postskill_second"]
        assert mock_grade.call_count == 2
        assert (tmp_path / "postskill_first" / ".evoclawbench" / "first_run_context.json").exists()
        entry = result["task_01_test"]
        assert entry["first_pass_mean_score"] == pytest.approx(0.25)
        assert entry["second_pass_mean_score"] == pytest.approx(0.75)
        assert entry["second_vs_first_delta"] == pytest.approx(0.5)


class TestExecuteSingleTaskRun:
    """Test _execute_single_task_run function."""

    def test_execute_single_run_returns_tuple(self):
        from benchmark import TaskRunContext, _execute_single_task_run
        from lib_tasks import Task

        mock_args = MagicMock()
        mock_args.model = "test/model"
        mock_args.judge = None
        mock_args.verbose = False

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )

        ctx = TaskRunContext(
            task=task,
            mode="baseline",
            run_idx=0,
            args=mock_args,
            run_id="run_001",
            skill_dir=Path("/tmp"),
            agent_id=None,
        )

        with patch("benchmark.execute_task") as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {},
                "workspace": "/tmp/workspace",
                "timed_out": False,
                "execution_time": 10.0,
            }
            with patch("benchmark.grade_task") as mock_grade:
                from lib_grading import GradeResult

                mock_grade.return_value = GradeResult(
                    task_id="task_01_test",
                    score=1.0,
                    max_score=1.0,
                    grading_type="automated",
                    breakdown={},
                    notes="",
                )
                with patch("benchmark.get_recorder"):
                    with patch("benchmark.start_recording"):
                        with patch("benchmark.end_recording"):
                            with patch("benchmark.record_transcript"):
                                with patch("benchmark.record_workspace_files"):
                                    with patch("benchmark.record_grading"):
                                        with patch("benchmark.record_error"):
                                            with patch(
                                                "benchmark.scan_created_skills", return_value=[]
                                            ):
                                                result = _execute_single_task_run(ctx)

        assert result is not None
        task_result, run_idx, grade, exec_result = result
        assert task_result == task
        assert run_idx == 0
        assert grade.score == 1.0


class TestParallelExecutionFix:
    """Test that verifies true parallel execution (not sequential)."""

    def test_single_thread_pool_for_multiple_tasks(self):
        """Verify that all tasks share a single ThreadPoolExecutor, not one per task."""
        execution_times = []
        lock = threading.Lock()

        def slow_task(task_id, delay=0.1):
            time.sleep(delay)
            with lock:
                execution_times.append((task_id, time.time()))
            return task_id

        tasks = [f"task_{i}" for i in range(4)]
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(slow_task, task_id): task_id for task_id in tasks}
            for future in concurrent.futures.as_completed(futures):
                future.result()

        total_time = time.time() - start_time

        assert len(execution_times) == 4
        assert (
            total_time < 0.5
        ), f"Expected parallel execution <0.5s, got {total_time:.2f}s (sequential detected)"

    def test_run_contexts_contain_environment_when_specified(self):
        """Test that TaskRunContext properly stores the environment object."""
        from benchmark import TaskRunContext

        mock_env = LocalEnvironment()
        mock_task = MagicMock()

        ctx = TaskRunContext(
            task=mock_task,
            mode="baseline",
            run_idx=0,
            args=MagicMock(),
            run_id="run_001",
            skill_dir=Path("/tmp"),
            agent_id=None,
            environment=mock_env,
        )

        assert ctx.environment is mock_env
        assert isinstance(ctx.environment, LocalEnvironment)

    def test_multiple_tasks_run_in_parallel_with_single_executor(self):
        """Test that 4 tasks with 4 workers run truly in parallel."""
        from benchmark import TaskRunContext

        execution_order = []
        lock = threading.Lock()
        barrier = threading.Barrier(4)

        def fast_task(ctx):
            barrier.wait()
            with lock:
                execution_order.append(("start", ctx.task.task_id, time.time()))
            time.sleep(0.05)
            with lock:
                execution_order.append(("end", ctx.task.task_id, time.time()))
            return ctx.task.task_id

        mock_args = MagicMock()
        mock_args.model = "test/model"
        mock_args.judge = None
        mock_args.verbose = False
        mock_args.runtime = "nanobot"

        with patch("benchmark._execute_single_task_run", side_effect=fast_task):
            tasks = []
            contexts = []
            for i in range(4):
                mock_task = MagicMock()
                mock_task.task_id = f"task_{i}"

                ctx = TaskRunContext(
                    task=mock_task,
                    mode="baseline",
                    run_idx=0,
                    args=mock_args,
                    run_id="run_001",
                    skill_dir=Path("/tmp"),
                    agent_id=None,
                )
                contexts.append((ctx, mock_task))
                tasks.append(mock_task)

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(fast_task, ctx) for ctx, _ in contexts]
                concurrent.futures.wait(futures)

        assert len(execution_order) == 8
        starts = [e for e in execution_order if e[0] == "start"]
        assert len(starts) == 4
        time_diffs = [starts[i + 1][2] - starts[i][2] for i in range(len(starts) - 1)]
        max_diff = max(time_diffs) if time_diffs else 0
        assert max_diff < 0.05, f"Tasks started too far apart ({max_diff:.3f}s), not parallel"


class TestEnvironmentInContext:
    """Test that environment is properly passed to TaskRunContext."""

    def test_environment_passed_through_context(self):
        """Verify environment object flows through TaskRunContext to execution."""
        from benchmark import TaskRunContext

        env = LocalEnvironment()
        task = MagicMock()
        task.task_id = "test_task"

        args = MagicMock()
        args.model = "test/model"
        args.judge = None
        args.verbose = False

        ctx = TaskRunContext(
            task=task,
            mode="baseline",
            run_idx=0,
            args=args,
            run_id="run_001",
            skill_dir=Path("/tmp"),
            agent_id=None,
            environment=env,
        )

        assert ctx.environment is env

    def test_no_environment_means_local_execution(self):
        """When environment is None, execution should use subprocess (local)."""
        from benchmark import TaskRunContext

        task = MagicMock()
        ctx = TaskRunContext(
            task=task,
            mode="baseline",
            run_idx=0,
            args=MagicMock(),
            run_id="run_001",
            skill_dir=Path("/tmp"),
            agent_id=None,
            environment=None,
        )

        assert ctx.environment is None


class TestRunSingleModeIntegration:
    """Integration test to verify _run_single_mode creates environments correctly."""

    def test_environment_created_for_docker_mode(self, tmp_path):
        """Test that DockerEnvironment is created when --environment docker is specified."""
        from benchmark import _run_single_mode
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )

        args = MagicMock()
        args.model = "test/model"
        args.judge = None
        args.verbose = False
        args.runtime = "nanobot"
        args.timeout_multiplier = 1.0
        args.environment = "docker"
        args.docker_image = "evoclawbench/runtime"
        args.workers = 1
        args.runs = 1

        created_environments = []

        def mock_execute_task(**kwargs):
            env = kwargs.get("environment")
            created_environments.append(env)
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {},
                "workspace": str(tmp_path / "workspace"),
                "timed_out": False,
                "execution_time": 0.1,
            }

        fake_docker_env = MagicMock()

        with patch("benchmark.DockerEnvironment", return_value=fake_docker_env):
            with patch("benchmark.execute_task", side_effect=mock_execute_task):
                with patch("benchmark.grade_task") as mock_grade:
                    from lib_grading import GradeResult

                    mock_grade.return_value = GradeResult(
                        task_id="task_01_test",
                        score=1.0,
                        max_score=1.0,
                        grading_type="automated",
                        breakdown={},
                        notes="",
                    )
                    with patch("benchmark.get_recorder"):
                        with patch("benchmark.start_recording"):
                            with patch("benchmark.end_recording"):
                                with patch("benchmark.record_transcript"):
                                    with patch("benchmark.record_workspace_files"):
                                        with patch("benchmark.record_grading"):
                                            with patch(
                                                "benchmark.scan_created_skills", return_value=[]
                                            ):
                                                _run_single_mode(
                                                    tasks_to_run=[task],
                                                    mode="baseline",
                                                    args=args,
                                                    run_id="run_001",
                                                    skill_dir=tmp_path,
                                                    agent_id=None,
                                                    run_start_ts="2026_01_01_00_00_00",
                                                )

        assert (
            len(created_environments) == 1
        ), f"Expected 1 environment, got {len(created_environments)}"
        assert created_environments[0] is fake_docker_env
        assert isinstance(created_environments[0], LocalEnvironment) is False

    def test_parallel_tasks_use_single_executor(self, tmp_path):
        """Verify that multiple tasks are submitted to a single ThreadPoolExecutor."""
        from benchmark import _run_single_mode
        from lib_tasks import Task

        tasks = [
            Task(
                task_id=f"task_{i:02d}_test",
                name=f"Test Task {i}",
                category="test",
                grading_type="automated",
                timeout_seconds=120,
                workspace_files=[],
                prompt="Do something",
                expected_behavior="Works",
                grading_criteria=["done"],
            )
            for i in range(4)
        ]

        args = MagicMock()
        args.model = "test/model"
        args.judge = None
        args.verbose = False
        args.runtime = "nanobot"
        args.timeout_multiplier = 1.0
        args.environment = "local"
        args.docker_image = "evoclawbench/runtime"
        args.workers = 4
        args.runs = 1

        executor_instances = []

        def mock_execute_task(**kwargs):
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {},
                "workspace": str(tmp_path / "workspace"),
                "timed_out": False,
                "execution_time": 0.1,
            }

        original_thread_pool = concurrent.futures.ThreadPoolExecutor

        class InstrumentedExecutor(original_thread_pool):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                executor_instances.append(self)

        with patch("concurrent.futures.ThreadPoolExecutor", InstrumentedExecutor):
            with patch("benchmark.execute_task", side_effect=mock_execute_task):
                with patch("benchmark.grade_task") as mock_grade:
                    from lib_grading import GradeResult

                    mock_grade.return_value = GradeResult(
                        task_id="task_01_test",
                        score=1.0,
                        max_score=1.0,
                        grading_type="automated",
                        breakdown={},
                        notes="",
                    )
                    with patch("benchmark.get_recorder"):
                        with patch("benchmark.start_recording"):
                            with patch("benchmark.end_recording"):
                                with patch("benchmark.record_transcript"):
                                    with patch("benchmark.record_workspace_files"):
                                        with patch("benchmark.record_grading"):
                                            with patch(
                                                "benchmark.scan_created_skills", return_value=[]
                                            ):
                                                _run_single_mode(
                                                    tasks_to_run=tasks,
                                                    mode="baseline",
                                                    args=args,
                                                    run_id="run_001",
                                                    skill_dir=tmp_path,
                                                    agent_id=None,
                                                    run_start_ts="2026_01_01_00_00_00",
                                                )

        assert len(executor_instances) == 1, (
            f"Expected 1 ThreadPoolExecutor, got {len(executor_instances)} "
            "(each task creating its own executor = sequential execution)"
        )

    def test_run_single_mode_enables_live_when_show_progress_true(self, tmp_path):
        """Rich Live wraps execution when args.show_progress is True."""
        from benchmark import _run_single_mode
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )

        args = MagicMock()
        args.model = "test/model"
        args.judge = None
        args.verbose = False
        args.runtime = "nanobot"
        args.timeout_multiplier = 1.0
        args.environment = "local"
        args.docker_image = "evoclawbench/runtime"
        args.workers = 2
        args.runs = 1
        args.show_progress = True

        def mock_execute_task(**kwargs):
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {"cost_usd": 0.01},
                "workspace": str(tmp_path / "workspace"),
                "timed_out": False,
                "execution_time": 0.1,
            }

        with patch("benchmark.Live") as mock_live:
            mock_live.return_value.__enter__.return_value = None
            mock_live.return_value.__exit__.return_value = None
            with patch("benchmark.execute_task", side_effect=mock_execute_task):
                with patch("benchmark.grade_task") as mock_grade:
                    from lib_grading import GradeResult

                    mock_grade.return_value = GradeResult(
                        task_id="task_01_test",
                        score=1.0,
                        max_score=1.0,
                        grading_type="automated",
                        breakdown={},
                        notes="",
                    )
                    with patch("benchmark.get_recorder"):
                        with patch("benchmark.start_recording"):
                            with patch("benchmark.end_recording"):
                                with patch("benchmark.record_transcript"):
                                    with patch("benchmark.record_workspace_files"):
                                        with patch("benchmark.record_grading"):
                                            with patch(
                                                "benchmark.scan_created_skills", return_value=[]
                                            ):
                                                _run_single_mode(
                                                    tasks_to_run=[task],
                                                    mode="baseline",
                                                    args=args,
                                                    run_id="run_001",
                                                    skill_dir=tmp_path,
                                                    agent_id=None,
                                                    run_start_ts="2026_01_01_00_00_00",
                                                )

        mock_live.assert_called_once()
        _args, kwargs = mock_live.call_args
        assert kwargs.get("refresh_per_second") == 4
        assert _args[0] is not None

    def test_run_single_mode_skips_live_when_show_progress_false(self, tmp_path):
        from benchmark import _run_single_mode
        from lib_tasks import Task

        task = Task(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="Works",
            grading_criteria=["done"],
        )

        args = MagicMock()
        args.model = "test/model"
        args.judge = None
        args.verbose = False
        args.runtime = "nanobot"
        args.timeout_multiplier = 1.0
        args.environment = "local"
        args.docker_image = "evoclawbench/runtime"
        args.workers = 1
        args.runs = 1
        args.show_progress = False

        def mock_execute_task(**kwargs):
            return {
                "status": "success",
                "exit_code": 0,
                "transcript": [],
                "usage": {},
                "workspace": str(tmp_path / "w"),
                "timed_out": False,
                "execution_time": 0.05,
            }

        with patch("benchmark.Live") as mock_live:
            with patch("benchmark.execute_task", side_effect=mock_execute_task):
                with patch("benchmark.grade_task") as mock_grade:
                    from lib_grading import GradeResult

                    mock_grade.return_value = GradeResult(
                        task_id="task_01_test",
                        score=1.0,
                        max_score=1.0,
                        grading_type="automated",
                        breakdown={},
                        notes="",
                    )
                    with patch("benchmark.get_recorder"):
                        with patch("benchmark.start_recording"):
                            with patch("benchmark.end_recording"):
                                with patch("benchmark.record_transcript"):
                                    with patch("benchmark.record_workspace_files"):
                                        with patch("benchmark.record_grading"):
                                            with patch(
                                                "benchmark.scan_created_skills", return_value=[]
                                            ):
                                                _run_single_mode(
                                                    tasks_to_run=[task],
                                                    mode="baseline",
                                                    args=args,
                                                    run_id="run_001",
                                                    skill_dir=tmp_path,
                                                    agent_id=None,
                                                    run_start_ts="2026_01_01_00_00_00",
                                                )

        mock_live.assert_not_called()
