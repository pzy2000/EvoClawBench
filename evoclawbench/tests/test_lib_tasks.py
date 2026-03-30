"""Tests for lib_tasks.py"""

import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_tasks import SubProblem, Task, TaskLoader

# ---------------------------------------------------------------------------
# SubProblem
# ---------------------------------------------------------------------------

class TestSubProblem:
    def test_creation(self):
        sp = SubProblem(index=1, title="Parse CSV", description="Handle CSV files")
        assert sp.index == 1
        assert sp.title == "Parse CSV"
        assert sp.description == "Handle CSV files"
        assert sp.expected_output == ""

    def test_repr(self):
        sp = SubProblem(index=2, title="Parse JSON", description="Handle JSON files")
        assert "index=2" in repr(sp)
        assert "Parse JSON" in repr(sp)


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TestTask:
    def _make_task(self, **overrides):
        defaults = dict(
            task_id="task_01_test",
            name="Test Task",
            category="test",
            grading_type="automated",
            timeout_seconds=120,
            workspace_files=[],
            prompt="Do something",
            expected_behavior="It works",
            grading_criteria=["criterion 1"],
        )
        defaults.update(overrides)
        return Task(**defaults)

    def test_basic_creation(self):
        t = self._make_task()
        assert t.task_id == "task_01_test"
        assert t.num_sub_problems == 0

    def test_with_sub_problems(self):
        sps = [SubProblem(1, "A", "desc A"), SubProblem(2, "B", "desc B")]
        t = self._make_task(sub_problems=sps)
        assert t.num_sub_problems == 2

    def test_to_dict_has_required_fields(self):
        t = self._make_task(skill_category="data")
        d = t.to_dict()
        assert d["task_id"] == "task_01_test"
        assert d["num_sub_problems"] == 0
        assert d["skill_category"] == "data"
        assert "has_automated_checks" in d
        assert "frontmatter" in d

    def test_repr(self):
        t = self._make_task()
        assert "task_01_test" in repr(t)


# ---------------------------------------------------------------------------
# TaskLoader – section parsing
# ---------------------------------------------------------------------------

class TestTaskLoaderParsing:
    def setup_method(self):
        self.loader = TaskLoader(Path("/nonexistent"))

    def test_parse_sections(self):
        body = textwrap.dedent("""\
            ## Prompt

            Do the thing.

            ## Expected Behavior

            It should work.

            ## Grading Criteria

            - [ ] criterion one
            - [ ] criterion two
        """)
        sections = self.loader._parse_sections(body)
        assert "Prompt" in sections
        assert "Do the thing." in sections["Prompt"]
        assert "Expected Behavior" in sections
        assert "Grading Criteria" in sections

    def test_extract_grading_criteria(self):
        text = textwrap.dedent("""\
            - [ ] File created
            - [x] Content correct
            - [ ] Format valid
            Some other text
        """)
        criteria = self.loader._extract_grading_criteria(text)
        assert len(criteria) == 3
        assert "File created" in criteria
        assert "Content correct" in criteria

    def test_extract_grading_criteria_empty(self):
        assert self.loader._extract_grading_criteria("") == []
        assert self.loader._extract_grading_criteria("no criteria here") == []

    def test_extract_sub_problems(self):
        text = textwrap.dedent("""\
            ### Sub-Problem 1: Parse CSV
            - Input: users_01.csv
            - Output: outputs/users_01.json

            ### Sub-Problem 2: Parse JSON
            - Input: users_02.json
            - Output: outputs/users_02.json
        """)
        sps = self.loader._extract_sub_problems(text)
        assert len(sps) == 2
        assert sps[0].index == 1
        assert sps[0].title == "Parse CSV"
        assert "users_01.csv" in sps[0].description
        assert sps[1].index == 2
        assert sps[1].title == "Parse JSON"

    def test_extract_sub_problems_empty(self):
        assert self.loader._extract_sub_problems("") == []
        assert self.loader._extract_sub_problems("no sub-problems here") == []


# ---------------------------------------------------------------------------
# TaskLoader – load from file
# ---------------------------------------------------------------------------

class TestTaskLoaderFile:
    def test_load_task_from_file(self, tmp_path):
        task_file = tmp_path / "task_99_test.md"
        task_file.write_text(textwrap.dedent("""\
            ---
            id: task_99_test
            name: Test Task
            category: testing
            grading_type: automated
            timeout_seconds: 60
            skill_category: test_skill
            workspace_files: []
            ---

            ## Prompt

            Do the test task.

            ## Expected Behavior

            It passes.

            ## Sub-Problems

            ### Sub-Problem 1: First
            Description of first.

            ### Sub-Problem 2: Second
            Description of second.

            ## Grading Criteria

            - [ ] First done
            - [ ] Second done

            ## Automated Checks

            ```python
            def grade(transcript: list, workspace_path: str) -> dict:
                return {"first_done": 1.0, "second_done": 0.5}
            ```
        """))

        loader = TaskLoader(tmp_path)
        task = loader.load_task(task_file)

        assert task.task_id == "task_99_test"
        assert task.name == "Test Task"
        assert task.category == "testing"
        assert task.grading_type == "automated"
        assert task.timeout_seconds == 60
        assert task.skill_category == "test_skill"
        assert "Do the test task" in task.prompt
        assert len(task.grading_criteria) == 2
        assert task.num_sub_problems == 2
        assert task.sub_problems[0].title == "First"
        assert task.automated_checks is not None
        assert "def grade" in task.automated_checks

    def test_load_task_missing_frontmatter(self, tmp_path):
        task_file = tmp_path / "task_bad.md"
        task_file.write_text("No frontmatter here")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="No YAML frontmatter"):
            loader.load_task(task_file)

    def test_load_all_tasks(self, tmp_path):
        for i in range(3):
            (tmp_path / f"task_{i:02d}_test.md").write_text(textwrap.dedent(f"""\
                ---
                id: task_{i:02d}_test
                name: Test {i}
                category: test
                grading_type: automated
                timeout_seconds: 60
                workspace_files: []
                ---

                ## Prompt

                Task {i}.

                ## Expected Behavior

                Works.

                ## Grading Criteria

                - [ ] Done
            """))

        # Also create a non-task file that should be ignored
        (tmp_path / "README.md").write_text("# Not a task")

        loader = TaskLoader(tmp_path)
        tasks = loader.load_all_tasks()
        assert len(tasks) == 3
        assert tasks[0].task_id == "task_00_test"
