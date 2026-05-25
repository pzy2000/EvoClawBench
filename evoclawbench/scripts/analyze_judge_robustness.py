#!/usr/bin/env python3
"""Regrade hybrid-task outputs with an alternate judge and summarize agreement."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_grading import GradeResult, _grade_llm_judge, grade_task  # noqa: E402
from lib_tasks import Task, TaskLoader  # noqa: E402

DEFAULT_HYBRID_SUBSET = (
    "task_02_log_analysis",
    "task_06_code_review",
    "task_07_doc_extraction",
    "task_11_web_extraction",
    "task_13_data_pipeline",
    "task_14_email_processing",
    "task_15_shell_automation",
    "task_16_ci_pipeline",
    "task_17_invoice_processing",
    "task_18_dep_audit",
    "task_19_meeting_notes",
    "task_21_metrics_anomaly",
)


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return None
    return num / (den_x * den_y)


def summarize_agreement(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    original = [_safe_float(r.get("original_score")) for r in records]
    alternate = [_safe_float(r.get("alternate_score")) for r in records]
    deltas = [abs(a - b) for a, b in zip(original, alternate)]
    top = sorted(
        records, key=lambda r: abs(r["alternate_score"] - r["original_score"]), reverse=True
    )
    return {
        "pairs": len(records),
        "pearson_correlation": (
            None
            if _pearson(original, alternate) is None
            else round(float(_pearson(original, alternate)), 4)
        ),
        "mean_absolute_delta": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "within_0_05": sum(1 for d in deltas if d <= 0.05),
        "within_0_10": sum(1 for d in deltas if d <= 0.10),
        "top_disagreements": top[:5],
    }


def _load_tasks(tasks_dir: Path) -> Dict[str, Task]:
    loader = TaskLoader(tasks_dir)
    return {task.task_id: task for task in loader.load_all_tasks()}


def _last_grade(payload: Dict[str, Any]) -> Dict[str, Any]:
    grades = payload.get("grades") or []
    return grades[-1] if grades else {}


def _last_execution(payload: Dict[str, Any]) -> Dict[str, Any]:
    results = payload.get("results") or []
    return results[-1] if results else {}


def _mean_breakdown_score(breakdown: Dict[str, Any], prefix: str) -> Optional[float]:
    values = [_safe_float(value) for key, value in breakdown.items() if key.startswith(prefix)]
    if not values:
        return None
    return sum(values) / len(values)


def _combine_with_original_automated_score(
    *,
    task: Task,
    original_grade: Dict[str, Any],
    alternate_llm_grade: GradeResult,
) -> GradeResult:
    breakdown = original_grade.get("breakdown") or {}
    auto_score = _mean_breakdown_score(breakdown, "automated.")
    if auto_score is None:
        return alternate_llm_grade

    weights = task.grading_weights or {"automated": 0.5, "llm_judge": 0.5}
    auto_weight = float(weights.get("automated", 0.5))
    llm_weight = float(weights.get("llm_judge", 0.5))
    total_weight = auto_weight + llm_weight
    if total_weight <= 0:
        auto_weight = llm_weight = 0.5
        total_weight = 1.0

    score = (auto_score * auto_weight + alternate_llm_grade.score * llm_weight) / total_weight
    combined_breakdown = {
        **{key: value for key, value in breakdown.items() if key.startswith("automated.")},
        **{f"llm_judge.{key}": value for key, value in alternate_llm_grade.breakdown.items()},
    }
    return GradeResult(
        task_id=task.task_id,
        score=score,
        max_score=1.0,
        grading_type="hybrid",
        breakdown=combined_breakdown,
        notes=(
            f"Reused original automated score {auto_score:.4f}; "
            f"alternate judge notes: {alternate_llm_grade.notes}"
        ),
        sub_problem_scores=original_grade.get("sub_problem_scores") or [],
    )


def _grade_with_judge_model(
    *,
    task: Task,
    original_grade: Dict[str, Any],
    execution_result: Dict[str, Any],
    skill_dir: Path,
    judge_model: str,
    runtime: str,
    judge_timeout_seconds: float,
) -> GradeResult:
    if task.grading_type != "hybrid":
        return grade_task(
            task=task,
            execution_result=execution_result,
            skill_dir=skill_dir,
            judge_model=judge_model,
            judge_timeout_seconds=judge_timeout_seconds,
            runtime=runtime,
        )

    alternate_llm = _grade_llm_judge(
        task=task,
        execution_result=execution_result,
        skill_dir=skill_dir,
        judge_model=judge_model,
        judge_timeout_seconds=judge_timeout_seconds,
        runtime=runtime,
    )
    return _combine_with_original_automated_score(
        task=task,
        original_grade=original_grade,
        alternate_llm_grade=alternate_llm,
    )


def _grade_with_fallback(
    *,
    task: Task,
    original_grade: Dict[str, Any],
    execution_result: Dict[str, Any],
    skill_dir: Path,
    judge_model: str,
    fallback_judge_model: Optional[str],
    runtime: str,
    judge_timeout_seconds: float,
) -> tuple[GradeResult, str, bool]:
    grade = _grade_with_judge_model(
        task=task,
        original_grade=original_grade,
        execution_result=execution_result,
        skill_dir=skill_dir,
        judge_model=judge_model,
        judge_timeout_seconds=judge_timeout_seconds,
        runtime=runtime,
    )
    if fallback_judge_model and "LLM judge failed" in (grade.notes or ""):
        fallback = _grade_with_judge_model(
            task=task,
            original_grade=original_grade,
            execution_result=execution_result,
            skill_dir=skill_dir,
            judge_model=fallback_judge_model,
            judge_timeout_seconds=judge_timeout_seconds,
            runtime=runtime,
        )
        if "LLM judge failed" not in (fallback.notes or ""):
            return fallback, fallback_judge_model, True
    return grade, judge_model, False


def regrade_result(
    *,
    result_path: Path,
    tasks_dir: Path,
    skill_dir: Path,
    alternate_judge_model: str,
    fallback_judge_model: Optional[str],
    judge_timeout_seconds: float,
    task_ids: Iterable[str],
    modes: Iterable[str],
) -> Dict[str, Any]:
    data = json.loads(result_path.read_text(encoding="utf-8"))
    tasks = _load_tasks(tasks_dir)
    records: List[Dict[str, Any]] = []
    section_by_mode = {
        "baseline": "baseline_results",
        "preskill": "preskill_results",
        "postskill": "postskill_results",
    }
    primary_judge_unavailable = False

    for mode in modes:
        section = data.get(section_by_mode[mode]) or {}
        for task_id in task_ids:
            task = tasks.get(task_id)
            payload = section.get(task_id)
            if task is None or payload is None:
                continue
            original_grade = _last_grade(payload)
            execution_result = _last_execution(payload)
            judge_to_try = (
                fallback_judge_model
                if primary_judge_unavailable and fallback_judge_model
                else alternate_judge_model
            )
            fallback_for_record = (
                None if judge_to_try == fallback_judge_model else fallback_judge_model
            )
            print(f"Regrading {mode}/{task_id} with {judge_to_try}", flush=True)
            alternate_grade, judge_used, fell_back = _grade_with_fallback(
                task=task,
                original_grade=original_grade,
                execution_result=execution_result,
                skill_dir=skill_dir,
                judge_model=judge_to_try,
                fallback_judge_model=fallback_for_record,
                runtime=str(data.get("runtime") or ""),
                judge_timeout_seconds=judge_timeout_seconds,
            )
            primary_judge_unavailable = primary_judge_unavailable or fell_back
            if fell_back:
                print(f"Fallback judge selected for remaining records: {judge_used}", flush=True)
            records.append(
                {
                    "task_id": task_id,
                    "mode": mode,
                    "original_score": round(_safe_float(original_grade.get("score")), 4),
                    "alternate_score": round(alternate_grade.score, 4),
                    "delta": round(
                        alternate_grade.score - _safe_float(original_grade.get("score")), 4
                    ),
                    "original_notes": str(original_grade.get("notes") or "")[:500],
                    "alternate_notes": alternate_grade.notes[:500],
                    "alternate_judge_used": judge_used,
                }
            )

    return {
        "source_json": str(result_path),
        "runtime": data.get("runtime"),
        "model": data.get("model"),
        "original_judge_model": data.get("judge_model"),
        "requested_alternate_judge_model": alternate_judge_model,
        "fallback_judge_model": fallback_judge_model,
        "judge_models_used": sorted({record["alternate_judge_used"] for record in records}),
        "records": records,
        "summary": summarize_agreement(records),
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Judge Robustness Summary",
        "",
        f"- Source JSON: `{Path(payload['source_json']).name}`",
        f"- Original judge: `{payload.get('original_judge_model') or 'unserialized'}`",
        f"- Alternate judge requested: `{payload['requested_alternate_judge_model']}`",
        f"- Fallback judge: `{payload.get('fallback_judge_model') or 'none'}`",
        f"- Judge models used: `{', '.join(payload.get('judge_models_used') or [])}`",
        f"- Pairs: {summary['pairs']}",
        f"- Pearson correlation: {summary['pearson_correlation']}",
        f"- Mean absolute delta: {summary['mean_absolute_delta']}",
        f"- Within 0.05: {summary['within_0_05']}",
        f"- Within 0.10: {summary['within_0_10']}",
        "",
        "| Task | Mode | Original | Alternate | Delta | Judge used |",
        "|---|---|---:|---:|---:|---|",
    ]
    for record in summary["top_disagreements"]:
        lines.append(
            "| {task_id} | {mode} | {original_score:.4f} | {alternate_score:.4f} | "
            "{delta:.4f} | `{alternate_judge_used}` |".format(**record)
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_json", type=Path)
    parser.add_argument("--tasks-dir", type=Path, default=Path("tasks"))
    parser.add_argument("--skill-dir", type=Path, default=Path("."))
    parser.add_argument(
        "--alternate-judge",
        default="openrouter/anthropic/claude-opus-4.5",
        help="Alternate judge model for robustness regrading",
    )
    parser.add_argument(
        "--fallback-judge",
        default="openai/qwen3.6-plus",
        help="Fallback judge used if the alternate judge fails",
    )
    parser.add_argument("--tasks", default=",".join(DEFAULT_HYBRID_SUBSET))
    parser.add_argument("--modes", default="baseline,preskill,postskill")
    parser.add_argument("--judge-timeout-seconds", type=float, default=180.0)
    parser.add_argument("--output-prefix", default="judge_robustness_summary")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/paper_subset_experiments"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = regrade_result(
        result_path=args.result_json,
        tasks_dir=args.tasks_dir,
        skill_dir=args.skill_dir,
        alternate_judge_model=args.alternate_judge,
        fallback_judge_model=args.fallback_judge or None,
        judge_timeout_seconds=args.judge_timeout_seconds,
        task_ids=[item.strip() for item in args.tasks.split(",") if item.strip()],
        modes=[item.strip() for item in args.modes.split(",") if item.strip()],
    )
    json_path = args.output_dir / f"{args.output_prefix}.json"
    md_path = args.output_dir / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
