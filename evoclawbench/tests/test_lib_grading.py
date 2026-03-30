"""Tests for lib_grading.py"""

import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_grading import (
    GradeResult,
    _average_scores,
    _extract_grading_code,
    _extract_sub_problem_scores,
    _normalize_score_dict,
    grade_skill_quality,
    grade_task,
)
from lib_tasks import Task


def _make_task(**overrides):
    defaults = dict(
        task_id="task_test",
        name="Test",
        category="test",
        grading_type="automated",
        timeout_seconds=60,
        workspace_files=[],
        prompt="Do it",
        expected_behavior="It works",
        grading_criteria=["done"],
    )
    defaults.update(overrides)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# GradeResult
# ---------------------------------------------------------------------------

class TestGradeResult:
    def test_to_dict(self):
        gr = GradeResult(
            task_id="t1",
            score=0.75,
            max_score=1.0,
            grading_type="automated",
            breakdown={"a": 0.5, "b": 1.0},
            notes="ok",
            sub_problem_scores=[0.5, 1.0],
        )
        d = gr.to_dict()
        assert d["task_id"] == "t1"
        assert d["score"] == 0.75
        assert d["sub_problem_scores"] == [0.5, 1.0]

    def test_default_sub_problem_scores(self):
        gr = GradeResult("t1", 0.5, 1.0, "automated", {}, "")
        assert gr.sub_problem_scores == []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_average_scores(self):
        assert _average_scores({"a": 0.5, "b": 1.0}) == pytest.approx(0.75)
        assert _average_scores({}) == 0.0
        assert _average_scores({"a": "not_a_number"}) == 0.0

    def test_normalize_score_dict(self):
        result = _normalize_score_dict({"a": 0.5, "b": 1, "c": "bad"})
        assert result == {"a": 0.5, "b": 1.0}
        assert "c" not in result

    def test_extract_grading_code(self):
        task = _make_task(
            automated_checks=textwrap.dedent("""\
                Some text before

                ```python
                def grade(transcript, workspace_path):
                    return {"score": 1.0}
                ```

                Some text after
            """)
        )
        code = _extract_grading_code(task)
        assert "def grade" in code
        assert "return" in code

    def test_extract_grading_code_missing(self):
        task = _make_task(automated_checks=None)
        assert _extract_grading_code(task) == ""

        task2 = _make_task(automated_checks="no code block here")
        assert _extract_grading_code(task2) == ""

    def test_extract_sub_problem_scores(self):
        scores = {
            "sub_1_exists": 1.0,
            "sub_1_valid": 0.5,
            "sub_2_exists": 1.0,
            "sub_2_valid": 1.0,
            "overall": 0.8,
        }
        result = _extract_sub_problem_scores(scores)
        assert len(result) == 2
        assert result[0] == pytest.approx(0.75)  # avg(1.0, 0.5)
        assert result[1] == pytest.approx(1.0)   # avg(1.0, 1.0)

    def test_extract_sub_problem_scores_empty(self):
        assert _extract_sub_problem_scores({"overall": 0.5}) == []
        assert _extract_sub_problem_scores({}) == []


# ---------------------------------------------------------------------------
# grade_task (automated)
# ---------------------------------------------------------------------------

class TestGradeTaskAutomated:
    def test_successful_grading(self, tmp_path):
        task = _make_task(
            automated_checks=textwrap.dedent("""\
                ```python
                def grade(transcript, workspace_path):
                    from pathlib import Path
                    workspace = Path(workspace_path)
                    scores = {}
                    if (workspace / "output.txt").exists():
                        scores["file_created"] = 1.0
                    else:
                        scores["file_created"] = 0.0
                    return scores
                ```
            """)
        )

        # Create expected file
        (tmp_path / "output.txt").write_text("hello")

        result = grade_task(
            task=task,
            execution_result={"transcript": [], "workspace": str(tmp_path)},
            skill_dir=tmp_path,
        )
        assert result.score == pytest.approx(1.0)
        assert result.breakdown["file_created"] == 1.0

    def test_grading_file_missing(self, tmp_path):
        task = _make_task(
            automated_checks=textwrap.dedent("""\
                ```python
                def grade(transcript, workspace_path):
                    from pathlib import Path
                    if (Path(workspace_path) / "output.txt").exists():
                        return {"file_created": 1.0}
                    return {"file_created": 0.0}
                ```
            """)
        )

        result = grade_task(
            task=task,
            execution_result={"transcript": [], "workspace": str(tmp_path)},
            skill_dir=tmp_path,
        )
        assert result.score == pytest.approx(0.0)

    def test_no_grading_code(self, tmp_path):
        task = _make_task(automated_checks=None)
        result = grade_task(
            task=task,
            execution_result={"transcript": [], "workspace": str(tmp_path)},
            skill_dir=tmp_path,
        )
        assert result.score == 0.0
        assert "No automated grading code" in result.notes


# ---------------------------------------------------------------------------
# grade_skill_quality
# ---------------------------------------------------------------------------

class TestGradeSkillQuality:
    def test_empty_skills(self):
        assert grade_skill_quality([], _make_task()) == 0.0

    def test_good_skill(self):
        skills = [{
            "name": "data-transform",
            "frontmatter": {"name": "data-transform", "description": "Transforms data formats"},
            "content_length": 600,
            "has_scripts": True,
            "scripts_count": 1,
            "references_count": 1,
        }]
        score = grade_skill_quality(skills, _make_task())
        assert score > 0.8  # should score highly

    def test_minimal_skill(self):
        skills = [{
            "name": "stub",
            "frontmatter": {},
            "content_length": 50,
            "has_scripts": False,
            "scripts_count": 0,
            "references_count": 0,
        }]
        score = grade_skill_quality(skills, _make_task())
        assert score < 0.3  # should score low

    def test_multiple_skills_averaged(self):
        skills = [
            {
                "name": "good",
                "frontmatter": {"name": "good", "description": "A good skill"},
                "content_length": 600,
                "has_scripts": True,
                "scripts_count": 1,
                "references_count": 1,
            },
            {
                "name": "bad",
                "frontmatter": {},
                "content_length": 10,
                "has_scripts": False,
                "scripts_count": 0,
                "references_count": 0,
            },
        ]
        score = grade_skill_quality(skills, _make_task())
        good_only = grade_skill_quality([skills[0]], _make_task())
        bad_only = grade_skill_quality([skills[1]], _make_task())
        assert score == pytest.approx((good_only + bad_only) / 2, abs=0.01)
