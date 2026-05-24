"""Tests for lib_agent.py"""

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_agent import (
    BASELINE_PREFIX,
    POSTSKILL_SUMMARY_PREFIX,
    PRESKILL_AUTHOR_PREFIX,
    SKILL_REUSE_PREFIX,
    _coerce,
    _extract_usage,
    _load_openclaw_transcript,
    _nanobot_agent_commands,
    _nanobot_timeout_seconds,
    _reset_openclaw_agent_workspace,
    _verify_bench_skills_loaded,
    copy_generated_skills,
    ensure_openclaw_agent,
    execute_nanobot_task,
    get_mode_prefix,
    hash_skill_files,
    prepare_workspace,
    skills_mutated,
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

    def test_preskill_author(self):
        prefix = get_mode_prefix("preskill_author")
        assert prefix == PRESKILL_AUTHOR_PREFIX
        assert "only for skill authoring" in prefix

    def test_postskill_summary(self):
        prefix = get_mode_prefix("postskill_summary")
        assert prefix == POSTSKILL_SUMMARY_PREFIX
        assert "first_run_context.json" in prefix

    def test_skill_reuse(self):
        assert get_mode_prefix("preskill_execute") == SKILL_REUSE_PREFIX
        assert get_mode_prefix("postskill_second") == SKILL_REUSE_PREFIX
        assert "must NOT" in SKILL_REUSE_PREFIX

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

    def test_baseline_no_skills_dir(self, tmp_path):
        task = _make_task()
        workspace = prepare_workspace(tmp_path, "run_005", task, "baseline")
        assert not (workspace / "skills").exists()

    def test_author_modes_copy_skill_creator_bundle(self, tmp_path):
        repo = tmp_path
        bundle = repo / "skills" / "skill-creator"
        bundle.mkdir(parents=True)
        (bundle / "SKILL.md").write_text("---\nname: skill-creator\n---\n\nBody.\n")
        skill_dir = repo / "evoclawbench"
        skill_dir.mkdir()

        task = _make_task()
        for mode in ("preskill_author", "postskill_summary"):
            workspace = prepare_workspace(skill_dir, f"run_{mode}", task, mode)
            seeded = workspace / "skills" / "skill-creator" / "SKILL.md"
            assert seeded.exists()
            assert "skill-creator" in seeded.read_text()

    def test_author_mode_missing_skill_creator_bundle_raises(self, tmp_path):
        skill_dir = tmp_path / "evoclawbench"
        skill_dir.mkdir(parents=True)
        task = _make_task()
        with pytest.raises(FileNotFoundError) as excinfo:
            prepare_workspace(skill_dir, "run_missing", task, "preskill_author")
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

    def test_workspace_root_author_copies_skill_creator(self, tmp_path):
        """workspace_root parameter works correctly in author mode."""
        repo = tmp_path / "repo"
        bundle = repo / "skills" / "skill-creator"
        bundle.mkdir(parents=True)
        (bundle / "SKILL.md").write_text("---\nname: skill-creator\n---\n")
        skill_dir = repo / "evoclawbench"
        skill_dir.mkdir()

        custom_root = tmp_path / "workspaces" / "2026_03_31_bench" / "0031"
        task = _make_task()
        workspace = prepare_workspace(
            skill_dir, "ignored_run_id", task, "preskill_author", workspace_root=custom_root
        )
        assert workspace == custom_root / f"{task.task_id}_preskill_author"
        seeded = workspace / "skills" / "skill-creator" / "SKILL.md"
        assert seeded.exists()

    def test_reuse_workspace_copies_only_generated_skills(self, tmp_path):
        source = tmp_path / "source"
        seed = source / "skills" / "skill-creator"
        seed.mkdir(parents=True)
        (seed / "SKILL.md").write_text("---\nname: skill-creator\n---\n")
        custom = source / "skills" / "custom"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("---\nname: custom\n---\n\nBody.")

        target = tmp_path / "target"
        copy_generated_skills(source, target)

        assert not (target / "skills" / "skill-creator").exists()
        assert (target / "skills" / "custom" / "SKILL.md").exists()

    def test_prepare_workspace_reuse_copies_generated_skills(self, tmp_path):
        source = tmp_path / "source"
        custom = source / "skills" / "custom"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("---\nname: custom\n---\n\nBody.")

        task = _make_task()
        workspace = prepare_workspace(
            tmp_path,
            "run_reuse",
            task,
            "preskill_execute",
            source_skills_workspace=source,
        )

        assert (workspace / "skills" / "custom" / "SKILL.md").exists()

    def test_hash_skill_files_detects_mutation(self, tmp_path):
        skill = tmp_path / "skills" / "custom"
        skill.mkdir(parents=True)
        skill_md = skill / "SKILL.md"
        skill_md.write_text("---\nname: custom\n---\n\nBody.")

        before = hash_skill_files(tmp_path)
        assert skills_mutated(before, hash_skill_files(tmp_path)) is False

        skill_md.write_text("---\nname: custom\n---\n\nChanged.")
        after = hash_skill_files(tmp_path)
        assert skills_mutated(before, after) is True

    def test_hash_skill_files_ignores_seeded_skill_creator(self, tmp_path):
        seed = tmp_path / "skills" / "skill-creator"
        seed.mkdir(parents=True)
        skill_md = seed / "SKILL.md"
        skill_md.write_text("---\nname: skill-creator\n---\n\nBody.")

        before = hash_skill_files(tmp_path)
        skill_md.write_text("---\nname: skill-creator\n---\n\nChanged.")
        assert before == {}
        assert skills_mutated(before, hash_skill_files(tmp_path)) is False


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


# ---------------------------------------------------------------------------
# OpenClaw agent management
# ---------------------------------------------------------------------------


class TestOpenClawAgentManagement:
    class Result:
        def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def test_ensure_openclaw_agent_raises_on_add_failure(self, tmp_path, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if cmd == ["openclaw", "agents", "list"]:
                return self.Result(0, stdout="Agents:\n")
            return self.Result(2, stderr="bad model")

        monkeypatch.setattr("lib_agent.subprocess.run", fake_run)

        with pytest.raises(RuntimeError, match="bad model"):
            ensure_openclaw_agent("agent-a", "bad/model", tmp_path)

        assert calls[-1][0:3] == ["openclaw", "agents", "add"]

    def test_reset_openclaw_agent_workspace_raises_on_add_failure(self, tmp_path, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if cmd[2] == "delete":
                return self.Result(0)
            return self.Result(1, stderr="config write failed")

        monkeypatch.setattr("lib_agent.subprocess.run", fake_run)

        with pytest.raises(RuntimeError, match="config write failed"):
            _reset_openclaw_agent_workspace("agent-a", "model-a", tmp_path)

        assert [cmd[2] for cmd in calls] == ["delete", "add"]


# ---------------------------------------------------------------------------
# nanobot runtime
# ---------------------------------------------------------------------------


class TestNanobotRuntime:
    class Result:
        def __init__(self, returncode: int = 0, stdout: str = "done", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def test_execute_nanobot_task_uses_current_agent_cli(self, tmp_path, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return self.Result()

        monkeypatch.setattr("lib_agent.subprocess.run", fake_run)

        task = _make_task(prompt="Summarize logs")
        result = execute_nanobot_task(
            task=task,
            model_id="openai/gpt-5.4-mini",
            run_id="run_001",
            timeout_multiplier=1.0,
            skill_dir=tmp_path,
        )

        assert result["status"] == "success"
        assert calls
        cmd, kwargs = calls[0]
        assert cmd[:2] == ["nanobot", "agent"]
        assert "run" not in cmd
        assert "--workspace" in cmd
        assert "--config" in cmd
        assert "--message" in cmd
        config_path = Path(cmd[cmd.index("--config") + 1])
        config = json.loads(config_path.read_text())
        assert config["agents"]["defaults"]["model"] == "openai/gpt-5.4-mini"
        assert config["agents"]["defaults"]["workspace"] == str(config_path.parents[1])
        assert kwargs["env"]["NANOBOT_AGENTS__DEFAULTS__MODEL"] == "openai/gpt-5.4-mini"
        assert kwargs["env"]["NANOBOT_MODEL"] == "openai/gpt-5.4-mini"

    def test_execute_nanobot_task_applies_timeout_floor(self, tmp_path, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return self.Result()

        monkeypatch.setattr("lib_agent.subprocess.run", fake_run)

        task = _make_task(prompt="Handle generated case", timeout_seconds=10)
        result = execute_nanobot_task(
            task=task,
            model_id="openai/qwen3.6-plus",
            run_id="run_001",
            timeout_multiplier=1.0,
            skill_dir=tmp_path,
        )

        assert result["status"] == "success"
        assert calls[0][1]["timeout"] == _nanobot_timeout_seconds(10, 1.0)
        assert calls[0][1]["timeout"] == 600

    def test_nanobot_agent_commands_prefer_sibling_project(self, tmp_path):
        repo = tmp_path / "repo"
        skill_dir = repo / "evoclawbench"
        nanobot_dir = repo / "nanobot"
        (nanobot_dir / "nanobot").mkdir(parents=True)
        (nanobot_dir / "pyproject.toml").write_text("[project]\nname = 'nanobot-ai'\n")

        commands = _nanobot_agent_commands(skill_dir, tmp_path / "workspace", "hello")

        assert commands[0][:4] == ["uv", "run", "--project", str(nanobot_dir)]
        assert commands[0][4:6] == ["nanobot", "agent"]
        assert commands[1][:2] == ["nanobot", "agent"]
