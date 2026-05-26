"""
Human-readable reports for EvoClawBench --mode bench runs.

Builds a structured dict from aggregate JSON, then renders Markdown, HTML,
or a short terminal summary.
"""

from __future__ import annotations

import html
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _sum_usage_across_runs(results: List[Dict[str, Any]]) -> Dict[str, float]:
    totals = {
        "input_tokens": 0.0,
        "output_tokens": 0.0,
        "total_tokens": 0.0,
        "cost_usd": 0.0,
        "request_count": 0.0,
    }
    for r in results:
        u = r.get("usage") or {}
        totals["input_tokens"] += _safe_float(u.get("input_tokens"))
        totals["output_tokens"] += _safe_float(u.get("output_tokens"))
        totals["total_tokens"] += _safe_float(u.get("total_tokens"))
        totals["cost_usd"] += _safe_float(u.get("cost_usd"))
        totals["request_count"] += _safe_float(u.get("request_count"))
    return totals


def _task_row(task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    grades: List[Dict[str, Any]] = payload.get("grades") or []
    last_grade = grades[-1] if grades else {}
    results: List[Dict[str, Any]] = payload.get("results") or []
    last_result = results[-1] if results else {}

    max_score = _safe_float(last_grade.get("max_score"), 0.0)
    mean_score = _safe_float(payload.get("mean_score"), 0.0)
    score_pct = (mean_score / max_score * 100.0) if max_score > 0 else 0.0

    sub_scores = last_grade.get("sub_problem_scores") or []
    if not isinstance(sub_scores, list):
        sub_scores = []

    breakdown = last_grade.get("breakdown") or {}
    if not isinstance(breakdown, dict):
        breakdown = {}

    usage_total = _sum_usage_across_runs(results)

    created = payload.get("created_skills") or []
    if not isinstance(created, list):
        created = []

    return {
        "task_id": task_id,
        "mean_score": mean_score,
        "max_score": max_score,
        "score_pct": score_pct,
        "grading_type": str(last_grade.get("grading_type", "") or ""),
        "std_score": _safe_float(payload.get("std_score"), 0.0),
        "sub_problem_scores": [float(x) for x in sub_scores if isinstance(x, (int, float))],
        "breakdown": {
            str(k): float(v) for k, v in breakdown.items() if isinstance(v, (int, float))
        },
        "notes": str(last_grade.get("notes") or ""),
        "exit_code": last_result.get("exit_code", -1),
        "timed_out": bool(last_result.get("timed_out", False)),
        "status": str(last_result.get("status") or ""),
        "workspace": str(last_result.get("workspace") or payload.get("workspace") or ""),
        "usage_total": usage_total,
        "created_skills": created,
        "skill_quality_score": _safe_float(payload.get("skill_quality_score"), 0.0),
        "runs_count": len(results),
    }


def build_bench_report(
    aggregate: Dict[str, Any],
    *,
    artifact_filenames: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Build a report dict from a full benchmark aggregate (must include bench_results).

    artifact_filenames: optional dict with results_json and trajectories_json basename strings.
    """
    bench: Dict[str, Dict[str, Any]] = aggregate.get("bench_results") or {}
    rows = [_task_row(tid, payload) for tid, payload in sorted(bench.items())]

    score_pcts = [r["score_pct"] for r in rows]
    mean_pass_pct = statistics.mean(score_pcts) if score_pcts else 0.0

    tot_tokens = sum(r["usage_total"]["total_tokens"] for r in rows)
    tot_cost = sum(r["usage_total"]["cost_usd"] for r in rows)
    skill_entries = sum(len(r["created_skills"]) for r in rows)

    ts = aggregate.get("timestamp")
    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        ts_iso = dt.isoformat()
    else:
        ts_iso = ""

    meta = {
        "benchmark": aggregate.get("benchmark", "evoclawbench"),
        "version": aggregate.get("version", ""),
        "model": aggregate.get("model", ""),
        "runtime": aggregate.get("runtime", ""),
        "mode": aggregate.get("mode", "bench"),
        "run_id": aggregate.get("run_id", ""),
        "timestamp": ts_iso,
        "runs_per_task": aggregate.get("runs_per_task", 1),
        "workers": aggregate.get("workers", 1),
        "environment": aggregate.get("environment", ""),
    }
    if artifact_filenames:
        meta["artifacts"] = dict(artifact_filenames)

    return {
        "meta": meta,
        "summary": {
            "task_count": len(rows),
            "mean_score_pct": mean_pass_pct,
            "total_tokens": tot_tokens,
            "total_cost_usd": tot_cost,
            "skills_total": skill_entries,
        },
        "tasks": rows,
    }


def print_bench_report_summary(report: Dict[str, Any]) -> None:
    """Short terminal summary (no full breakdown tables)."""
    meta = report.get("meta") or {}
    summ = report.get("summary") or {}
    tasks: List[Dict[str, Any]] = report.get("tasks") or []

    print("\n" + "=" * 70)
    print("  EVOCLAWBENCH BENCH REPORT")
    print("=" * 70)
    print(f"\n  Run ID:      {meta.get('run_id', '')}")
    print(f"  Model:       {meta.get('model', '')}")
    print(f"  Runtime:     {meta.get('runtime', '')}")
    if meta.get("timestamp"):
        print(f"  Finished:    {meta.get('timestamp')}")
    print(f"\n  Tasks:       {summ.get('task_count', 0)}")
    msp_short = float(summ.get("mean_score_pct", 0.0))
    print(f"  Mean score:  {msp_short:.1f}% (mean of task score / max)")
    print(f"  Total tokens: {int(summ.get('total_tokens', 0))}")
    print(f"  Total cost:   ${float(summ.get('total_cost_usd', 0.0)):.4f}")
    print(f"  Skills found: {summ.get('skills_total', 0)}")

    arts = meta.get("artifacts") or {}
    if arts.get("results_json"):
        print(f"\n  Results JSON:     {arts['results_json']}")
    if arts.get("trajectories_json"):
        print(f"  Trajectories JSON: {arts['trajectories_json']}")

    if tasks:
        print(f"\n  {'TASK':<38} {'SCORE':>12} {'SUBS':>6}")
        print("  " + "-" * 58)
    for r in tasks:
        tid = str(r.get("task_id", ""))
        ms = float(r.get("mean_score", 0.0))
        mx = float(r.get("max_score", 0.0))
        subs = r.get("sub_problem_scores") or []
        sub_s = f"{len(subs)}" if subs else "-"
        print(f"  {tid:<38} {ms:>5.2f}/{mx:<4.1f}   {sub_s:>6}")

    print("\n" + "=" * 70)


def render_bench_report_markdown(report: Dict[str, Any]) -> str:
    meta = report.get("meta") or {}
    summ = report.get("summary") or {}
    tasks: List[Dict[str, Any]] = report.get("tasks") or []

    lines: List[str] = [
        "# EvoClawBench — bench mode report",
        "",
        "## Run",
        "",
        f"- **Run ID**: `{meta.get('run_id', '')}`",
        f"- **Model**: `{meta.get('model', '')}`",
        f"- **Runtime**: `{meta.get('runtime', '')}`",
        f"- **Environment**: `{meta.get('environment', '')}`",
        f"- **Workers**: {meta.get('workers', '')}",
        f"- **Runs per task**: {meta.get('runs_per_task', '')}",
    ]
    if meta.get("timestamp"):
        lines.append(f"- **UTC time**: `{meta.get('timestamp')}`")
    lines.extend(["", "## Summary", ""])
    lines.append(f"- Tasks: **{summ.get('task_count', 0)}**")
    lines.append(
        f"- Mean score (avg of task mean/max): **{float(summ.get('mean_score_pct', 0.0)):.2f}%**"
    )
    lines.append(f"- Total tokens: **{int(summ.get('total_tokens', 0))}**")
    lines.append(f"- Total cost (USD): **{float(summ.get('total_cost_usd', 0.0)):.4f}**")
    lines.append(f"- Skills detected (non-seeded): **{summ.get('skills_total', 0)}**")

    arts = meta.get("artifacts") or {}
    if arts:
        lines.extend(["", "## Artifacts", ""])
        if arts.get("results_json"):
            lines.append(f"- Results: `{arts['results_json']}`")
        if arts.get("trajectories_json"):
            lines.append(f"- Trajectories: `{arts['trajectories_json']}`")

    hdr = "| Task | Mean / Max | % | Grading | Exit | Workspace |"
    sep = "| --- | --- | --- | --- | --- | --- |"
    lines.extend(["", "## Tasks", "", hdr, sep])
    for r in tasks:
        tid = str(r.get("task_id", ""))
        ms = float(r.get("mean_score", 0.0))
        mx = float(r.get("max_score", 0.0))
        pct = float(r.get("score_pct", 0.0))
        gt = str(r.get("grading_type", ""))
        ex = r.get("exit_code", "")
        ws = str(r.get("workspace", "")).replace("|", "\\|")
        lines.append(f"| `{tid}` | {ms:.3f} / {mx:.3f} | {pct:.1f}% | {gt} | {ex} | `{ws}` |")

    for r in tasks:
        tid = str(r.get("task_id", ""))
        lines.extend(["", f"### `{tid}`", ""])
        lines.append(f"- **Runs**: {r.get('runs_count', 0)}")
        lines.append(f"- **Timed out**: {r.get('timed_out', False)}")
        if r.get("status"):
            lines.append(f"- **Status**: `{r.get('status')}`")
        ut = r.get("usage_total") or {}
        lines.append(
            f"- **Usage (sum over runs)**: in={int(ut.get('input_tokens', 0))}, "
            f"out={int(ut.get('output_tokens', 0))}, total={int(ut.get('total_tokens', 0))}, "
            f"cost_usd={float(ut.get('cost_usd', 0.0)):.4f}"
        )
        subs = r.get("sub_problem_scores") or []
        if subs:
            pretty = ", ".join(f"{float(x):.3f}" for x in subs)
            lines.append(f"- **Sub-problem scores** ({len(subs)}): {pretty}")
        bd = r.get("breakdown") or {}
        if bd:
            lines.append("- **Breakdown**:")
            for k in sorted(bd.keys()):
                lines.append(f"  - `{k}`: {float(bd[k]):.4f}")
        notes = str(r.get("notes") or "")
        if notes:
            lines.append(f"- **Notes**: {notes}")
        skills = r.get("created_skills") or []
        sq = float(r.get("skill_quality_score", 0.0))
        lines.append(f"- **Skill quality (heuristic)**: {sq:.4f}")
        if skills:
            lines.append("- **Created skills**:")
            for s in skills:
                if not isinstance(s, dict):
                    continue
                name = str(s.get("name", ""))
                path = str(s.get("path", ""))
                lines.append(f"  - `{name}` — `{path}`")
        else:
            lines.append("- **Created skills**: (none)")

    lines.append("")
    return "\n".join(lines)


def render_bench_report_html(report: Dict[str, Any]) -> str:
    meta = report.get("meta") or {}
    summ = report.get("summary") or {}
    tasks: List[Dict[str, Any]] = report.get("tasks") or []

    def esc(s: Any) -> str:
        return html.escape(str(s), quote=True)

    parts: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8"/>',
        "<title>EvoClawBench bench report</title>",
        "<style>",
        "body{font-family:system-ui,sans-serif;margin:1.5rem;line-height:1.45;color:#1a1a1a;}",
        "h1,h2{border-bottom:1px solid #ccc;padding-bottom:.2rem;}",
        "table{border-collapse:collapse;width:100%;margin:1rem 0;}",
        "th,td{border:1px solid #ddd;padding:.4rem .55rem;text-align:left;}",
        "th{background:#f4f4f4;}",
        "tbody tr:nth-child(even){background:#fafafa;}",
        ".mono{font-family:ui-monospace,SFMono-Regular,monospace;font-size:.88em;}",
        ".task{margin-top:2rem;padding-top:1rem;border-top:1px solid #eee;}",
        "ul.breakdown{margin:.3rem 0;columns:2;}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>EvoClawBench — bench mode</h1>",
        "<h2>Run</h2>",
        '<table class="mono">',
        f"<tr><th>Run ID</th><td>{esc(meta.get('run_id', ''))}</td></tr>",
        f"<tr><th>Model</th><td>{esc(meta.get('model', ''))}</td></tr>",
        f"<tr><th>Runtime</th><td>{esc(meta.get('runtime', ''))}</td></tr>",
        f"<tr><th>Environment</th><td>{esc(meta.get('environment', ''))}</td></tr>",
        f"<tr><th>Workers</th><td>{esc(meta.get('workers', ''))}</td></tr>",
        f"<tr><th>Runs / task</th><td>{esc(meta.get('runs_per_task', ''))}</td></tr>",
    ]
    if meta.get("timestamp"):
        parts.append(f"<tr><th>UTC</th><td>{esc(meta.get('timestamp'))}</td></tr>")
    parts.append("</table>")

    parts.append("<h2>Summary</h2><ul>")
    parts.append(f"<li>Tasks: <strong>{esc(summ.get('task_count', 0))}</strong></li>")
    msp = float(summ.get("mean_score_pct", 0.0))
    parts.append(f"<li>Mean score %: <strong>{esc(f'{msp:.2f}')}</strong></li>")
    parts.append(f"<li>Total tokens: <strong>{esc(int(summ.get('total_tokens', 0)))}</strong></li>")
    tc = float(summ.get("total_cost_usd", 0.0))
    parts.append(f"<li>Total cost USD: <strong>{esc(f'{tc:.4f}')}</strong></li>")
    parts.append(f"<li>Skills: <strong>{esc(summ.get('skills_total', 0))}</strong></li>")
    parts.append("</ul>")

    arts = meta.get("artifacts") or {}
    if arts:
        parts.append('<h2>Artifacts</h2><ul class="mono">')
        if arts.get("results_json"):
            parts.append(f"<li>Results: {esc(arts['results_json'])}</li>")
        if arts.get("trajectories_json"):
            parts.append(f"<li>Trajectories: {esc(arts['trajectories_json'])}</li>")
        parts.append("</ul>")

    parts.append("<h2>Tasks</h2>")
    parts.append("<table>")
    parts.append(
        "<thead><tr><th>Task</th><th>Mean / Max</th><th>%</th><th>Grading</th>"
        "<th>Exit</th><th>Workspace</th></tr></thead><tbody>"
    )
    for r in tasks:
        tid = esc(r.get("task_id", ""))
        ms = float(r.get("mean_score", 0.0))
        mx = float(r.get("max_score", 0.0))
        pct = float(r.get("score_pct", 0.0))
        parts.append(
            "<tr>"
            f'<td class="mono">{tid}</td>'
            f"<td>{esc( f'{ms:.3f} / {mx:.3f}')}</td>"
            f"<td>{esc(f'{pct:.1f}')}</td>"
            f"<td>{esc(r.get('grading_type', ''))}</td>"
            f"<td>{esc(r.get('exit_code', ''))}</td>"
            f"<td class=\"mono\">{esc(r.get('workspace', ''))}</td>"
            "</tr>"
        )
    parts.append("</tbody></table>")

    for r in tasks:
        tid = esc(r.get("task_id", ""))
        parts.append(f'<section class="task"><h3 class="mono">{tid}</h3>')
        parts.append("<ul>")
        parts.append(f"<li>Runs: {esc(r.get('runs_count', 0))}</li>")
        parts.append(f"<li>Timed out: {esc(r.get('timed_out', False))}</li>")
        if r.get("status"):
            parts.append(f"<li>Status: {esc(r.get('status'))}</li>")
        ut = r.get("usage_total") or {}
        cost_u = float(ut.get("cost_usd", 0.0))
        inn = esc(int(ut.get("input_tokens", 0)))
        outt = esc(int(ut.get("output_tokens", 0)))
        tot = esc(int(ut.get("total_tokens", 0)))
        parts.append(
            "<li>Usage (sum): "
            f"in={inn}, out={outt}, "
            f"total={tot}, "
            f"cost_usd={esc(f'{cost_u:.4f}')}"
            "</li>"
        )
        subs = r.get("sub_problem_scores") or []
        if subs:
            pretty = esc(", ".join(f"{float(x):.3f}" for x in subs))
            parts.append(f"<li>Sub-problem scores ({esc(len(subs))}): {pretty}</li>")
        bd = r.get("breakdown") or {}
        if bd:
            parts.append('<li>Breakdown:<ul class="breakdown">')
            for k in sorted(bd.keys()):
                parts.append(
                    f"<li><span class=\"mono\">{esc(k)}</span>: {esc(f'{float(bd[k]):.4f}')}</li>"
                )
            parts.append("</ul></li>")
        notes = str(r.get("notes") or "")
        if notes:
            parts.append(f"<li>Notes: {esc(notes)}</li>")
        skq = float(r.get("skill_quality_score", 0.0))
        parts.append(f"<li>Skill quality: {esc(f'{skq:.4f}')}</li>")
        skills = r.get("created_skills") or []
        if skills:
            parts.append("<li>Created skills:<ul>")
            for s in skills:
                if isinstance(s, dict):
                    parts.append(
                        '<li><span class="mono">'
                        f"{esc(s.get('name', ''))}</span> — "
                        f"<span class=\"mono\">{esc(s.get('path', ''))}</span></li>"
                    )
            parts.append("</ul></li>")
        else:
            parts.append("<li>Created skills: (none)</li>")
        parts.append("</ul></section>")

    parts.append("</body></html>")
    return "\n".join(parts)
