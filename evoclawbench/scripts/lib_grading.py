"""
EvoClawBench grading engine.

Adapted from PinchBench with support for sub-problem grading and skill quality evaluation.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from lib_tasks import Task

logger = logging.getLogger(__name__)


DEFAULT_JUDGE_MODEL = "openrouter/anthropic/claude-opus-4.5"
DEFAULT_JUDGE_TIMEOUT_SECONDS = 180


@dataclass
class GradeResult:
    task_id: str
    score: float
    max_score: float
    grading_type: str
    breakdown: Dict[str, float]
    notes: str
    sub_problem_scores: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "score": self.score,
            "max_score": self.max_score,
            "grading_type": self.grading_type,
            "breakdown": self.breakdown,
            "notes": self.notes,
            "sub_problem_scores": self.sub_problem_scores,
        }


def grade_task(
    *,
    task: Task,
    execution_result: Dict[str, Any],
    skill_dir: Path,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    judge_timeout_seconds: float = DEFAULT_JUDGE_TIMEOUT_SECONDS,
    verbose: bool = False,
    runtime: str = "openclaw",
) -> GradeResult:
    grading_type = task.grading_type
    if verbose:
        logger.info("   [VERBOSE] Grading task %s with type: %s", task.task_id, grading_type)

    if grading_type == "automated":
        return _grade_automated(task, execution_result, verbose=verbose)
    if grading_type == "llm_judge":
        return _grade_llm_judge(
            task=task,
            execution_result=execution_result,
            judge_model=judge_model,
            judge_timeout_seconds=judge_timeout_seconds,
            skill_dir=skill_dir,
            verbose=verbose,
            runtime=runtime,
        )
    if grading_type == "hybrid":
        auto_result = _grade_automated(task, execution_result, verbose=verbose)
        llm_result = _grade_llm_judge(
            task=task,
            execution_result=execution_result,
            judge_model=judge_model,
            judge_timeout_seconds=judge_timeout_seconds,
            skill_dir=skill_dir,
            verbose=verbose,
            runtime=runtime,
        )
        return _combine_grades(task, auto_result, llm_result)
    raise ValueError(f"Unknown grading type: {grading_type}")


def grade_skill_quality(
    skills: List[Dict[str, Any]],
    task: Task,
    judge_model: str = DEFAULT_JUDGE_MODEL,
) -> float:
    """Evaluate quality of skills created by the agent. Returns score in [0, 1].

    For now, uses heuristic scoring. Can be extended to use LLM judge.
    """
    if not skills:
        return 0.0

    total_score = 0.0
    for skill in skills:
        score = 0.0

        # Has frontmatter with name and description
        fm = skill.get("frontmatter", {})
        if fm.get("name"):
            score += 0.2
        if fm.get("description"):
            score += 0.2

        # Has meaningful content (not just a stub)
        content_len = skill.get("content_length", 0)
        if content_len > 100:
            score += 0.2
        if content_len > 500:
            score += 0.1

        # Has scripts (executable components)
        if skill.get("has_scripts"):
            score += 0.2

        # Has references
        if skill.get("references_count", 0) > 0:
            score += 0.1

        total_score += min(score, 1.0)

    return round(total_score / len(skills), 4)


def _grade_automated(
    task: Task, execution_result: Dict[str, Any], verbose: bool = False
) -> GradeResult:
    grading_code = _extract_grading_code(task)
    if not grading_code:
        return GradeResult(
            task_id=task.task_id,
            score=0.0,
            max_score=1.0,
            grading_type="automated",
            breakdown={},
            notes="No automated grading code found",
        )

    namespace: Dict[str, Any] = {}
    exec(grading_code, namespace)
    grade_func = namespace.get("grade")
    if not callable(grade_func):
        return GradeResult(
            task_id=task.task_id,
            score=0.0,
            max_score=1.0,
            grading_type="automated",
            breakdown={},
            notes="Automated grading function missing",
        )

    scores = grade_func(
        execution_result.get("transcript", []),
        execution_result.get("workspace", ""),
    )
    if not isinstance(scores, dict):
        scores = {}

    if verbose:
        logger.info("   [VERBOSE] Automated scores: %s", scores)

    # Extract sub-problem scores if keys follow pattern "sub_N_*"
    sub_scores = _extract_sub_problem_scores(scores)

    total = _average_scores(scores)
    return GradeResult(
        task_id=task.task_id,
        score=total,
        max_score=1.0,
        grading_type="automated",
        breakdown=_normalize_score_dict(scores),
        notes="",
        sub_problem_scores=sub_scores,
    )


def _grade_llm_judge(
    *,
    task: Task,
    execution_result: Dict[str, Any],
    judge_model: str,
    judge_timeout_seconds: float,
    skill_dir: Path,
    verbose: bool = False,
    runtime: str = "openclaw",
) -> GradeResult:
    workspace_path = execution_result.get("workspace", "")
    workspace = Path(workspace_path) if workspace_path else None

    transcript_summary = _summarize_transcript(execution_result.get("transcript", []))
    rubric = task.llm_judge_rubric or _format_grading_criteria(task)
    workspace_context = _build_workspace_context(task, workspace) if workspace else ""
    prompt = _build_judge_prompt(task, transcript_summary, rubric, workspace_context)

    if verbose:
        logger.info("   [VERBOSE] Judge prompt (first 800 chars):\n%s", prompt[:800])

    try:
        response_text = _call_llm(judge_model, prompt, judge_timeout_seconds)
        if verbose:
            logger.info("   [VERBOSE] Judge raw response: %s", response_text[:500])
        scores = _parse_judge_response(response_text)
        total = float(scores.pop("total", _average_scores(scores)))
        notes = str(scores.pop("notes", ""))
        return GradeResult(
            task_id=task.task_id,
            score=max(0.0, min(1.0, total)),
            max_score=1.0,
            grading_type="llm_judge",
            breakdown=_normalize_score_dict(scores),
            notes=notes,
        )
    except Exception as exc:
        logger.warning("LLM judge failed for %s (runtime=%s): %s", task.task_id, runtime, exc)
        return GradeResult(
            task_id=task.task_id,
            score=0.0,
            max_score=1.0,
            grading_type="llm_judge",
            breakdown={},
            notes=f"LLM judge failed: {exc}",
        )


def _combine_grades(
    task: Task, auto_result: GradeResult, llm_result: GradeResult
) -> GradeResult:
    weights = task.grading_weights or {"automated": 0.5, "llm_judge": 0.5}
    auto_weight = float(weights.get("automated", 0.5))
    llm_weight = float(weights.get("llm_judge", 0.5))
    total_weight = auto_weight + llm_weight
    if total_weight <= 0:
        auto_weight = llm_weight = 0.5
        total_weight = 1.0
    combined_score = (auto_result.score * auto_weight + llm_result.score * llm_weight) / total_weight
    breakdown = {
        **{f"automated.{k}": v for k, v in auto_result.breakdown.items()},
        **{f"llm_judge.{k}": v for k, v in llm_result.breakdown.items()},
    }
    notes = " | ".join(filter(None, [auto_result.notes, llm_result.notes]))

    # Merge sub-problem scores (prefer automated if available)
    sub_scores = auto_result.sub_problem_scores or llm_result.sub_problem_scores

    return GradeResult(
        task_id=task.task_id,
        score=combined_score,
        max_score=1.0,
        grading_type="hybrid",
        breakdown=breakdown,
        notes=notes,
        sub_problem_scores=sub_scores,
    )


def _extract_grading_code(task: Task) -> str:
    if not task.automated_checks:
        return ""
    match = re.search(r"```python\s*(.*?)\s*```", task.automated_checks, re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def _average_scores(scores: Dict[str, Any]) -> float:
    values = [float(v) for v in scores.values() if isinstance(v, (int, float))]
    if not values:
        return 0.0
    return sum(values) / len(values)


def _normalize_score_dict(scores: Dict[str, Any]) -> Dict[str, float]:
    normalized: Dict[str, float] = {}
    for key, value in scores.items():
        try:
            normalized[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return normalized


def _extract_sub_problem_scores(scores: Dict[str, Any]) -> List[float]:
    """Extract per-sub-problem scores from keys like 'sub_1_correct', 'sub_2_correct', etc."""
    sub_groups: Dict[int, List[float]] = {}
    for key, value in scores.items():
        match = re.match(r"sub_(\d+)_", str(key))
        if match and isinstance(value, (int, float)):
            idx = int(match.group(1))
            sub_groups.setdefault(idx, []).append(float(value))

    if not sub_groups:
        return []

    result = []
    for idx in sorted(sub_groups.keys()):
        values = sub_groups[idx]
        result.append(sum(values) / len(values))
    return result


def _format_grading_criteria(task: Task) -> str:
    if not task.grading_criteria:
        return ""
    return "\n".join(f"- {criterion}" for criterion in task.grading_criteria)


def _summarize_transcript(transcript: List[Dict[str, Any]]) -> str:
    summary_parts: List[str] = []
    for event in transcript:
        if event.get("type") != "message":
            continue
        msg = event.get("message", {})
        role = msg.get("role")
        if role == "assistant":
            for item in msg.get("content", []):
                if item.get("type") == "toolCall":
                    summary_parts.append(
                        f"Tool: {item.get('name')}({json.dumps(item.get('arguments', {}))})"
                    )
        elif role == "toolResult":
            content = msg.get("content", [])
            if content:
                result_preview = str(content[0])[:200]
                summary_parts.append(f"Result: {result_preview}")
        elif role == "user":
            content = msg.get("content", [])
            if content:
                summary_parts.append(f"User: {content[0]}")
    return "\n".join(summary_parts)


def _build_judge_prompt(
    task: Task, transcript_summary: str, rubric: str, workspace_context: str = ""
) -> str:
    context_section = ""
    if workspace_context:
        context_section = f"## Agent Output Files\n{workspace_context}\n\n"
    return (
        "You are a grading function. Your ONLY job is to output a single JSON object.\n\n"
        "CRITICAL RULES:\n"
        "- Do NOT use any tools\n"
        "- Respond with ONLY a JSON object — nothing else\n\n"
        "Be a strict evaluator. Reserve 1.0 for genuinely excellent performance. "
        "An average acceptable completion should score around 0.6-0.7.\n\n"
        "## Task\n"
        f"{task.prompt}\n\n"
        "## Expected Behavior\n"
        f"{task.expected_behavior}\n\n"
        f"{context_section}"
        "## Agent Transcript (summarized)\n"
        f"{transcript_summary}\n\n"
        "## Grading Rubric\n"
        f"{rubric}\n\n"
        "Score each criterion from 0.0 to 1.0.\n\n"
        "Respond with ONLY this JSON structure (no markdown, no code fences):\n"
        '{"scores": {"criterion_name": 0.0}, "total": 0.0, "notes": "brief justification"}'
    )


def _parse_model_name(model: str) -> tuple:
    """Parse 'provider/model-name' → (provider, model_id).

    Examples:
        'openai/gpt-4o'           → ('openai', 'gpt-4o')
        'openrouter/anthropic/c'  → ('openrouter', 'anthropic/c')
        'gpt-4o'                  → ('openai', 'gpt-4o')
    """
    if "/" in model:
        provider, rest = model.split("/", 1)
        return provider.lower(), rest
    return "openai", model


def _call_llm(model: str, prompt: str, timeout: float) -> str:
    """Call an LLM via the openai-compatible SDK and return the response text."""
    import os

    import openai

    provider, model_id = _parse_model_name(model)

    if provider == "openrouter":
        client = openai.OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY", os.environ.get("OPENAI_API_KEY", "dummy")),
            base_url="https://openrouter.ai/api/v1",
            timeout=timeout,
        )
    else:
        client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", "dummy"),
            base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1"),
            timeout=timeout,
        )

    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content or ""


def _parse_judge_response(text: str) -> Dict[str, Any]:
    """Extract JSON scores dict from LLM judge response.

    Expects: {"scores": {...}, "total": float, "notes": str}
    Falls back to {"scores": {}, "total": 0.0} on parse failure.
    """
    text = text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Try to extract a JSON object via regex
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            logger.warning("LLM judge response contains no JSON: %s", text[:200])
            return {"total": 0.0, "notes": "unparseable response"}
        try:
            parsed = json.loads(match.group())
        except json.JSONDecodeError:
            logger.warning("LLM judge JSON extraction failed: %s", text[:200])
            return {"total": 0.0, "notes": "unparseable response"}

    if not isinstance(parsed, dict):
        return {"total": 0.0, "notes": "unexpected response type"}

    # Flatten: support both {"scores": {"k": v}, "total": x} and flat {"k": v, "total": x}
    result: Dict[str, Any] = {}
    if "scores" in parsed and isinstance(parsed["scores"], dict):
        result.update(parsed["scores"])
    else:
        result.update({k: v for k, v in parsed.items() if k not in ("total", "notes")})

    if "total" in parsed:
        result["total"] = parsed["total"]
    if "notes" in parsed:
        result["notes"] = parsed["notes"]

    return result


def _build_workspace_context(task: Task, workspace: Path, max_chars_per_file: int = 3000) -> str:
    """Read agent output files (and relevant source files) for judge context.

    Includes:
    - outputs/*.json  (the agent's produced results)
    - assets source files referenced in workspace_files (limited size)
    """
    parts: List[str] = []

    outputs_dir = workspace / "outputs"
    if outputs_dir.exists():
        for f in sorted(outputs_dir.glob("*.json"))[:10]:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")[:max_chars_per_file]
                parts.append(f"--- Output: {f.name} ---\n{content}")
            except OSError:
                pass

    # Include source/asset files (text only, limited size) for accuracy checks
    source_files = [
        wf for wf in task.workspace_files
        if isinstance(wf, str) and (wf.endswith(".txt") or wf.endswith(".py") or wf.endswith(".js") or wf.endswith(".go"))
    ]
    chars_budget = max_chars_per_file
    for wf in source_files[:5]:
        src = workspace / wf
        if src.exists():
            try:
                content = src.read_text(encoding="utf-8", errors="replace")[:chars_budget]
                parts.append(f"--- Source: {wf} ---\n{content}")
                chars_budget = max(500, chars_budget - len(content) // 2)
            except OSError:
                pass

    return "\n\n".join(parts)
