#!/usr/bin/env python3
"""Summarize subset cost, token, time, and amortization tradeoffs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

USAGE_METRICS = ("total_tokens", "total_cost_usd", "total_execution_time_seconds")
REUSE_COUNTS = (1, 2, 5, 10)


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _empty_usage() -> Dict[str, float]:
    return {
        "total_tokens": 0.0,
        "total_cost_usd": 0.0,
        "total_execution_time_seconds": 0.0,
        "request_count": 0.0,
    }


def _add_usage(items: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    total = _empty_usage()
    for item in items:
        for key in total:
            total[key] += _safe_float(item.get(key))
    return total


def _phase_usage(results: Dict[str, Any], phase: str) -> Dict[str, float]:
    return _add_usage(
        (payload.get("phase_usage") or {}).get(phase) or {}
        for payload in results.values()
        if isinstance(payload, dict)
    )


def _metric_available(metric: str, baseline: Dict[str, Any], candidate: Dict[str, Any]) -> bool:
    if metric == "total_cost_usd":
        return _safe_float(baseline.get(metric)) > 0.0 or _safe_float(candidate.get(metric)) > 0.0
    return _safe_float(baseline.get(metric)) > 0.0 and _safe_float(candidate.get(metric)) > 0.0


def _break_even_reuse_count(
    *,
    setup_usage: Dict[str, Any],
    candidate_reuse_usage: Dict[str, Any],
    baseline_usage: Dict[str, Any],
    metric: str,
    baseline_credit: float = 0.0,
) -> Optional[int]:
    if not _metric_available(metric, baseline_usage, candidate_reuse_usage):
        return None

    setup = _safe_float(setup_usage.get(metric))
    candidate = _safe_float(candidate_reuse_usage.get(metric))
    baseline = _safe_float(baseline_usage.get(metric))
    overhead = max(0.0, setup - baseline_credit)
    per_reuse_savings = baseline - candidate

    if overhead <= 0.0:
        return 1
    if per_reuse_savings <= 0.0:
        return None
    return max(1, math.ceil(overhead / per_reuse_savings))


def _score_delta_per_million_tokens(
    baseline_score: float,
    candidate_score: float,
    baseline_usage: Dict[str, Any],
    candidate_usage: Dict[str, Any],
) -> Optional[float]:
    extra_tokens = _safe_float(candidate_usage.get("total_tokens")) - _safe_float(
        baseline_usage.get("total_tokens")
    )
    if extra_tokens <= 0:
        return None
    return round(((candidate_score - baseline_score) * 100.0) / (extra_tokens / 1_000_000), 4)


def _format_break_even(value: Optional[int]) -> str:
    return "unavailable/never" if value is None else str(value)


def summarize_result(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics = data.get("metrics") or {}
    end_to_end = metrics.get("end_to_end") or {}
    execution = metrics.get("execution_only") or {}
    scores = end_to_end.get("mean_scores") or {}
    e2e_usage = end_to_end.get("usage") or {}
    exec_usage = execution.get("usage") or {}

    baseline_score = _safe_float(scores.get("baseline"))
    baseline_e2e = e2e_usage.get("baseline") or {}
    baseline_exec = exec_usage.get("baseline") or baseline_e2e

    preskill_setup = _phase_usage(data.get("preskill_results") or {}, "skill_generation")
    preskill_exec = exec_usage.get("preskill") or _phase_usage(
        data.get("preskill_results") or {}, "execution"
    )
    postskill_first = _phase_usage(data.get("postskill_results") or {}, "first_execution")
    postskill_summary = _phase_usage(data.get("postskill_results") or {}, "skill_summary")
    postskill_setup = _add_usage([postskill_first, postskill_summary])
    postskill_exec = exec_usage.get("postskill") or _phase_usage(
        data.get("postskill_results") or {}, "second_execution"
    )

    rows: List[Dict[str, Any]] = []
    break_even: Dict[str, Dict[str, Optional[int]]] = {}
    simulations: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {}

    for mode in ("baseline", "preskill", "postskill"):
        usage = e2e_usage.get(mode) or {}
        score = _safe_float(scores.get(mode))
        rows.append(
            {
                "mode": mode,
                "score_pct": round(score * 100.0, 2),
                "delta_score_pct": round((score - baseline_score) * 100.0, 2),
                "total_tokens": int(_safe_float(usage.get("total_tokens"))),
                "total_cost_usd": round(_safe_float(usage.get("total_cost_usd")), 6),
                "total_time_hours": round(
                    _safe_float(usage.get("total_execution_time_seconds")) / 3600.0, 3
                ),
                "request_count": int(_safe_float(usage.get("request_count"))),
                "delta_score_per_1m_extra_tokens": (
                    _score_delta_per_million_tokens(baseline_score, score, baseline_e2e, usage)
                    if mode != "baseline"
                    else None
                ),
            }
        )

    for mode, setup, reuse, credit_source in (
        ("preskill", preskill_setup, preskill_exec, None),
        ("postskill", postskill_setup, postskill_exec, baseline_exec),
    ):
        baseline_credit_by_metric = credit_source or {}
        break_even[mode] = {
            metric: _break_even_reuse_count(
                setup_usage=setup,
                candidate_reuse_usage=reuse,
                baseline_usage=baseline_exec,
                metric=metric,
                baseline_credit=_safe_float(baseline_credit_by_metric.get(metric)),
            )
            for metric in USAGE_METRICS
        }
        simulations[mode] = {}
        for count in REUSE_COUNTS:
            simulations[mode][str(count)] = {}
            for metric in USAGE_METRICS:
                if not _metric_available(metric, baseline_exec, reuse):
                    simulations[mode][str(count)][metric] = None
                    continue
                direct_runs = count + (1 if mode == "postskill" else 0)
                candidate_total = _safe_float(setup.get(metric)) + count * _safe_float(
                    reuse.get(metric)
                )
                baseline_total = direct_runs * _safe_float(baseline_exec.get(metric))
                simulations[mode][str(count)][metric] = round(candidate_total / baseline_total, 4)

    return {
        "source_json": str(path),
        "model": data.get("model"),
        "runtime": data.get("runtime"),
        "judge_model": data.get("judge_model"),
        "mode": data.get("mode"),
        "tasks": len(data.get("baseline_results") or {}),
        "cost_rows": rows,
        "break_even_reuse_count": break_even,
        "amortized_ratio_vs_direct": simulations,
        "notes": [
            "Postskill amortization gives one baseline-credit for the first execution phase.",
            "Cost break-even is unavailable when source usage has zero or unknown USD cost.",
        ],
    }


def render_markdown(summaries: List[Dict[str, Any]]) -> str:
    lines = ["# Cost and Amortization Summary", ""]
    for summary in summaries:
        lines.extend(
            [
                f"## {summary['runtime']} / {summary['model']}",
                "",
                f"- Source JSON: `{Path(summary['source_json']).name}`",
                f"- Judge model: `{summary.get('judge_model') or 'unserialized'}`",
                f"- Tasks: {summary['tasks']}",
                "",
                "| Mode | Score | Delta | Tokens | Cost USD | Time h | Requests | "
                "Delta / 1M extra tokens |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summary["cost_rows"]:
            delta_per = row["delta_score_per_1m_extra_tokens"]
            lines.append(
                "| {mode} | {score_pct:.2f} | {delta_score_pct:.2f} | {total_tokens} | "
                "{total_cost_usd:.6f} | {total_time_hours:.3f} | "
                "{request_count} | {delta} |".format(
                    **row,
                    delta="" if delta_per is None else f"{delta_per:.4f}",
                )
            )
        lines.extend(
            [
                "",
                "| Mode | Token break-even | Cost break-even | Time break-even |",
                "|---|---:|---:|---:|",
            ]
        )
        for mode, values in summary["break_even_reuse_count"].items():
            lines.append(
                "| {mode} | {tokens} | {cost} | {time} |".format(
                    mode=mode,
                    tokens=_format_break_even(values["total_tokens"]),
                    cost=_format_break_even(values["total_cost_usd"]),
                    time=_format_break_even(values["total_execution_time_seconds"]),
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", type=Path, help="Benchmark result JSON files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/paper_subset_experiments"),
        help="Directory for cost_amortization_summary.{json,md}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = [summarize_result(path) for path in args.results]
    payload = {"summaries": summaries}
    json_path = args.output_dir / "cost_amortization_summary.json"
    md_path = args.output_dir / "cost_amortization_summary.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summaries), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
