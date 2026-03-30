"""Tests for OpenClaw session transcript loading and workspace normalization."""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import lib_agent


class TestReadNdjsonTranscript:
    def test_reads_valid_lines(self, tmp_path):
        p = tmp_path / "t.jsonl"
        p.write_text(
            '{"type": "session", "cwd": "/a"}\n\n{"bad": }\n{"type": "x"}\n',
            encoding="utf-8",
        )
        rows = lib_agent._read_ndjson_transcript(p)
        assert len(rows) == 2
        assert rows[0]["type"] == "session"
        assert rows[1]["type"] == "x"

    def test_missing_file(self, tmp_path):
        p = tmp_path / "missing.jsonl"
        assert lib_agent._read_ndjson_transcript(p) == []


class TestOpenclawAgentSessionsDir:
    def test_normalizes_agent_id(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            lib_agent.Path,
            "home",
            classmethod(lambda cls: tmp_path),
        )
        d = lib_agent._openclaw_agent_sessions_dir("MyAgent:1")
        assert d == tmp_path / ".openclaw" / "agents" / "myagent-1" / "sessions"


class TestLoadOpenclawTranscript:
    def test_loads_exact_session_file_not_newest_mtime(self, tmp_path, monkeypatch):
        monkeypatch.setattr(lib_agent, "_openclaw_agent_sessions_dir", lambda aid: tmp_path)
        sid = "task_01_test_999"
        correct = tmp_path / f"{sid}.jsonl"
        correct.write_text(
            '{"type": "session", "cwd": "/expected"}\n',
            encoding="utf-8",
        )
        stale = tmp_path / "stale.jsonl"
        stale.write_text(
            '{"type": "session", "cwd": "/wrong"}\n',
            encoding="utf-8",
        )
        future = time.time() + 10_000
        os.utime(stale, (future, future))

        tr = lib_agent._load_openclaw_transcript("evobench-x", sid, time.time())
        assert len(tr) == 1
        assert tr[0]["cwd"] == "/expected"

    def test_retries_until_file_appears(self, tmp_path, monkeypatch):
        monkeypatch.setattr(lib_agent, "_openclaw_agent_sessions_dir", lambda aid: tmp_path)
        sid = "task_retry_1"
        target = tmp_path / f"{sid}.jsonl"

        def sleep_writes_file(_seconds: float) -> None:
            target.write_text(
                '{"type": "session", "cwd": "/delayed"}\n',
                encoding="utf-8",
            )

        monkeypatch.setattr(lib_agent.time, "sleep", sleep_writes_file)
        tr = lib_agent._load_openclaw_transcript("evobench-y", sid, time.time())
        assert len(tr) == 1
        assert tr[0]["cwd"] == "/delayed"

    def test_empty_session_id_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(lib_agent, "_openclaw_agent_sessions_dir", lambda aid: tmp_path)
        assert lib_agent._load_openclaw_transcript("a", "  ", time.time()) == []

    def test_missing_file_after_retries_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(lib_agent, "_openclaw_agent_sessions_dir", lambda aid: tmp_path)
        monkeypatch.setattr(lib_agent.time, "sleep", lambda _s: None)
        tr = lib_agent._load_openclaw_transcript("evobench-z", "no_such_session_1", time.time())
        assert tr == []


class TestNormalizeTranscriptWorkspace:
    def test_overwrites_session_and_tool_result_cwd(self):
        transcript = [
            {"type": "session", "cwd": "/old", "id": "1"},
            {
                "type": "message",
                "message": {
                    "role": "toolResult",
                    "details": {"cwd": "/old2", "exitCode": 0},
                },
            },
        ]
        out = lib_agent._normalize_transcript_workspace(transcript, "/benchmark/workspace")
        assert out is transcript
        assert transcript[0]["cwd"] == "/benchmark/workspace"
        assert transcript[1]["message"]["details"]["cwd"] == "/benchmark/workspace"
        assert transcript[1]["message"]["details"]["exitCode"] == 0

    def test_skips_non_tool_result_messages(self):
        transcript = [
            {"type": "message", "message": {"role": "user", "content": "hi"}},
        ]
        lib_agent._normalize_transcript_workspace(transcript, "/w")
        assert "cwd" not in transcript[0]["message"]
