"""Tests for lib_agent.py"""

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_agent import (
    BASELINE_PREFIX,
    BENCH_PREFIX,
    EVOLUTION_PREFIX_BASE,
    _coerce,
    _extract_usage,
    _load_openclaw_transcript,
    _verify_bench_skills_loaded,
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
        prefix = get_mode_prefix("bench")
        assert prefix == BENCH_PREFIX
        assert "skill-creator" in prefix
        assert "repeating" in prefix.lower()

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
                        "cacheRead": 10,
                        "cacheWrite": 2,
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
        assert usage["cache_read_tokens"] == 10
        assert usage["cache_write_tokens"] == 2
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

    def test_uses_workspace_root_when_provided(self, tmp_path):
        """workspace_root overrides the /tmp/evoclawbench/... default path."""
        task = _make_task()
        custom_root = tmp_path / "custom_root"
        workspace = prepare_workspace(
            tmp_path, "run_009", task, "baseline", workspace_root=custom_root
        )
        assert workspace == custom_root / f"{task.task_id}_baseline"
        assert workspace.exists()

    def test_workspace_root_bench_copies_skill_creator(self, tmp_path):
        """workspace_root parameter works correctly in bench mode."""
        repo = tmp_path / "repo"
        bundle = repo / "skills" / "skill-creator"
        bundle.mkdir(parents=True)
        (bundle / "SKILL.md").write_text("---\nname: skill-creator\n---\n")
        skill_dir = repo / "evoclawbench"
        skill_dir.mkdir()

        custom_root = tmp_path / "workspaces" / "2026_03_31_bench" / "0031"
        task = _make_task()
        workspace = prepare_workspace(
            skill_dir, "ignored_run_id", task, "bench", workspace_root=custom_root
        )
        assert workspace == custom_root / f"{task.task_id}_bench"
        seeded = workspace / "skills" / "skill-creator" / "SKILL.md"
        assert seeded.exists()


# ---------------------------------------------------------------------------
# _load_openclaw_transcript
# ---------------------------------------------------------------------------


def _write_sessions_json(sessions_dir: Path, session_id: str, session_file: Path) -> None:
    """Helper: write a sessions.json that maps session_id to session_file."""
    data = {
        "agent:test-agent:main": {
            "sessionId": session_id,
            "sessionFile": str(session_file),
            "updatedAt": 9999999999999,
        }
    }
    (sessions_dir / "sessions.json").write_text(json.dumps(data))


def _make_transcript_lines(*entries: dict) -> str:
    return "\n".join(json.dumps(e) for e in entries)


_SAMPLE_TRANSCRIPT = [
    {"type": "session", "version": 3, "id": "sess-1", "timestamp": "2026-01-01T00:00:00Z"},
    {
        "type": "message",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": "done"}],
            "usage": {"input": 100, "output": 50, "totalTokens": 150, "cost": {"total": 0.01}},
        },
    },
]


class TestLoadOpenclawTranscript:
    def _make_agent_dir(self, tmp_path: Path, agent_id: str = "test-agent") -> Path:
        agent_dir = tmp_path / ".openclaw" / "agents" / agent_id / "sessions"
        agent_dir.mkdir(parents=True)
        return agent_dir

    def test_loads_direct_path_when_session_id_matches_filename(self, tmp_path, monkeypatch):
        """Direct {session_id}.jsonl path is found and returned."""
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_dir(tmp_path)
        session_id = "task_01_test_1700000000000"
        transcript_file = sessions_dir / f"{session_id}.jsonl"
        transcript_file.write_text(_make_transcript_lines(*_SAMPLE_TRANSCRIPT))

        result = _load_openclaw_transcript("test-agent", session_id, 0.0)
        assert len(result) == 2
        assert result[0]["type"] == "session"

    def test_loads_via_sessions_json_sessionfile(self, tmp_path, monkeypatch):
        """When {session_id}.jsonl is absent, sessions.json sessionFile is used."""
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_dir(tmp_path)
        session_id = "task_01_test_1700000000000"
        # OpenClaw writes a UUID-named file, NOT {session_id}.jsonl
        uuid_file = sessions_dir / "b55b39ec-08c5-44b6-bf59-54fb312ae93a.jsonl"
        uuid_file.write_text(_make_transcript_lines(*_SAMPLE_TRANSCRIPT))
        _write_sessions_json(sessions_dir, session_id, uuid_file)

        result = _load_openclaw_transcript("test-agent", session_id, 0.0)
        assert len(result) == 2
        assert result[1]["message"]["role"] == "assistant"

    def test_sessions_json_usage_data_extractable(self, tmp_path, monkeypatch):
        """Usage fields from UUID-backed transcript are parsed correctly."""
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_dir(tmp_path)
        session_id = "task_token_test_1700000000000"
        uuid_file = sessions_dir / "abc123.jsonl"
        uuid_file.write_text(_make_transcript_lines(*_SAMPLE_TRANSCRIPT))
        _write_sessions_json(sessions_dir, session_id, uuid_file)

        result = _load_openclaw_transcript("test-agent", session_id, 0.0)
        usage = _extract_usage(result)
        assert usage["input_tokens"] == 100
        assert usage["total_tokens"] == 150

    def test_returns_empty_when_no_file_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        self._make_agent_dir(tmp_path)
        result = _load_openclaw_transcript("test-agent", "nonexistent_session", 0.0)
        assert result == []

    def test_sessions_json_wrong_session_id_not_used(self, tmp_path, monkeypatch):
        """sessions.json entry with different sessionId is skipped."""
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_dir(tmp_path)
        uuid_file = sessions_dir / "wrong.jsonl"
        uuid_file.write_text(_make_transcript_lines(*_SAMPLE_TRANSCRIPT))
        _write_sessions_json(sessions_dir, "OTHER_SESSION", uuid_file)

        result = _load_openclaw_transcript("test-agent", "task_01_test_1700000000000", 0.0)
        assert result == []


# ---------------------------------------------------------------------------
# _verify_bench_skills_loaded
# ---------------------------------------------------------------------------


class TestVerifyBenchSkillsLoaded:
    def _make_agent_sessions(self, tmp_path: Path, agent_id: str = "test-agent") -> Path:
        sessions_dir = tmp_path / ".openclaw" / "agents" / agent_id / "sessions"
        sessions_dir.mkdir(parents=True)
        return sessions_dir

    def _write_sessions_json_with_skills(self, sessions_dir: Path, skill_names: list) -> None:
        entries = [{"name": n} for n in skill_names]
        data = {
            "agent:test-agent:main": {
                "sessionId": "some-session",
                "sessionFile": str(sessions_dir / "dummy.jsonl"),
                "systemPromptReport": {"skills": {"promptChars": 100, "entries": entries}},
            }
        }
        (sessions_dir / "sessions.json").write_text(json.dumps(data))

    def test_no_warning_when_skill_creator_present(self, tmp_path, monkeypatch, caplog):
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_sessions(tmp_path)
        workspace = tmp_path / "ws"
        self._write_sessions_json_with_skills(sessions_dir, ["skill-creator", "other-skill"])

        with caplog.at_level(logging.WARNING, logger="evoclawbench"):
            _verify_bench_skills_loaded("test-agent", workspace)

        assert not any(
            "skill-creator" in r.message for r in caplog.records if r.levelno >= logging.WARNING
        )

    def test_warns_when_skill_creator_missing(self, tmp_path, monkeypatch, caplog):
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        sessions_dir = self._make_agent_sessions(tmp_path)
        workspace = tmp_path / "ws"
        self._write_sessions_json_with_skills(sessions_dir, ["some-other-skill"])

        with caplog.at_level(logging.WARNING, logger="evoclawbench"):
            _verify_bench_skills_loaded("test-agent", workspace)

        assert any(
            "skill-creator" in r.message for r in caplog.records if r.levelno >= logging.WARNING
        )

    def test_warns_when_no_sessions_json(self, tmp_path, monkeypatch, caplog):
        monkeypatch.setattr("lib_agent.Path.home", lambda: tmp_path)
        self._make_agent_sessions(tmp_path)
        workspace = tmp_path / "ws"

        with caplog.at_level(logging.WARNING, logger="evoclawbench"):
            _verify_bench_skills_loaded("test-agent", workspace)

        assert any(
            "skill-creator" in r.message for r in caplog.records if r.levelno >= logging.WARNING
        )
