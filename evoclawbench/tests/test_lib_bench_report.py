"""Tests for bench mode report builder and renderers."""

from __future__ import annotations

from lib_bench_report import (
    build_bench_report,
    render_bench_report_html,
    render_bench_report_markdown,
)


def _minimal_aggregate() -> dict:
    return {
        "benchmark": "evoclawbench",
        "version": "0.1.0",
        "model": "test/model",
        "runtime": "openclaw",
        "mode": "bench",
        "run_id": "0001",
        "timestamp": 1_700_000_000.0,
        "runs_per_task": 1,
        "workers": 2,
        "environment": "local",
        "bench_results": {
            "task_a": {
                "task_id": "task_a",
                "grades": [
                    {
                        "task_id": "task_a",
                        "score": 0.5,
                        "max_score": 1.0,
                        "grading_type": "automated",
                        "breakdown": {"sub_1_x": 1.0},
                        "notes": "ok",
                        "sub_problem_scores": [0.5, 1.0],
                    }
                ],
                "results": [
                    {
                        "workspace": "/tmp/ws/task_a_bench",
                        "exit_code": 0,
                        "timed_out": False,
                        "status": "success",
                        "usage": {
                            "input_tokens": 100,
                            "output_tokens": 50,
                            "total_tokens": 150,
                            "cost_usd": 0.01,
                            "request_count": 2,
                        },
                    },
                    {
                        "workspace": "/tmp/ws/task_a_bench",
                        "exit_code": 0,
                        "timed_out": False,
                        "usage": {
                            "input_tokens": 200,
                            "output_tokens": 100,
                            "total_tokens": 300,
                            "cost_usd": 0.02,
                            "request_count": 1,
                        },
                    },
                ],
                "mean_score": 0.5,
                "std_score": 0.0,
                "created_skills": [
                    {"name": "skill-one", "path": "/tmp/ws/task_a_bench/skills/skill-one/SKILL.md"}
                ],
                "skill_quality_score": 0.42,
            },
            "task_b": {
                "task_id": "task_b",
                "grades": [
                    {
                        "task_id": "task_b",
                        "score": 0.0,
                        "max_score": 1.0,
                        "grading_type": "automated",
                        "breakdown": {},
                        "notes": "x < script alert",  # HTML-sensitive
                        "sub_problem_scores": [],
                    }
                ],
                "results": [
                    {
                        "workspace": "/tmp/ws/task_b",
                        "exit_code": 1,
                        "timed_out": True,
                        "status": "error",
                        "usage": {},
                    }
                ],
                "mean_score": 0.0,
                "std_score": 0.0,
                "created_skills": [],
                "skill_quality_score": 0.0,
            },
        },
    }


def test_build_bench_report_sums_and_ordering():
    agg = _minimal_aggregate()
    report = build_bench_report(
        agg,
        artifact_filenames={"results_json": "out.json", "trajectories_json": "tr.json"},
    )

    assert report["meta"]["run_id"] == "0001"
    assert report["meta"]["artifacts"]["results_json"] == "out.json"
    assert [t["task_id"] for t in report["tasks"]] == ["task_a", "task_b"]

    summ = report["summary"]
    assert summ["task_count"] == 2
    # Mean of score pcts: (0.5/1*100 + 0)/2 = 25
    assert abs(summ["mean_score_pct"] - 25.0) < 0.01
    assert summ["total_tokens"] == 450.0  # 150 + 300
    assert abs(summ["total_cost_usd"] - 0.03) < 1e-6
    assert summ["skills_total"] == 1

    row_a = report["tasks"][0]
    assert row_a["usage_total"]["input_tokens"] == 300.0
    assert row_a["sub_problem_scores"] == [0.5, 1.0]
    assert row_a["breakdown"] == {"sub_1_x": 1.0}

    row_b = report["tasks"][1]
    assert row_b["timed_out"] is True
    assert row_b["exit_code"] == 1


def test_markdown_contains_workspace_and_subscores():
    report = build_bench_report(_minimal_aggregate())
    md = render_bench_report_markdown(report)
    assert "task_a" in md
    assert "/tmp/ws/task_a_bench" in md
    assert "0.500, 1.000" in md or "1.000" in md
    assert "skill-one" in md


def test_html_escapes_notes():
    report = build_bench_report(_minimal_aggregate())
    html_out = render_bench_report_html(report)
    assert "task_b" in html_out
    assert "<script" not in html_out.lower()
    assert "x &lt; script alert" in html_out or "&lt;" in html_out
