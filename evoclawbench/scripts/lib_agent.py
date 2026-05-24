"""
EvoClawBench agent execution helpers.

Supports OpenClaw and nanobot runtimes with baseline, preskill, and postskill phases.
Also supports Docker-based isolated execution via the Environment abstraction.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shlex
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from lib_model_pricing import enrich_usage_with_estimated_cost
from lib_tasks import Task

if TYPE_CHECKING:
    from lib_environment import Environment


logger = logging.getLogger(__name__)
_OPENCLAW_AGENT_CONFIG_LOCK = threading.Lock()

# Skill directory names seeded into workspaces and excluded from created-skill metrics.
SEEDED_SKILL_NAMES: frozenset[str] = frozenset({"skill-creator"})
BENCH_SEEDED_SKILL_NAMES = SEEDED_SKILL_NAMES


class ModelValidationError(Exception):
    pass


BASELINE_PREFIX = (
    "BASELINE MODE:\n"
    "Complete the task directly. You must NOT create, edit, or delete any skills or "
    "SKILL.md files. Solve each sub-problem independently from scratch, and focus on "
    "producing the required grader-visible outputs.\n\n"
)

PRESKILL_AUTHOR_PREFIX = (
    "PRESKILL AUTHOR MODE:\n"
    "Before solving the task, create a task-specific reusable skill. Read "
    "`skills/skill-creator/SKILL.md` and write one or more new skills under "
    "`skills/<skill-name>/SKILL.md` that would help an agent solve this task later. "
    "Do not produce the final task outputs in `outputs/`; this phase is only for "
    "skill authoring. Do not replace or delete `skills/skill-creator`.\n\n"
)

POSTSKILL_SUMMARY_PREFIX = (
    "POSTSKILL SUMMARY MODE:\n"
    "Summarize a reusable task-specific skill from a completed first run. Read "
    "`.evoclawbench/first_run_context.json` for the first run prompt, grading details, "
    "workspace output summary, and transcript summary. Create one or more skills under "
    "`skills/<skill-name>/SKILL.md` so a later agent can solve the same task more "
    "accurately and efficiently. Do not redo the task and do not write final task "
    "outputs in `outputs/`. Do not replace or delete `skills/skill-creator`.\n\n"
)

SKILL_REUSE_PREFIX = (
    "SKILL REUSE EXECUTION MODE:\n"
    "Complete the task using the existing skills in `skills/` when helpful. You must NOT "
    "create, edit, or delete any skills or SKILL.md files during this execution phase. "
    "Focus on producing the required grader-visible outputs and validate them before "
    "finishing.\n\n"
)

SKILL_AUTHOR_MODES: frozenset[str] = frozenset({"preskill_author", "postskill_summary"})
SKILL_REUSE_MODES: frozenset[str] = frozenset({"preskill_execute", "postskill_second"})
BASELINE_EXECUTION_MODES: frozenset[str] = frozenset({"baseline", "postskill_first"})


def slugify_model(model_id: str) -> str:
    return model_id.replace("/", "-").replace(".", "-").lower()


def _nanobot_agent_commands(
    skill_dir: Path, workspace: Path, prompt: str, config_path: Optional[Path] = None
) -> List[List[str]]:
    base_args = [
        "agent",
        "--workspace",
        str(workspace.resolve()),
    ]
    if config_path is not None:
        base_args.extend(["--config", str(config_path)])
    base_args.extend(
        [
            "--no-markdown",
            "--no-logs",
            "--message",
            prompt,
        ]
    )
    commands: List[List[str]] = []
    sibling_project = skill_dir.parent / "nanobot"
    if (sibling_project / "pyproject.toml").is_file() and (sibling_project / "nanobot").is_dir():
        commands.append(["uv", "run", "--project", str(sibling_project), "nanobot", *base_args])
    commands.extend(
        [
            ["nanobot", *base_args],
            ["python", "-m", "nanobot", *base_args],
        ]
    )
    return commands


def _raw_provider_value(raw_config: Dict[str, Any], provider: str, key: str) -> Any:
    provider_data = raw_config.get("providers", {}).get(provider, {})
    if not isinstance(provider_data, dict):
        return None
    snake_key = {
        "apiKey": "api_key",
        "apiBase": "api_base",
        "extraHeaders": "extra_headers",
    }.get(key, key)
    return (
        provider_data.get(key)
        if provider_data.get(key) is not None
        else provider_data.get(snake_key)
    )


def _load_raw_nanobot_config() -> Dict[str, Any]:
    config_path = Path.home() / ".nanobot" / "config.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_nanobot_benchmark_config(workspace: Path, model_id: str) -> Path:
    workspace = workspace.resolve()
    raw_config = _load_raw_nanobot_config()
    provider_names = [
        "custom",
        "azureOpenai",
        "azure_openai",
        "anthropic",
        "openai",
        "openrouter",
        "deepseek",
        "groq",
        "zhipu",
        "dashscope",
        "vllm",
        "ollama",
        "ovms",
        "gemini",
        "moonshot",
        "minimax",
        "mistral",
        "aihubmix",
        "siliconflow",
        "volcengine",
        "volcengineCodingPlan",
        "volcengine_coding_plan",
        "byteplus",
        "byteplusCodingPlan",
        "byteplus_coding_plan",
    ]
    providers: Dict[str, Dict[str, Any]] = {}
    for name in provider_names:
        api_key = _raw_provider_value(raw_config, name, "apiKey")
        api_base = _raw_provider_value(raw_config, name, "apiBase")
        extra_headers = _raw_provider_value(raw_config, name, "extraHeaders")
        if api_key or api_base or extra_headers:
            providers[name] = {
                "apiKey": api_key or "",
                "apiBase": api_base,
                "extraHeaders": extra_headers,
            }

    openai_provider = providers.setdefault("openai", {"apiKey": "", "apiBase": None})
    openai_provider["apiKey"] = (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("NANOBOT_PROVIDERS__OPENAI__API_KEY")
        or openai_provider.get("apiKey")
        or ""
    )
    openai_provider["apiBase"] = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or os.environ.get("NANOBOT_PROVIDERS__OPENAI__API_BASE")
        or openai_provider.get("apiBase")
    )

    config = {
        "agents": {
            "defaults": {
                "workspace": str(workspace),
                "model": model_id,
                "provider": "auto",
            }
        },
        "providers": providers,
    }
    config_path = workspace / ".evoclawbench" / "nanobot_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path


def get_mode_prefix(mode: str) -> str:
    if mode in BASELINE_EXECUTION_MODES:
        return BASELINE_PREFIX
    if mode == "preskill_author":
        return PRESKILL_AUTHOR_PREFIX
    if mode == "postskill_summary":
        return POSTSKILL_SUMMARY_PREFIX
    if mode in SKILL_REUSE_MODES:
        return SKILL_REUSE_PREFIX
    return ""


def _skill_creator_bundle_path(skill_dir: Path) -> Path:
    """Monorepo bundle: <repo>/skills/skill-creator adjacent to evoclawbench root."""
    return (skill_dir.parent / "skills" / "skill-creator").resolve()


def _copy_seeded_skill_creator(skill_dir: Path, workspace: Path) -> None:
    bundle = _skill_creator_bundle_path(skill_dir)
    if not bundle.is_dir():
        raise FileNotFoundError(
            f"Skill authoring requires skill-creator bundle at {bundle} "
            "(expected monorepo layout: <repo>/skills/skill-creator next to evoclawbench/)"
        )
    dest = workspace / "skills" / "skill-creator"
    shutil.copytree(bundle, dest, dirs_exist_ok=True)


def copy_generated_skills(
    source_workspace: str | Path,
    target_workspace: str | Path,
    *,
    exclude_names: frozenset[str] = SEEDED_SKILL_NAMES,
) -> None:
    """Copy non-seeded skills from one task workspace into another."""
    source_skills = Path(source_workspace) / "skills"
    if not source_skills.is_dir():
        return
    target_skills = Path(target_workspace) / "skills"
    target_skills.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(source_skills.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name in exclude_names:
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        shutil.copytree(skill_dir, target_skills / skill_dir.name, dirs_exist_ok=True)


def _copy_first_run_context(source_workspace: str | Path, target_workspace: Path) -> None:
    source = Path(source_workspace) / ".evoclawbench" / "first_run_context.json"
    if not source.is_file():
        logger.warning("Postskill summary context missing: %s", source)
        return
    dest = target_workspace / ".evoclawbench" / "first_run_context.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())


def hash_skill_files(
    workspace_path: str | Path,
    *,
    exclude_names: frozenset[str] = SEEDED_SKILL_NAMES,
) -> Dict[str, str]:
    """Return sha256 hashes for all non-seeded files under workspace/skills."""
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    if not skills_dir.is_dir():
        return {}
    hashes: Dict[str, str] = {}
    for path in sorted(skills_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(skills_dir)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] in exclude_names:
            continue
        hashes[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def skills_mutated(before: Dict[str, str], after: Dict[str, str]) -> bool:
    """True when a reuse execution added, removed, or modified a skill file."""
    return before != after


# ---------------------------------------------------------------------------
# OpenClaw runtime
# ---------------------------------------------------------------------------


def ensure_openclaw_agent(agent_id: str, model_id: str, workspace_dir: Path) -> bool:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    with _OPENCLAW_AGENT_CONFIG_LOCK:
        try:
            list_result = subprocess.run(
                ["openclaw", "agents", "list"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            logger.error("openclaw CLI not found")
            return False

        if list_result.returncode == 0:
            existing = set()
            for line in list_result.stdout.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    name_part = line[2:].split()[0] if line[2:].strip() else ""
                    if name_part:
                        existing.add(name_part.lower())
            normalized = agent_id.replace(":", "-").lower()
            if agent_id.lower() in existing or normalized in existing:
                logger.info("Agent %s already exists", agent_id)
                return False

        logger.info("Creating OpenClaw agent %s", agent_id)
        try:
            add_result = subprocess.run(
                [
                    "openclaw",
                    "agents",
                    "add",
                    agent_id,
                    "--model",
                    model_id,
                    "--workspace",
                    str(workspace_dir),
                    "--non-interactive",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            logger.error("openclaw CLI not found")
            return False
        if add_result.returncode != 0:
            detail = add_result.stderr.strip() or add_result.stdout.strip()
            raise RuntimeError(f"Failed to create OpenClaw agent {agent_id}: {detail}")
    return True


def _reset_openclaw_agent_workspace(agent_id: str, model_id: str, workspace: Path) -> None:
    """Delete and recreate the agent so its workspace matches the task workspace."""
    workspace.mkdir(parents=True, exist_ok=True)
    with _OPENCLAW_AGENT_CONFIG_LOCK:
        try:
            delete_result = subprocess.run(
                ["openclaw", "agents", "delete", agent_id, "--force"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            logger.error("openclaw CLI not found")
            raise
        if delete_result.returncode != 0 and "Unknown agent id" not in delete_result.stderr:
            detail = delete_result.stderr.strip() or delete_result.stdout.strip()
            logger.warning("Failed to delete OpenClaw agent %s before reset: %s", agent_id, detail)
        try:
            add_result = subprocess.run(
                [
                    "openclaw",
                    "agents",
                    "add",
                    agent_id,
                    "--model",
                    model_id,
                    "--workspace",
                    str(workspace),
                    "--non-interactive",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            logger.error("openclaw CLI not found")
            raise
        if add_result.returncode != 0:
            detail = add_result.stderr.strip() or add_result.stdout.strip()
            raise RuntimeError(f"Failed to reset OpenClaw agent {agent_id}: {detail}")
        logger.info("Reset agent %s workspace to %s", agent_id, workspace)


def _openclaw_agent_dir(agent_id: str) -> Path:
    return Path.home() / ".openclaw" / "agents" / agent_id.replace(":", "-").lower()


def _openclaw_agent_sessions_dir(agent_id: str) -> Path:
    return _openclaw_agent_dir(agent_id) / "sessions"


def cleanup_openclaw_sessions(agent_id: str) -> None:
    sessions_dir = _openclaw_agent_sessions_dir(agent_id)
    if not sessions_dir.exists():
        return
    removed = 0
    for pattern in ("*.jsonl", "*.jsonl.lock", "*.ndjson"):
        for path in sessions_dir.rglob(pattern):
            try:
                path.unlink()
                removed += 1
            except OSError:
                pass
    store = sessions_dir / "sessions.json"
    if store.exists():
        try:
            store.unlink()
        except OSError:
            pass
    if removed:
        logger.info("Removed %s old session files for %s", removed, agent_id)


def _read_ndjson_transcript(path: Path) -> List[Dict[str, Any]]:
    """Load newline-delimited JSON objects from a transcript file."""
    transcript: List[Dict[str, Any]] = []
    if not path.is_file():
        return transcript
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            transcript.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return transcript


def _load_openclaw_transcript_legacy(agent_id: str, started_at: float) -> List[Dict[str, Any]]:
    """Previous heuristic: newest transcript by mtime. Available only when env is set."""
    sessions_dir = _openclaw_agent_sessions_dir(agent_id)
    if not sessions_dir.exists():
        return []

    candidates = list(sessions_dir.rglob("*.jsonl")) + list(sessions_dir.rglob("*.ndjson"))
    if not candidates:
        return []

    recent = [p for p in candidates if p.stat().st_mtime >= (started_at - 5.0)]
    pool = recent or candidates
    transcript_path = max(pool, key=lambda p: p.stat().st_mtime)
    return _read_ndjson_transcript(transcript_path)


def _load_openclaw_transcript(
    agent_id: str, session_id: str, started_at: float
) -> List[Dict[str, Any]]:
    """
    Load the OpenClaw session transcript for this run.

    Resolution order:
    1. Direct path: ``sessions/{session_id}.jsonl`` (used if OpenClaw ever names files
       after the --session-id flag).
    2. sessions.json index: OpenClaw writes a ``sessions.json`` file whose entries carry a
       ``sessionFile`` key (absolute path to the UUID-named ``.jsonl``) and a ``sessionId``
       matching the value passed to ``--session-id``.  We scan that index for a matching
       ``sessionId`` and load the referenced file.
    3. Legacy fallback: newest ``.jsonl`` by mtime (opt-in via
       ``EVOCLAW_OPENCLAW_TRANSCRIPT_LEGACY_FALLBACK=1``).
    """
    sid = session_id.strip()
    if not sid:
        logger.warning("OpenClaw transcript: empty session_id for agent %s", agent_id)
        return []

    sessions_dir = _openclaw_agent_sessions_dir(agent_id)

    # 1. Direct path — in case OpenClaw uses the session-id as the filename
    transcript_path = sessions_dir / f"{sid}.jsonl"
    attempts = 30
    sleep_s = 0.05
    for attempt in range(attempts):
        if transcript_path.is_file():
            data = _read_ndjson_transcript(transcript_path)
            if data:
                return data
        if attempt + 1 < attempts:
            time.sleep(sleep_s)

    # 2. sessions.json index — OpenClaw stores sessionFile -> absolute UUID path
    sessions_json = sessions_dir / "sessions.json"
    if sessions_json.is_file():
        try:
            index: Dict[str, Any] = json.loads(sessions_json.read_text(encoding="utf-8"))
            for entry in index.values():
                if not isinstance(entry, dict):
                    continue
                if entry.get("sessionId") == sid:
                    sf = entry.get("sessionFile", "")
                    if sf:
                        data = _read_ndjson_transcript(Path(sf))
                        if data:
                            return data
        except Exception as exc:
            logger.debug("OpenClaw transcript: error reading sessions.json: %s", exc)

    logger.warning(
        "OpenClaw transcript: missing or empty file for session %s under %s",
        sid,
        sessions_dir,
    )

    # 3. Legacy fallback (opt-in)
    legacy = os.environ.get("EVOCLAW_OPENCLAW_TRANSCRIPT_LEGACY_FALLBACK", "").strip().lower()
    if legacy in {"1", "true", "yes"}:
        logger.warning(
            "OpenClaw transcript: using EVOCLAW_OPENCLAW_TRANSCRIPT_LEGACY_FALLBACK loader"
        )
        return _load_openclaw_transcript_legacy(agent_id, started_at)
    return []


def _normalize_transcript_workspace(
    transcript: List[Dict[str, Any]], workspace: str
) -> List[Dict[str, Any]]:
    """Overwrite embedded cwd in session and toolResult events to match the benchmark workspace."""
    for event in transcript:
        if event.get("type") == "session":
            event["cwd"] = workspace
            continue
        if event.get("type") != "message":
            continue
        msg = event.get("message")
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "toolResult":
            continue
        details = msg.get("details")
        if isinstance(details, dict) and "cwd" in details:
            details["cwd"] = workspace
    return transcript


def execute_openclaw_task(
    *,
    task: Task,
    agent_id: str,
    model_id: str,
    run_id: str,
    timeout_multiplier: float,
    skill_dir: Path,
    mode: str = "baseline",
    verbose: bool = False,
    environment: Optional["Environment"] = None,
    workspace_root: Optional[Path] = None,
    source_skills_workspace: Optional[Path] = None,
    context_source_workspace: Optional[Path] = None,
) -> Dict[str, Any]:
    logger.info("[OpenClaw] Agent [%s] task: %s (mode=%s)", agent_id, task.task_id, mode)

    cleanup_openclaw_sessions(agent_id)
    start_time = time.time()
    workspace = prepare_workspace(
        skill_dir,
        run_id,
        task,
        mode,
        workspace_root=workspace_root,
        source_skills_workspace=source_skills_workspace,
        context_source_workspace=context_source_workspace,
    )
    skill_hash_before = hash_skill_files(workspace)

    if environment is None:
        _reset_openclaw_agent_workspace(agent_id, model_id, workspace)

    session_id = f"{task.task_id}_{int(time.time() * 1000)}"
    timeout_seconds = task.timeout_seconds * timeout_multiplier

    prompt = get_mode_prefix(mode) + task.prompt

    stdout, stderr = "", ""
    exit_code = -1
    timed_out = False

    cmd_result: Dict[str, Any] = {}
    try:
        if environment is not None:
            cmd = (
                f"openclaw agent --agent {agent_id} --session-id {session_id} --message '{prompt}'"
            )
            cmd_result = environment.execute(
                {"command": cmd},
                cwd=str(workspace),
                timeout=timeout_seconds,
            )
            stdout = cmd_result.get("output", "")
            stderr = cmd_result.get("exception_info", "")
            exit_code = cmd_result.get("returncode", -1)
        else:
            result = subprocess.run(
                [
                    "openclaw",
                    "agent",
                    "--agent",
                    agent_id,
                    "--session-id",
                    session_id,
                    "--message",
                    prompt,
                ],
                capture_output=True,
                text=True,
                cwd=str(workspace),
                timeout=timeout_seconds,
                check=False,
            )
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = _coerce(exc.stdout)
        stderr = _coerce(exc.stderr)
    except FileNotFoundError as exc:
        stderr = f"openclaw command not found: {exc}"

    transcript = _load_openclaw_transcript(agent_id, session_id, start_time)
    transcript = _normalize_transcript_workspace(transcript, str(workspace))
    usage = enrich_usage_with_estimated_cost(model_id, _extract_usage(transcript))
    execution_time = time.time() - start_time

    skill_hash_after = hash_skill_files(workspace)
    skill_mutation_violation = mode in SKILL_REUSE_MODES and skills_mutated(
        skill_hash_before, skill_hash_after
    )

    if mode in SKILL_AUTHOR_MODES:
        _verify_bench_skills_loaded(agent_id, workspace)

    status = "success"
    if timed_out:
        status = "timeout"
    elif not transcript or exit_code not in (0, -1):
        status = "error"

    return {
        "agent_id": agent_id,
        "task_id": task.task_id,
        "status": status,
        "transcript": transcript,
        "usage": usage,
        "workspace": str(workspace),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "execution_time": execution_time,
        "stdout": stdout,
        "stderr": stderr,
        "mode": mode,
        "skill_hash_before": skill_hash_before,
        "skill_hash_after": skill_hash_after,
        "skill_mutation_violation": skill_mutation_violation,
    }


# ---------------------------------------------------------------------------
# nanobot runtime
# ---------------------------------------------------------------------------


def execute_nanobot_task(
    *,
    task: Task,
    model_id: str,
    run_id: str,
    timeout_multiplier: float,
    skill_dir: Path,
    mode: str = "baseline",
    verbose: bool = False,
    environment: Optional["Environment"] = None,
    workspace_root: Optional[Path] = None,
    source_skills_workspace: Optional[Path] = None,
    context_source_workspace: Optional[Path] = None,
) -> Dict[str, Any]:
    logger.info("[nanobot] task: %s (mode=%s)", task.task_id, mode)

    start_time = time.time()
    workspace = prepare_workspace(
        skill_dir,
        run_id,
        task,
        mode,
        workspace_root=workspace_root,
        source_skills_workspace=source_skills_workspace,
        context_source_workspace=context_source_workspace,
    )
    skill_hash_before = hash_skill_files(workspace)
    timeout_seconds = task.timeout_seconds * timeout_multiplier

    prompt = get_mode_prefix(mode) + task.prompt
    config_path = _write_nanobot_benchmark_config(workspace, model_id)

    stdout, stderr = "", ""
    exit_code = -1
    timed_out = False

    if environment is not None:
        merged_env = os.environ.copy()
        merged_env["NANOBOT_WORKSPACE"] = str(workspace)
        if model_id:
            merged_env["NANOBOT_MODEL"] = model_id
            merged_env["NANOBOT_AGENTS__DEFAULTS__MODEL"] = model_id

        try:
            cmd = _nanobot_agent_commands(skill_dir, workspace, prompt, config_path)[0]
            cmd_result = environment.execute(
                {"command": shlex.join(cmd)},
                cwd=str(workspace),
                timeout=timeout_seconds,
            )
            stdout = cmd_result.get("output", "")
            stderr = cmd_result.get("exception_info", "")
            exit_code = cmd_result.get("returncode", -1)
        except Exception as exc:
            stderr = str(exc)
    else:
        env = os.environ.copy()
        env["NANOBOT_WORKSPACE"] = str(workspace)
        if model_id:
            env["NANOBOT_MODEL"] = model_id
            env["NANOBOT_AGENTS__DEFAULTS__MODEL"] = model_id

        cmds_to_try = _nanobot_agent_commands(skill_dir, workspace, prompt, config_path)

        for cmd in cmds_to_try:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(workspace),
                    timeout=timeout_seconds,
                    env=env,
                    check=False,
                )
                stdout = result.stdout
                stderr = result.stderr
                exit_code = result.returncode
                break
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                stdout = _coerce(exc.stdout)
                stderr = _coerce(exc.stderr)
                break
            except FileNotFoundError:
                continue
        else:
            stderr = "nanobot command not found (tried CLI and python -m)"

    transcript = _load_nanobot_transcript(workspace, stdout)
    usage = enrich_usage_with_estimated_cost(model_id, _extract_usage(transcript))
    execution_time = time.time() - start_time
    skill_hash_after = hash_skill_files(workspace)
    skill_mutation_violation = mode in SKILL_REUSE_MODES and skills_mutated(
        skill_hash_before, skill_hash_after
    )

    status = "success"
    if timed_out:
        status = "timeout"
    elif exit_code not in (0, -1):
        status = "error"

    return {
        "agent_id": f"nanobot-{slugify_model(model_id)}",
        "task_id": task.task_id,
        "status": status,
        "transcript": transcript,
        "usage": usage,
        "workspace": str(workspace),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "execution_time": execution_time,
        "stdout": stdout,
        "stderr": stderr,
        "mode": mode,
        "skill_hash_before": skill_hash_before,
        "skill_hash_after": skill_hash_after,
        "skill_mutation_violation": skill_mutation_violation,
    }


def _load_nanobot_transcript(workspace: Path, stdout: str) -> List[Dict[str, Any]]:
    """Load transcript from nanobot's workspace or parse from stdout."""
    session_dir = workspace / ".nanobot" / "sessions"
    if session_dir.exists():
        for f in sorted(session_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "messages" in data:
                    return [{"type": "message", "message": m} for m in data["messages"]]
            except (json.JSONDecodeError, OSError):
                continue

    if stdout.strip():
        return [
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": stdout}],
                },
            }
        ]
    return []


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _verify_bench_skills_loaded(agent_id: str, workspace: Path) -> None:
    """Log a warning if sessions.json shows that skill-creator was NOT in the system prompt.

    Called after a bench-mode task completes.  OpenClaw should have auto-discovered
    ``{workspace}/skills/skill-creator/SKILL.md`` and listed it under
    ``systemPromptReport.skills.entries`` in sessions.json.
    """
    sessions_dir = _openclaw_agent_sessions_dir(agent_id)
    sessions_json = sessions_dir / "sessions.json"
    if not sessions_json.is_file():
        logger.warning(
            "Bench skills check: sessions.json not found for agent %s — "
            "cannot confirm skill-creator was loaded from workspace %s",
            agent_id,
            workspace,
        )
        return

    try:
        index: Dict[str, Any] = json.loads(sessions_json.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Bench skills check: error reading sessions.json for %s: %s", agent_id, exc)
        return

    for entry in index.values():
        if not isinstance(entry, dict):
            continue
        report = entry.get("systemPromptReport") or {}
        skills_section = report.get("skills") or {}
        entries = skills_section.get("entries") or []
        loaded_names = {e.get("name") for e in entries if isinstance(e, dict)}
        if "skill-creator" in loaded_names:
            logger.debug(
                "Bench skills check OK: skill-creator found in system prompt for agent %s",
                agent_id,
            )
            return

    logger.warning(
        "Bench skills check: skill-creator NOT found in sessions.json for agent %s (workspace=%s). "
        "Verify that workspace/skills/skill-creator/ exists and OpenClaw scanned it.",
        agent_id,
        workspace,
    )


def prepare_workspace(
    skill_dir: Path,
    run_id: str,
    task: Task,
    mode: str = "baseline",
    workspace_root: Optional[Path] = None,
    source_skills_workspace: Optional[Path] = None,
    context_source_workspace: Optional[Path] = None,
) -> Path:
    """Prepare isolated workspace for a task run.

    Args:
        workspace_root: When provided, the workspace is created as
            ``workspace_root / "{task_id}_{mode}"``, overriding the default
            ``/tmp/evoclawbench/{run_id}/{task.task_id}_{mode}`` path.
    """
    if workspace_root is not None:
        workspace = workspace_root / f"{task.task_id}_{mode}"
    else:
        workspace = Path(f"/tmp/evoclawbench/{run_id}/{task.task_id}_{mode}")

    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    for file_spec in task.workspace_files:
        # Handle plain string entries: "assets/foo/bar.txt" -> copy to assets/foo/bar.txt
        if isinstance(file_spec, str):
            source = skill_dir / file_spec
            dest = workspace / file_spec
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if source.is_dir():
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                else:
                    dest.write_bytes(source.read_bytes())
            except FileNotFoundError:
                logger.error("Workspace file not found: %s", source)
                raise
            continue

        if "content" in file_spec:
            dest = workspace / file_spec["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(file_spec["content"])
            continue

        source_key = file_spec.get("source", file_spec.get("src", ""))
        dest_key = file_spec.get("dest", file_spec.get("dst", source_key))
        source = skill_dir / source_key
        dest = workspace / dest_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            if source.is_dir():
                shutil.copytree(source, dest, dirs_exist_ok=True)
            else:
                dest.write_bytes(source.read_bytes())
        except FileNotFoundError:
            logger.error("Workspace file not found: %s", source)
            raise

    # Pre-create outputs/ directory so agents don't need to create it themselves
    (workspace / "outputs").mkdir(exist_ok=True)

    if mode in SKILL_AUTHOR_MODES:
        _copy_seeded_skill_creator(skill_dir, workspace)

    if source_skills_workspace is not None:
        copy_generated_skills(source_skills_workspace, workspace)

    if context_source_workspace is not None:
        _copy_first_run_context(context_source_workspace, workspace)

    return workspace


def execute_task(
    *,
    task: Task,
    runtime: str,
    model_id: str,
    run_id: str,
    timeout_multiplier: float,
    skill_dir: Path,
    mode: str = "baseline",
    agent_id: Optional[str] = None,
    verbose: bool = False,
    environment: Optional["Environment"] = None,
    workspace_root: Optional[Path] = None,
    source_skills_workspace: Optional[Path] = None,
    context_source_workspace: Optional[Path] = None,
) -> Dict[str, Any]:
    """Unified task execution dispatcher for both runtimes.

    Args:
        environment: Optional Environment instance (e.g., DockerEnvironment) for isolated execution.
                    If provided, agent commands will be executed within this environment.
        workspace_root: When provided, task workspaces are created under this directory instead of
                    the default ``/tmp/evoclawbench/{run_id}/`` path.
    """
    if runtime == "openclaw":
        if agent_id is None:
            agent_id = f"evobench-{slugify_model(model_id)}"
        return execute_openclaw_task(
            task=task,
            agent_id=agent_id,
            model_id=model_id,
            run_id=run_id,
            timeout_multiplier=timeout_multiplier,
            skill_dir=skill_dir,
            mode=mode,
            verbose=verbose,
            environment=environment,
            workspace_root=workspace_root,
            source_skills_workspace=source_skills_workspace,
            context_source_workspace=context_source_workspace,
        )
    elif runtime == "nanobot":
        return execute_nanobot_task(
            task=task,
            model_id=model_id,
            run_id=run_id,
            timeout_multiplier=timeout_multiplier,
            skill_dir=skill_dir,
            mode=mode,
            verbose=verbose,
            environment=environment,
            workspace_root=workspace_root,
            source_skills_workspace=source_skills_workspace,
            context_source_workspace=context_source_workspace,
        )
    else:
        raise ValueError(f"Unknown runtime: {runtime}. Use 'openclaw' or 'nanobot'.")


def _coerce(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _extract_usage(transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "cost_usd": 0.0,
        "request_count": 0,
    }
    for entry in transcript:
        if entry.get("type") != "message":
            continue
        msg = entry.get("message", {})
        if msg.get("role") != "assistant":
            continue
        totals["request_count"] += 1
        usage = msg.get("usage", {})
        totals["input_tokens"] += int(usage.get("input", 0) or 0)
        totals["output_tokens"] += int(usage.get("output", 0) or 0)
        totals["total_tokens"] += int(usage.get("totalTokens", 0) or 0)
        totals["cache_read_tokens"] += int(usage.get("cacheRead", 0) or 0)
        totals["cache_write_tokens"] += int(usage.get("cacheWrite", 0) or 0)
        cost = usage.get("cost", {})
        totals["cost_usd"] += float(cost.get("total", 0.0) or 0.0)
    return totals
