"""Quality gates for the generated domain-expansion tasks."""

import ast
import hashlib
import re
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_tasks import Task, TaskLoader

TASKS_DIR = Path(__file__).parent.parent / "tasks"
SKILL_ROOT = Path(__file__).parent.parent


def _task_number(task: Task) -> int:
    match = re.match(r"task_(\d+)_", task.task_id)
    return int(match.group(1)) if match else -1


def _extract_code(task: Task) -> str:
    match = re.search(r"```python\s*(.*?)\s*```", task.automated_checks or "", re.DOTALL)
    assert match, f"{task.task_id} is missing a Python automated check block"
    return match.group(1)


def _literal_assignment(code: str, name: str):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise AssertionError(f"Could not find {name} assignment")


@pytest.fixture(scope="module")
def all_tasks():
    return TaskLoader(TASKS_DIR).load_all_tasks()


@pytest.fixture(scope="module")
def generated_tasks(all_tasks):
    return [task for task in all_tasks if _task_number(task) >= 22]


def test_official_task_count_and_subproblem_count(all_tasks):
    official = [task for task in all_tasks if task.task_id != "task_00_sanity"]

    assert len(all_tasks) == 101
    assert len(official) == 100
    assert sum(task.num_sub_problems for task in official) == 502


def test_generated_tasks_have_family_metadata_and_fixtures(generated_tasks):
    assert len(generated_tasks) == 79

    for task in generated_tasks:
        assert task.frontmatter.get("task_family")
        assert task.frontmatter.get("grader_family")
        assert task.num_sub_problems == 5
        assert task.frontmatter.get("sub_problems") == 5
        for file_spec in task.workspace_files:
            assert isinstance(file_spec, str)
            assert (SKILL_ROOT / file_spec).is_file(), (task.task_id, file_spec)


def test_generated_tasks_have_distinct_grader_families(generated_tasks):
    families = {task.frontmatter.get("grader_family") for task in generated_tasks}
    normalized_hashes = set()

    for task in generated_tasks:
        code = _extract_code(task)
        ast.parse(code)
        normalized = re.sub(r"task_\d+_[a-z0-9_]+", "TASK_ID", code)
        normalized_hashes.add(hashlib.sha256(normalized.encode()).hexdigest())

    assert len(families) >= 16
    assert len(normalized_hashes) >= 16


def test_generated_graders_are_tamper_resistant(generated_tasks, tmp_path):
    representatives = {}
    for task in generated_tasks:
        family = task.frontmatter.get("grader_family")
        representatives.setdefault(family, task)

    assert len(representatives) >= 16

    for family, task in representatives.items():
        workspace = tmp_path / task.task_id
        output_dir = workspace / "outputs"
        output_dir.mkdir(parents=True)

        for file_spec in task.workspace_files:
            source = SKILL_ROOT / file_spec
            dest = workspace / file_spec
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            dest.write_text("tampered input fixture\n", encoding="utf-8")

        code = _extract_code(task)
        required_fields = _literal_assignment(code, "required_fields")
        numeric_fields = set(_literal_assignment(code, "numeric_fields"))
        dict_fields = set(_literal_assignment(code, "dict_fields"))
        bool_fields = set(_literal_assignment(code, "bool_fields"))
        text_fields = set(_literal_assignment(code, "text_fields"))

        fake_report = {}
        for field in required_fields:
            if field in numeric_fields:
                fake_report[field] = 0
            elif field in dict_fields:
                fake_report[field] = {}
            elif field in bool_fields:
                fake_report[field] = False
            elif field in text_fields:
                fake_report[field] = "tampered"
            else:
                fake_report[field] = []

        for case_index in range(1, 6):
            path = output_dir / f"case_{case_index:02d}_report.json"
            path.write_text(__import__("json").dumps(fake_report), encoding="utf-8")

        namespace = {}
        exec(code, namespace)
        scores = namespace["grade"]([], str(workspace))
        average_score = sum(float(value) for value in scores.values()) / len(scores)

        assert average_score < 1.0, f"{family} accepted tampered inputs for {task.task_id}"
