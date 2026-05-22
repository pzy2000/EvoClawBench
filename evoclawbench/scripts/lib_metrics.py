"""
EvoClawBench metrics computation.

Computes skill-evolution-specific metrics: fail2pass ratio, consistency,
efficiency gain, and skill quality scores.
"""

from __future__ import annotations

import logging
import re
import statistics
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional

import yaml

logger = logging.getLogger(__name__)


def compute_fail2pass(
    baseline_scores: Dict[str, float],
    evolution_scores: Dict[str, float],
) -> Dict[str, Any]:
    """Compute fail2pass ratio per task and overall.

    Args:
        baseline_scores: {task_id: mean_score} from baseline (no-skill) runs
        evolution_scores: {task_id: mean_score} from evolution (with-skill) runs

    Returns:
        Dict with per-task and overall fail2pass metrics.
    """
    per_task = {}
    all_task_ids = set(baseline_scores.keys()) | set(evolution_scores.keys())

    for task_id in sorted(all_task_ids):
        baseline = baseline_scores.get(task_id, 0.0)
        evolution = evolution_scores.get(task_id, 0.0)
        if baseline > 0:
            ratio = evolution / baseline
        elif evolution > 0:
            ratio = float("inf")
        else:
            ratio = 1.0
        per_task[task_id] = {
            "baseline_score": round(baseline, 4),
            "evolution_score": round(evolution, 4),
            "fail2pass": round(ratio, 4) if ratio != float("inf") else "inf",
        }

    baseline_mean = statistics.mean(baseline_scores.values()) if baseline_scores else 0.0
    evolution_mean = statistics.mean(evolution_scores.values()) if evolution_scores else 0.0

    if baseline_mean > 0:
        overall_ratio = evolution_mean / baseline_mean
    elif evolution_mean > 0:
        overall_ratio = float("inf")
    else:
        overall_ratio = 1.0

    return {
        "per_task": per_task,
        "overall": {
            "baseline_mean": round(baseline_mean, 4),
            "evolution_mean": round(evolution_mean, 4),
            "fail2pass": round(overall_ratio, 4) if overall_ratio != float("inf") else "inf",
        },
    }


def compute_consistency(sub_problem_scores: List[float]) -> float:
    """Compute consistency score for a task's sub-problem scores.

    consistency = 1 - CV (coefficient of variation)
    CV = std / mean

    Returns value in [0, 1] where 1 = perfectly consistent.
    Returns 1.0 if all scores are identical or only one score exists.
    """
    if len(sub_problem_scores) <= 1:
        return 1.0
    mean = statistics.mean(sub_problem_scores)
    if mean == 0:
        return 0.0
    std = statistics.stdev(sub_problem_scores)
    cv = std / mean
    return max(0.0, min(1.0, round(1.0 - cv, 4)))


def compute_efficiency_gain(
    baseline_usage: Dict[str, Any],
    evolution_usage: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute efficiency gain between baseline and evolution modes.

    Returns ratios > 1.0 if evolution mode is more efficient.
    """
    result = {}

    baseline_tokens = baseline_usage.get("total_tokens", 0)
    evolution_tokens = evolution_usage.get("total_tokens", 0)
    if evolution_tokens > 0:
        result["token_efficiency_gain"] = round(baseline_tokens / evolution_tokens, 4)
    else:
        result["token_efficiency_gain"] = None

    baseline_cost = baseline_usage.get("total_cost_usd", 0.0)
    evolution_cost = evolution_usage.get("total_cost_usd", 0.0)
    if evolution_cost > 0:
        result["cost_efficiency_gain"] = round(baseline_cost / evolution_cost, 4)
    else:
        result["cost_efficiency_gain"] = None

    baseline_time = baseline_usage.get("total_execution_time_seconds", 0.0)
    evolution_time = evolution_usage.get("total_execution_time_seconds", 0.0)
    if evolution_time > 0:
        result["time_efficiency_gain"] = round(baseline_time / evolution_time, 4)
    else:
        result["time_efficiency_gain"] = None

    return result


def _empty_usage() -> Dict[str, Any]:
    return {
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "total_execution_time_seconds": 0.0,
        "cost_usd": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "request_count": 0,
    }


def _sum_usage(results: Dict[str, Dict[str, Any]], key: str) -> Dict[str, Any]:
    total = _empty_usage()
    for payload in results.values():
        usage = payload.get(key) or {}
        if not usage and key == "end_to_end_usage":
            usage = payload.get("usage") or {}
        for usage_key in total:
            total[usage_key] += usage.get(usage_key, 0) or 0
    if total["total_cost_usd"] == 0.0 and total["cost_usd"]:
        total["total_cost_usd"] = total["cost_usd"]
    if total["cost_usd"] == 0.0 and total["total_cost_usd"]:
        total["cost_usd"] = total["total_cost_usd"]
    return total


def _mean_score(results: Dict[str, Dict[str, Any]], score_key: str = "mean_score") -> float:
    scores = [float(payload.get(score_key, 0.0) or 0.0) for payload in results.values()]
    return round(statistics.mean(scores), 4) if scores else 0.0


def _ratio(candidate: float, baseline: float) -> float | str:
    if baseline > 0:
        return round(candidate / baseline, 4)
    if candidate > 0:
        return "inf"
    return 1.0


def _collect_created_skills(results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    skills: List[Dict[str, Any]] = []
    for payload in results.values():
        created = payload.get("created_skills") or []
        if isinstance(created, list):
            skills.extend(created)
    return skills


def _mean_skill_quality(results: Dict[str, Dict[str, Any]]) -> float:
    scores = [
        float(payload.get("skill_quality_score", 0.0) or 0.0)
        for payload in results.values()
        if payload.get("skill_quality_score") is not None
    ]
    return round(statistics.mean(scores), 4) if scores else 0.0


def aggregate_three_mode_metrics(
    *,
    baseline_results: Dict[str, Dict[str, Any]],
    preskill_results: Dict[str, Dict[str, Any]],
    postskill_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate baseline, preskill, and postskill benchmark metrics."""
    baseline_score = _mean_score(baseline_results)
    preskill_score = _mean_score(preskill_results)
    postskill_score = _mean_score(postskill_results)

    baseline_exec_usage = _sum_usage(baseline_results, "usage")
    preskill_exec_usage = _sum_usage(preskill_results, "usage")
    postskill_exec_usage = _sum_usage(postskill_results, "usage")

    baseline_e2e_usage = _sum_usage(baseline_results, "end_to_end_usage")
    preskill_e2e_usage = _sum_usage(preskill_results, "end_to_end_usage")
    postskill_e2e_usage = _sum_usage(postskill_results, "end_to_end_usage")

    first_pass_mean = _mean_score(postskill_results, "first_pass_mean_score")
    second_pass_mean = postskill_score
    if first_pass_mean > 0:
        second_vs_first_ratio: float | str = round(second_pass_mean / first_pass_mean, 4)
    elif second_pass_mean > 0:
        second_vs_first_ratio = "inf"
    else:
        second_vs_first_ratio = 1.0

    preskill_skills = _collect_created_skills(preskill_results)
    postskill_skills = _collect_created_skills(postskill_results)

    return {
        "execution_only": {
            "mean_scores": {
                "baseline": baseline_score,
                "preskill": preskill_score,
                "postskill": postskill_score,
            },
            "ratios_vs_baseline": {
                "preskill": _ratio(preskill_score, baseline_score),
                "postskill": _ratio(postskill_score, baseline_score),
            },
            "usage": {
                "baseline": baseline_exec_usage,
                "preskill": preskill_exec_usage,
                "postskill": postskill_exec_usage,
            },
            "efficiency_vs_baseline": {
                "preskill": compute_efficiency_gain(baseline_exec_usage, preskill_exec_usage),
                "postskill": compute_efficiency_gain(baseline_exec_usage, postskill_exec_usage),
            },
        },
        "end_to_end": {
            "mean_scores": {
                "baseline": baseline_score,
                "preskill": preskill_score,
                "postskill": postskill_score,
            },
            "ratios_vs_baseline": {
                "preskill": _ratio(preskill_score, baseline_score),
                "postskill": _ratio(postskill_score, baseline_score),
            },
            "usage": {
                "baseline": baseline_e2e_usage,
                "preskill": preskill_e2e_usage,
                "postskill": postskill_e2e_usage,
            },
            "efficiency_vs_baseline": {
                "preskill": compute_efficiency_gain(baseline_e2e_usage, preskill_e2e_usage),
                "postskill": compute_efficiency_gain(baseline_e2e_usage, postskill_e2e_usage),
            },
        },
        "postskill": {
            "first_pass_mean": first_pass_mean,
            "second_pass_mean": second_pass_mean,
            "second_vs_first_delta": round(second_pass_mean - first_pass_mean, 4),
            "second_vs_first_ratio": second_vs_first_ratio,
        },
        "created_skills": {
            "preskill_count": len(preskill_skills),
            "postskill_count": len(postskill_skills),
            "preskill": preskill_skills,
            "postskill": postskill_skills,
        },
        "skill_quality": {
            "preskill_mean": _mean_skill_quality(preskill_results),
            "postskill_mean": _mean_skill_quality(postskill_results),
        },
        "skill_mutation_violations": {
            "preskill": sum(
                1
                for payload in preskill_results.values()
                if payload.get("skill_mutation_violation")
            ),
            "postskill": sum(
                1
                for payload in postskill_results.values()
                if payload.get("skill_mutation_violation")
            ),
        },
    }


def compute_evoscore(
    evolution_pass_rate: float,
    fail2pass_ratio: float,
    consistency_evolution: float,
    efficiency_gain: float,
    skill_quality: float,
) -> float:
    """Compute the composite EvoScore for leaderboard ranking.

    EvoScore = 0.4 * pass_rate + 0.2 * f2p_norm + 0.2 * consistency + 0.1 * eff + 0.1 * skill_q

    Args:
        evolution_pass_rate: Score in evolution mode [0, 1]
        fail2pass_ratio: fail2pass ratio (clamped to [0, 2] then normalized to [0, 1])
        consistency_evolution: Consistency score in evolution mode [0, 1]
        efficiency_gain: Token efficiency gain (clamped to [0, 2] then normalized to [0, 1])
        skill_quality: Skill quality score [0, 1]
    """
    f2p_norm = min(fail2pass_ratio, 2.0) / 2.0
    eff_norm = min(efficiency_gain, 2.0) / 2.0

    score = (
        0.4 * evolution_pass_rate
        + 0.2 * f2p_norm
        + 0.2 * consistency_evolution
        + 0.1 * eff_norm
        + 0.1 * skill_quality
    )
    return round(score, 4)


def scan_created_skills(
    workspace_path: str,
    *,
    exclude_names: Optional[FrozenSet[str]] = None,
) -> List[Dict[str, Any]]:
    """Scan workspace for skills created by the agent during evolution mode.

    exclude_names: Optional set of skill directory names to omit (e.g. bench seeded bundle).
    """
    skills = []
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"

    if not skills_dir.exists():
        return skills

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if exclude_names is not None and skill_dir.name in exclude_names:
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8")
        frontmatter = {}
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            try:
                frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError:
                pass

        scripts_dir = skill_dir / "scripts"
        refs_dir = skill_dir / "references"
        scripts_count = len(list(scripts_dir.glob("*"))) if scripts_dir.exists() else 0
        refs_count = len(list(refs_dir.glob("*"))) if refs_dir.exists() else 0

        skills.append(
            {
                "name": skill_dir.name,
                "path": str(skill_md),
                "content_length": len(content),
                "frontmatter": frontmatter,
                "has_scripts": scripts_count > 0,
                "scripts_count": scripts_count,
                "references_count": refs_count,
            }
        )

    return skills


def aggregate_metrics(task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate all EvoClawBench metrics from task results.

    Each task_result should contain:
        - task_id
        - baseline_grade (dict with "score" or "mean")
        - evolution_grade (dict with "score" or "mean")
        - baseline_usage (token usage dict)
        - evolution_usage (token usage dict)
        - sub_problem_scores_baseline (list of floats)
        - sub_problem_scores_evolution (list of floats)
        - created_skills (list from scan_created_skills)
        - skill_quality_score (float, from LLM judge)
    """
    baseline_scores = {}
    evolution_scores = {}
    consistency_baseline_list = []
    consistency_evolution_list = []
    total_baseline_usage: Dict[str, Any] = {
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "total_execution_time_seconds": 0.0,
    }
    total_evolution_usage: Dict[str, Any] = {
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "total_execution_time_seconds": 0.0,
    }
    skill_quality_scores = []
    all_created_skills = []

    for result in task_results:
        task_id = result["task_id"]

        b_grade = result.get("baseline_grade", {})
        e_grade = result.get("evolution_grade", {})
        baseline_scores[task_id] = float(b_grade.get("score", b_grade.get("mean", 0.0)))
        evolution_scores[task_id] = float(e_grade.get("score", e_grade.get("mean", 0.0)))

        b_sub = result.get("sub_problem_scores_baseline", [])
        e_sub = result.get("sub_problem_scores_evolution", [])
        if b_sub:
            consistency_baseline_list.append(compute_consistency(b_sub))
        if e_sub:
            consistency_evolution_list.append(compute_consistency(e_sub))

        b_usage = result.get("baseline_usage", {})
        e_usage = result.get("evolution_usage", {})
        for key in total_baseline_usage:
            total_baseline_usage[key] += b_usage.get(key, 0)
            total_evolution_usage[key] += e_usage.get(key, 0)

        sq = result.get("skill_quality_score")
        if sq is not None:
            skill_quality_scores.append(float(sq))

        all_created_skills.extend(result.get("created_skills", []))

    fail2pass = compute_fail2pass(baseline_scores, evolution_scores)
    efficiency = compute_efficiency_gain(total_baseline_usage, total_evolution_usage)

    consistency_baseline = (
        statistics.mean(consistency_baseline_list) if consistency_baseline_list else 0.0
    )
    consistency_evolution = (
        statistics.mean(consistency_evolution_list) if consistency_evolution_list else 0.0
    )
    skill_quality_mean = statistics.mean(skill_quality_scores) if skill_quality_scores else 0.0

    evolution_pass_rate = fail2pass["overall"]["evolution_mean"]
    f2p_ratio = fail2pass["overall"]["fail2pass"]
    if isinstance(f2p_ratio, str):
        f2p_ratio = 2.0
    eff_gain = efficiency.get("token_efficiency_gain", 1.0) or 1.0

    evoscore = compute_evoscore(
        evolution_pass_rate=evolution_pass_rate,
        fail2pass_ratio=f2p_ratio,
        consistency_evolution=consistency_evolution,
        efficiency_gain=eff_gain,
        skill_quality=skill_quality_mean,
    )

    return {
        "evoscore": evoscore,
        "fail2pass": fail2pass,
        "consistency": {
            "baseline": round(consistency_baseline, 4),
            "evolution": round(consistency_evolution, 4),
        },
        "efficiency": efficiency,
        "skill_quality": {
            "mean": round(skill_quality_mean, 4),
            "per_task": {r["task_id"]: r.get("skill_quality_score", 0.0) for r in task_results},
        },
        "created_skills": {
            "total_count": len(all_created_skills),
            "skills": all_created_skills,
        },
    }
