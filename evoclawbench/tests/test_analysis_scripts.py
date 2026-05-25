"""Tests for paper subset analysis helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze_cost_and_amortization import summarize_result  # noqa: E402
from analyze_judge_robustness import (  # noqa: E402
    _combine_with_original_automated_score,
    summarize_agreement,
)
from lib_grading import GradeResult  # noqa: E402
from lib_tasks import Task  # noqa: E402
from run_ablation_subset import DEFAULT_SKILL_DIR, summarize_ablation  # noqa: E402


def _usage(tokens: int, cost: float, seconds: float, requests: int = 1) -> dict:
    return {
        "total_tokens": tokens,
        "total_cost_usd": cost,
        "total_execution_time_seconds": seconds,
        "request_count": requests,
    }


def test_cost_summary_computes_break_even(tmp_path):
    result_path = tmp_path / "subset.json"
    result_path.write_text(
        json.dumps(
            {
                "model": "openai/gpt-5.4-mini",
                "runtime": "openclaw",
                "mode": "all",
                "judge_model": "judge/model",
                "baseline_results": {"task_a": {}},
                "preskill_results": {
                    "task_a": {
                        "phase_usage": {
                            "skill_generation": _usage(40, 0.04, 10),
                            "execution": _usage(60, 0.06, 20),
                        }
                    }
                },
                "postskill_results": {
                    "task_a": {
                        "phase_usage": {
                            "first_execution": _usage(100, 0.10, 30),
                            "skill_summary": _usage(20, 0.02, 5),
                            "second_execution": _usage(50, 0.05, 15),
                        }
                    }
                },
                "metrics": {
                    "execution_only": {
                        "usage": {
                            "baseline": _usage(100, 0.10, 30),
                            "preskill": _usage(60, 0.06, 20),
                            "postskill": _usage(50, 0.05, 15),
                        }
                    },
                    "end_to_end": {
                        "mean_scores": {
                            "baseline": 0.5,
                            "preskill": 0.6,
                            "postskill": 0.7,
                        },
                        "usage": {
                            "baseline": _usage(100, 0.10, 30),
                            "preskill": _usage(100, 0.10, 30),
                            "postskill": _usage(170, 0.17, 50),
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_result(result_path)

    assert summary["tasks"] == 1
    assert summary["cost_rows"][1]["mode"] == "preskill"
    assert summary["break_even_reuse_count"]["preskill"]["total_tokens"] == 1
    assert summary["break_even_reuse_count"]["postskill"]["total_tokens"] == 1


def test_judge_robustness_agreement_summary():
    summary = summarize_agreement(
        [
            {"task_id": "a", "mode": "baseline", "original_score": 0.5, "alternate_score": 0.6},
            {"task_id": "b", "mode": "baseline", "original_score": 0.7, "alternate_score": 0.65},
        ]
    )

    assert summary["pairs"] == 2
    assert summary["mean_absolute_delta"] == 0.075
    assert summary["within_0_10"] == 2


def test_judge_robustness_reuses_original_automated_score():
    task = Task(
        task_id="task_h",
        name="Hybrid",
        category="test",
        grading_type="hybrid",
        timeout_seconds=10,
        workspace_files=[],
        prompt="prompt",
        expected_behavior="expected",
        grading_criteria=[],
        grading_weights={"automated": 0.9, "llm_judge": 0.1},
    )
    original_grade = {
        "breakdown": {
            "automated.exists": 1.0,
            "automated.valid": 1.0,
            "llm_judge.quality": 1.0,
        },
        "sub_problem_scores": [1.0],
    }
    alternate_llm = GradeResult(
        task_id="task_h",
        score=0.5,
        max_score=1.0,
        grading_type="llm_judge",
        breakdown={"quality": 0.5},
        notes="partial",
    )

    combined = _combine_with_original_automated_score(
        task=task,
        original_grade=original_grade,
        alternate_llm_grade=alternate_llm,
    )

    assert combined.score == pytest.approx(0.95)
    assert combined.breakdown["automated.exists"] == 1.0
    assert combined.breakdown["llm_judge.quality"] == 0.5


def test_ablation_summary_groups_variants():
    summary = summarize_ablation(
        [
            {
                "task_id": "task_a",
                "variant": "baseline",
                "score": 0.5,
                "usage": _usage(100, 0.1, 10),
            },
            {
                "task_id": "task_a",
                "variant": "empty_skill_reuse",
                "score": 0.4,
                "usage": _usage(120, 0.12, 12),
                "created_skill_count": 1,
            },
        ]
    )

    assert summary["variants"]["baseline"]["mean_score_pct"] == 50.0
    assert summary["variants"]["empty_skill_reuse"]["mean_delta_vs_baseline_pct"] == -10.0
    assert summary["variants"]["empty_skill_reuse"]["created_skill_count"] == 1


def test_ablation_default_skill_dir_points_to_benchmark_root():
    assert DEFAULT_SKILL_DIR.name == "evoclawbench"
    assert (DEFAULT_SKILL_DIR.parent / "skills" / "skill-creator" / "SKILL.md").is_file()
