"""Tests for lib_agent.py"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_agent import (
    BASELINE_PREFIX,
    EVOLUTION_PREFIX_BASE,
    _coerce,
    _extract_usage,
    get_mode_prefix,
    prepare_workspace,
    slugify_model,
)
from lib_tasks import Task


def _make_task(**overrides):
    defaults = dict(
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
    defaults.update(overrides)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# slugify_model
# ---------------------------------------------------------------------------


class TestSlugifyModel:
    def test_basic(self):
        assert slugify_model("anthropic/claude-sonnet-4") == "anthropic-claude-sonnet-4"

    def test_dots(self):
        assert slugify_model("openai/gpt-4.5") == "openai-gpt-4-5"

    def test_no_special_chars(self):
        assert slugify_model("mymodel") == "mymodel"


# ---------------------------------------------------------------------------
# get_mode_prefix
# ---------------------------------------------------------------------------


class TestGetModePrefix:
    def test_baseline(self):
        prefix = get_mode_prefix("baseline")
        assert prefix == BASELINE_PREFIX
        assert "must NOT create" in prefix

    def test_evolution(self):
        prefix = get_mode_prefix("evolution")
        assert EVOLUTION_PREFIX_BASE in prefix
        assert "encouraged" in prefix
        assert "CRITICAL PRIORITY ORDER" in prefix

    def test_bench(self):
        assert get_mode_prefix("bench") == ""

    def test_unknown(self):
        assert get_mode_prefix("unknown") == ""
        assert get_mode_prefix("") == ""


# ---------------------------------------------------------------------------
# _coerce
# ---------------------------------------------------------------------------


class TestCoerce:
    def test_none(self):
        assert _coerce(None) == ""

    def test_bytes(self):
        assert _coerce(b"hello") == "hello"

    def test_string(self):
        assert _coerce("hello") == "hello"

    def test_other(self):
        assert _coerce(42) == "42"


# ---------------------------------------------------------------------------
# _extract_usage
# ---------------------------------------------------------------------------


class TestExtractUsage:
    def test_empty_transcript(self):
        usage = _extract_usage([])
        assert usage["input_tokens"] == 0
        assert usage["request_count"] == 0

    def test_with_usage_data(self):
        transcript = [
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "hello"}],
                    "usage": {
                        "input": 100,
                        "output": 50,
                        "totalTokens": 150,
                        "cost": {"total": 0.01},
                    },
                },
            },
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "world"}],
                    "usage": {
                        "input": 200,
                        "output": 80,
                        "totalTokens": 280,
                        "cost": {"total": 0.02},
                    },
                },
            },
        ]
        usage = _extract_usage(transcript)
        assert usage["input_tokens"] == 300
        assert usage["output_tokens"] == 130
        assert usage["total_tokens"] == 430
        assert usage["cost_usd"] == pytest.approx(0.03)
        assert usage["request_count"] == 2

    def test_ignores_non_assistant(self):
        transcript = [
            {"type": "message", "message": {"role": "user", "content": "hi"}},
            {"type": "other_event"},
        ]
        usage = _extract_usage(transcript)
        assert usage["request_count"] == 0


# ---------------------------------------------------------------------------
# prepare_workspace
# ---------------------------------------------------------------------------


class TestPrepareWorkspace:
    def test_creates_workspace(self, tmp_path):
        task = _make_task()
        workspace = prepare_workspace(tmp_path, "run_001", task, "baseline")
        assert workspace.exists()
        assert workspace.is_dir()

    def test_copies_content_files(self, tmp_path):
        task = _make_task(
            workspace_files=[
                {"path": "config.json", "content": '{"key": "value"}'},
            ]
        )
        workspace = prepare_workspace(tmp_path, "run_002", task, "baseline")
        config = workspace / "config.json"
        assert config.exists()
        assert '"key"' in config.read_text()

    def test_copies_source_files(self, tmp_path):
        # Create a source asset file
        source_file = tmp_path / "assets" / "test.txt"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("test content")

        task = _make_task(
            workspace_files=[
                {"source": "assets/test.txt", "dest": "input.txt"},
            ]
        )
        workspace = prepare_workspace(tmp_path, "run_003", task, "baseline")
        assert (workspace / "input.txt").exists()
        assert (workspace / "input.txt").read_text() == "test content"

    def test_evolution_creates_skills_dir(self, tmp_path):
        task = _make_task()
        workspace = prepare_workspace(tmp_path, "run_004", task, "evolution")
        assert (workspace / "skills").exists()

    def test_baseline_no_skills_dir(self, tmp_path):
        task = _make_task()
        workspace = prepare_workspace(tmp_path, "run_005", task, "baseline")
        assert not (workspace / "skills").exists()

    def test_bench_copies_skill_creator_bundle(self, tmp_path):
        repo = tmp_path
        bundle = repo / "skills" / "skill-creator"
        bundle.mkdir(parents=True)
        (bundle / "SKILL.md").write_text("---\nname: skill-creator\n---\n\nBody.\n")
        skill_dir = repo / "evoclawbench"
        skill_dir.mkdir()

        task = _make_task()
        workspace = prepare_workspace(skill_dir, "run_bench_ok", task, "bench")
        seeded = workspace / "skills" / "skill-creator" / "SKILL.md"
        assert seeded.exists()
        assert "skill-creator" in seeded.read_text()

    def test_bench_missing_skill_creator_bundle_raises(self, tmp_path):
        skill_dir = tmp_path / "evoclawbench"
        skill_dir.mkdir(parents=True)
        task = _make_task()
        with pytest.raises(FileNotFoundError) as excinfo:
            prepare_workspace(skill_dir, "run_bench_missing", task, "bench")
        assert "skills/skill-creator" in str(excinfo.value)

    def test_cleans_existing_workspace(self, tmp_path):
        task = _make_task()
        # First run
        workspace = prepare_workspace(tmp_path, "run_006", task, "baseline")
        (workspace / "stale.txt").write_text("old")

        # Second run should clean
        workspace = prepare_workspace(tmp_path, "run_006", task, "baseline")
        assert not (workspace / "stale.txt").exists()

    def test_missing_source_file_raises(self, tmp_path):
        task = _make_task(
            workspace_files=[
                {"source": "assets/nonexistent.txt", "dest": "input.txt"},
            ]
        )
        with pytest.raises(FileNotFoundError):
            prepare_workspace(tmp_path, "run_007", task, "baseline")

    def test_nested_dest_path(self, tmp_path):
        task = _make_task(
            workspace_files=[
                {"path": "subdir/deep/config.json", "content": "{}"},
            ]
        )
        workspace = prepare_workspace(tmp_path, "run_008", task, "baseline")
        assert (workspace / "subdir" / "deep" / "config.json").exists()
