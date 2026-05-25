"""Integration tests: validate all task files load correctly and assets exist."""

import ast
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_tasks import TaskLoader

TASKS_DIR = Path(__file__).parent.parent / "tasks"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
SKILL_ROOT = Path(__file__).parent.parent


class TestAllTasksLoad:
    """Verify every task_*.md file loads without errors."""

    @pytest.fixture(scope="class")
    def loader(self):
        return TaskLoader(TASKS_DIR)

    @pytest.fixture(scope="class")
    def all_tasks(self, loader):
        tasks = loader.load_all_tasks()
        assert len(tasks) >= 9, f"Expected at least 9 tasks, got {len(tasks)}"
        return tasks

    def test_all_tasks_have_ids(self, all_tasks):
        for task in all_tasks:
            assert task.task_id, f"Task missing id: {task.file_path}"
            assert task.task_id.startswith("task_"), f"Bad task_id format: {task.task_id}"

    def test_all_tasks_have_names(self, all_tasks):
        for task in all_tasks:
            assert task.name, f"Task {task.task_id} missing name"

    def test_all_tasks_have_categories(self, all_tasks):
        for task in all_tasks:
            assert task.category, f"Task {task.task_id} missing category"

    def test_all_tasks_have_prompts(self, all_tasks):
        for task in all_tasks:
            assert task.prompt, f"Task {task.task_id} has empty prompt"
            assert len(task.prompt) >= 10, f"Task {task.task_id} prompt too short"

    def test_all_tasks_have_expected_behavior(self, all_tasks):
        for task in all_tasks:
            # sanity check may not have detailed behavior
            if task.task_id == "task_00_sanity":
                continue
            assert task.expected_behavior, f"Task {task.task_id} missing expected_behavior"

    def test_all_tasks_have_grading_criteria(self, all_tasks):
        for task in all_tasks:
            assert len(task.grading_criteria) >= 1, f"Task {task.task_id} has no grading criteria"

    def test_valid_grading_types(self, all_tasks):
        valid_types = {"automated", "llm_judge", "hybrid"}
        for task in all_tasks:
            assert (
                task.grading_type in valid_types
            ), f"Task {task.task_id} has invalid grading_type: {task.grading_type}"

    def test_reasonable_timeouts(self, all_tasks):
        for task in all_tasks:
            assert (
                10 <= task.timeout_seconds <= 1800
            ), f"Task {task.task_id} has unreasonable timeout: {task.timeout_seconds}"

    def test_unique_task_ids(self, all_tasks):
        ids = [t.task_id for t in all_tasks]
        assert len(ids) == len(set(ids)), f"Duplicate task IDs found: {ids}"


class TestAutomatedChecks:
    """Verify automated grading code compiles and defines grade()."""

    @pytest.fixture(scope="class")
    def tasks_with_checks(self):
        loader = TaskLoader(TASKS_DIR)
        tasks = loader.load_all_tasks()
        return [t for t in tasks if t.automated_checks]

    def test_all_grading_code_compiles(self, tasks_with_checks):
        for task in tasks_with_checks:
            code = self._extract_code(task.automated_checks)
            assert code, f"Task {task.task_id}: no Python code block found in automated checks"
            try:
                ast.parse(code)
            except SyntaxError as e:
                pytest.fail(f"Task {task.task_id}: grading code has syntax error: {e}")

    def test_all_grading_code_defines_grade(self, tasks_with_checks):
        for task in tasks_with_checks:
            code = self._extract_code(task.automated_checks)
            if not code:
                continue
            namespace = {}
            exec(code, namespace)
            assert "grade" in namespace, f"Task {task.task_id}: no 'grade' function defined"
            assert callable(namespace["grade"]), f"Task {task.task_id}: 'grade' is not callable"

    def test_grade_returns_dict(self, tasks_with_checks):
        """Call grade() with empty transcript and a temp workspace to verify it returns dict."""
        for task in tasks_with_checks:
            code = self._extract_code(task.automated_checks)
            if not code:
                continue
            namespace = {}
            exec(code, namespace)
            grade_func = namespace.get("grade")
            if not grade_func:
                continue
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                try:
                    result = grade_func([], tmpdir)
                except Exception:
                    # Some grade functions may fail with empty data; that's ok
                    continue
                assert isinstance(
                    result, dict
                ), f"Task {task.task_id}: grade() returned {type(result)}, expected dict"
                # All values should be numeric
                for key, val in result.items():
                    assert isinstance(val, (int, float)), (
                        f"Task {task.task_id}: grade()['{key}'] = {val} "
                        f"({type(val)}), expected number"
                    )

    def _extract_code(self, text):
        if not text:
            return ""
        match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
        return match.group(1) if match else ""


class TestSubProblems:
    """Verify tasks 01-08 have sub-problems."""

    @pytest.fixture(scope="class")
    def core_tasks(self):
        loader = TaskLoader(TASKS_DIR)
        tasks = loader.load_all_tasks()
        return {t.task_id: t for t in tasks if t.task_id != "task_00_sanity"}

    def test_core_tasks_have_sub_problems(self, core_tasks):
        for task_id, task in core_tasks.items():
            assert (
                task.num_sub_problems >= 3
            ), f"Task {task_id} has only {task.num_sub_problems} sub-problems (expected >= 3)"


class TestWorkspaceFiles:
    """Verify workspace file references point to existing assets."""

    @pytest.fixture(scope="class")
    def all_tasks(self):
        loader = TaskLoader(TASKS_DIR)
        return loader.load_all_tasks()

    def test_source_files_exist(self, all_tasks):
        for task in all_tasks:
            for file_spec in task.workspace_files:
                if isinstance(file_spec, str):
                    # Plain string: "assets/foo/bar.txt"
                    source_path = SKILL_ROOT / file_spec
                    assert (
                        source_path.exists()
                    ), f"Task {task.task_id}: workspace source file not found: {source_path}"
                    continue
                if "content" in file_spec:
                    continue
                source = file_spec.get("source", file_spec.get("src", ""))
                if not source:
                    continue
                source_path = SKILL_ROOT / source
                assert (
                    source_path.exists()
                ), f"Task {task.task_id}: workspace source file not found: {source_path}"


class TestAssetFiles:
    """Verify asset files are valid (parseable)."""

    def test_json_assets_valid(self):
        for json_file in ASSETS_DIR.rglob("*.json"):
            try:
                json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {json_file}: {e}")

    def test_python_assets_compile(self):
        for py_file in ASSETS_DIR.rglob("*.py"):
            try:
                ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_csv_assets_have_headers(self):
        for csv_file in ASSETS_DIR.rglob("*.csv"):
            content = csv_file.read_text(encoding="utf-8")
            lines = [line for line in content.strip().split("\n") if line.strip()]
            assert len(lines) >= 2, f"CSV {csv_file} has fewer than 2 lines (header + data)"

    def test_sql_assets_valid(self):
        for sql_file in ASSETS_DIR.rglob("*.sql"):
            content = sql_file.read_text(encoding="utf-8").upper()
            assert (
                "CREATE TABLE" in content or "ALTER TABLE" in content
            ), f"SQL file {sql_file} missing CREATE/ALTER TABLE"
