"""Tests for lib_metrics.py"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_metrics import (
    aggregate_metrics,
    aggregate_three_mode_metrics,
    compute_consistency,
    compute_efficiency_gain,
    compute_evoscore,
    compute_fail2pass,
    scan_created_skills,
)

# ---------------------------------------------------------------------------
# compute_fail2pass
# ---------------------------------------------------------------------------


class TestComputeFail2Pass:
    def test_basic_improvement(self):
        result = compute_fail2pass(
            baseline_scores={"t1": 0.5, "t2": 0.6},
            evolution_scores={"t1": 0.8, "t2": 0.9},
        )
        assert result["overall"]["fail2pass"] > 1.0
        assert result["overall"]["baseline_mean"] == pytest.approx(0.55, abs=0.01)
        assert result["overall"]["evolution_mean"] == pytest.approx(0.85, abs=0.01)

    def test_no_change(self):
        result = compute_fail2pass(
            baseline_scores={"t1": 0.7},
            evolution_scores={"t1": 0.7},
        )
        assert result["overall"]["fail2pass"] == pytest.approx(1.0)

    def test_baseline_zero(self):
        result = compute_fail2pass(
            baseline_scores={"t1": 0.0},
            evolution_scores={"t1": 0.5},
        )
        assert result["per_task"]["t1"]["fail2pass"] == "inf"

    def test_both_zero(self):
        result = compute_fail2pass(
            baseline_scores={"t1": 0.0},
            evolution_scores={"t1": 0.0},
        )
        assert result["per_task"]["t1"]["fail2pass"] == 1.0

    def test_empty_scores(self):
        result = compute_fail2pass({}, {})
        assert result["overall"]["baseline_mean"] == 0.0
        assert result["overall"]["evolution_mean"] == 0.0
        assert result["overall"]["fail2pass"] == 1.0

    def test_per_task_structure(self):
        result = compute_fail2pass(
            baseline_scores={"t1": 0.4, "t2": 0.6},
            evolution_scores={"t1": 0.8, "t2": 0.6},
        )
        assert "t1" in result["per_task"]
        assert "t2" in result["per_task"]
        assert result["per_task"]["t1"]["fail2pass"] == pytest.approx(2.0)
        assert result["per_task"]["t2"]["fail2pass"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# compute_consistency
# ---------------------------------------------------------------------------


class TestComputeConsistency:
    def test_perfect_consistency(self):
        assert compute_consistency([0.8, 0.8, 0.8, 0.8]) == 1.0

    def test_single_score(self):
        assert compute_consistency([0.5]) == 1.0

    def test_empty(self):
        assert compute_consistency([]) == 1.0

    def test_all_zeros(self):
        assert compute_consistency([0.0, 0.0, 0.0]) == 0.0

    def test_high_variance(self):
        score = compute_consistency([0.0, 1.0, 0.0, 1.0])
        assert score < 0.5

    def test_low_variance(self):
        score = compute_consistency([0.8, 0.85, 0.82, 0.78])
        assert score > 0.9

    def test_bounded_zero_to_one(self):
        score = compute_consistency([0.01, 10.0])  # extreme variance
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# compute_efficiency_gain
# ---------------------------------------------------------------------------


class TestComputeEfficiencyGain:
    def test_basic_gain(self):
        result = compute_efficiency_gain(
            baseline_usage={
                "total_tokens": 10000,
                "total_cost_usd": 1.0,
                "total_execution_time_seconds": 100,
            },
            evolution_usage={
                "total_tokens": 5000,
                "total_cost_usd": 0.5,
                "total_execution_time_seconds": 50,
            },
        )
        assert result["token_efficiency_gain"] == pytest.approx(2.0)
        assert result["cost_efficiency_gain"] == pytest.approx(2.0)
        assert result["time_efficiency_gain"] == pytest.approx(2.0)

    def test_zero_evolution(self):
        result = compute_efficiency_gain(
            baseline_usage={
                "total_tokens": 1000,
                "total_cost_usd": 1.0,
                "total_execution_time_seconds": 10,
            },
            evolution_usage={
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "total_execution_time_seconds": 0,
            },
        )
        assert result["token_efficiency_gain"] is None
        assert result["cost_efficiency_gain"] is None
        assert result["time_efficiency_gain"] is None

    def test_empty_usage(self):
        result = compute_efficiency_gain({}, {})
        assert result["token_efficiency_gain"] is None


# ---------------------------------------------------------------------------
# compute_evoscore
# ---------------------------------------------------------------------------


class TestComputeEvoScore:
    def test_perfect_scores(self):
        score = compute_evoscore(
            evolution_pass_rate=1.0,
            fail2pass_ratio=2.0,
            consistency_evolution=1.0,
            efficiency_gain=2.0,
            skill_quality=1.0,
        )
        # 0.4*1 + 0.2*1 + 0.2*1 + 0.1*1 + 0.1*1 = 1.0
        assert score == pytest.approx(1.0)

    def test_zero_scores(self):
        score = compute_evoscore(0.0, 0.0, 0.0, 0.0, 0.0)
        assert score == pytest.approx(0.0)

    def test_clamping(self):
        # fail2pass > 2.0 should be clamped
        score1 = compute_evoscore(0.5, 5.0, 0.5, 5.0, 0.5)
        score2 = compute_evoscore(0.5, 2.0, 0.5, 2.0, 0.5)
        assert score1 == score2

    def test_bounded(self):
        score = compute_evoscore(0.7, 1.3, 0.8, 1.1, 0.6)
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# scan_created_skills
# ---------------------------------------------------------------------------


class TestScanCreatedSkills:
    def test_empty_workspace(self, tmp_path):
        skills = scan_created_skills(str(tmp_path))
        assert skills == []

    def test_no_skills_dir(self, tmp_path):
        skills = scan_created_skills(str(tmp_path / "nonexistent"))
        assert skills == []

    def test_finds_skills(self, tmp_path):
        skills_dir = tmp_path / "skills" / "my-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: A test skill\n---\n\n# My Skill\n\nDoes things."
        )
        scripts_dir = skills_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "run.py").write_text("print('hello')")

        skills = scan_created_skills(str(tmp_path))
        assert len(skills) == 1
        assert skills[0]["name"] == "my-skill"
        assert skills[0]["frontmatter"]["name"] == "my-skill"
        assert skills[0]["has_scripts"] is True
        assert skills[0]["scripts_count"] == 1
        assert skills[0]["content_length"] > 0

    def test_ignores_non_skill_dirs(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "random_file.txt").write_text("not a skill")
        no_md = skills_dir / "no-skill-md"
        no_md.mkdir()
        (no_md / "README.md").write_text("not a SKILL.md")

        skills = scan_created_skills(str(tmp_path))
        assert skills == []

    def test_skill_without_frontmatter(self, tmp_path):
        skill_dir = tmp_path / "skills" / "plain"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Just a heading\n\nNo frontmatter.")

        skills = scan_created_skills(str(tmp_path))
        assert len(skills) == 1
        assert skills[0]["frontmatter"] == {}

    def test_exclude_names_filters_seed_skills(self, tmp_path):
        skills_root = tmp_path / "skills"
        for name, body in (
            ("skill-creator", "---\nname: skill-creator\n---\n"),
            ("other", "---\nname: other\n---\n"),
        ):
            d = skills_root / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(body)

        all_skills = scan_created_skills(str(tmp_path))
        assert {s["name"] for s in all_skills} == {"skill-creator", "other"}

        filtered = scan_created_skills(str(tmp_path), exclude_names=frozenset({"skill-creator"}))
        assert len(filtered) == 1
        assert filtered[0]["name"] == "other"


# ---------------------------------------------------------------------------
# aggregate_metrics
# ---------------------------------------------------------------------------


class TestAggregateMetrics:
    def test_basic_aggregation(self):
        results = [
            {
                "task_id": "t1",
                "baseline_grade": {"score": 0.5},
                "evolution_grade": {"score": 0.8},
                "baseline_usage": {
                    "total_tokens": 1000,
                    "total_cost_usd": 0.1,
                    "total_execution_time_seconds": 10,
                },
                "evolution_usage": {
                    "total_tokens": 800,
                    "total_cost_usd": 0.08,
                    "total_execution_time_seconds": 8,
                },
                "sub_problem_scores_baseline": [0.5, 0.5, 0.5],
                "sub_problem_scores_evolution": [0.8, 0.8, 0.8],
                "created_skills": [{"name": "test-skill"}],
                "skill_quality_score": 0.7,
            },
        ]
        m = aggregate_metrics(results)
        assert "evoscore" in m
        assert "fail2pass" in m
        assert "consistency" in m
        assert "efficiency" in m
        assert "skill_quality" in m
        assert "created_skills" in m
        assert m["created_skills"]["total_count"] == 1
        assert m["fail2pass"]["overall"]["fail2pass"] > 1.0

    def test_empty_results(self):
        m = aggregate_metrics([])
        # With no data: fail2pass=1.0 (neutral), eff_gain=1.0 (neutral)
        # f2p_norm = 1.0/2.0 = 0.5, eff_norm = 1.0/2.0 = 0.5
        # evoscore = 0.4*0 + 0.2*0.5 + 0.2*0 + 0.1*0.5 + 0.1*0 = 0.15
        assert m["evoscore"] == pytest.approx(0.15)
        assert m["created_skills"]["total_count"] == 0


class TestAggregateThreeModeMetrics:
    def test_execution_and_end_to_end_usage_are_separate(self):
        baseline = {
            "t1": {
                "mean_score": 0.5,
                "usage": {
                    "total_tokens": 100,
                    "total_cost_usd": 1.0,
                    "total_execution_time_seconds": 10,
                },
            }
        }
        preskill = {
            "t1": {
                "mean_score": 0.75,
                "usage": {
                    "total_tokens": 60,
                    "total_cost_usd": 0.6,
                    "total_execution_time_seconds": 6,
                },
                "end_to_end_usage": {
                    "total_tokens": 160,
                    "total_cost_usd": 1.6,
                    "total_execution_time_seconds": 16,
                },
                "created_skills": [{"name": "pre"}],
                "skill_quality_score": 0.8,
            }
        }
        postskill = {
            "t1": {
                "mean_score": 0.9,
                "first_pass_mean_score": 0.4,
                "usage": {
                    "total_tokens": 50,
                    "total_cost_usd": 0.5,
                    "total_execution_time_seconds": 5,
                },
                "end_to_end_usage": {
                    "total_tokens": 220,
                    "total_cost_usd": 2.2,
                    "total_execution_time_seconds": 22,
                },
                "created_skills": [{"name": "post"}],
                "skill_quality_score": 0.6,
                "skill_mutation_violation": True,
            }
        }

        metrics = aggregate_three_mode_metrics(
            baseline_results=baseline,
            preskill_results=preskill,
            postskill_results=postskill,
        )

        assert metrics["execution_only"]["mean_scores"]["baseline"] == pytest.approx(0.5)
        assert metrics["execution_only"]["ratios_vs_baseline"]["preskill"] == pytest.approx(1.5)
        assert metrics["execution_only"]["usage"]["preskill"]["total_tokens"] == 60
        assert metrics["end_to_end"]["usage"]["preskill"]["total_tokens"] == 160
        assert metrics["postskill"]["first_pass_mean"] == pytest.approx(0.4)
        assert metrics["postskill"]["second_pass_mean"] == pytest.approx(0.9)
        assert metrics["postskill"]["second_vs_first_delta"] == pytest.approx(0.5)
        assert metrics["created_skills"]["preskill_count"] == 1
        assert metrics["created_skills"]["postskill_count"] == 1
        assert metrics["skill_quality"]["preskill_mean"] == pytest.approx(0.8)
        assert metrics["skill_mutation_violations"]["postskill"] == 1

    def test_empty_three_mode_metrics(self):
        metrics = aggregate_three_mode_metrics(
            baseline_results={},
            preskill_results={},
            postskill_results={},
        )

        assert metrics["execution_only"]["mean_scores"] == {
            "baseline": 0.0,
            "preskill": 0.0,
            "postskill": 0.0,
        }
        assert metrics["created_skills"]["preskill_count"] == 0
        assert metrics["postskill"]["second_vs_first_ratio"] == 1.0
