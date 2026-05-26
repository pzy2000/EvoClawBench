"""Tests for lib_model_pricing — estimated USD cost from token counts."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_model_pricing import (
    enrich_usage_with_estimated_cost,
    estimate_cost_usd,
    resolve_pricing_profile_id,
)


class TestResolvePricingProfileId:
    def test_gpt_5_nano_openai_prefix(self):
        assert resolve_pricing_profile_id("openai/gpt-5-nano") == "gpt-5-nano"

    def test_minimax_m25_slash_form(self):
        assert resolve_pricing_profile_id("openai/MiniMax/MiniMax-M2.5") == "minimax-m2.5"

    def test_minimax_lowercase(self):
        assert resolve_pricing_profile_id("minimax/minimax-m2.5-20260211") == "minimax-m2.5"

    def test_qwen_35_plus(self):
        assert resolve_pricing_profile_id("openai/qwen3.5-plus") == "qwen3.5-plus"

    def test_unknown_returns_none(self):
        assert resolve_pricing_profile_id("some/vendor/unknown-model-v99") is None


class TestEstimateCostUsd:
    def test_gpt_5_nano_matches_openai_table(self):
        """OpenAI platform Standard: gpt-5-nano $0.05/M in, $0.005/M cache, $0.40/M out."""
        cost = estimate_cost_usd(
            "openai/gpt-5-nano",
            {
                "input_tokens": 1_000_000,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
            },
        )
        assert cost == pytest.approx(0.05, rel=1e-6)

        cost2 = estimate_cost_usd(
            "gpt-5-nano",
            {
                "input_tokens": 0,
                "output_tokens": 1_000_000,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
            },
        )
        assert cost2 == pytest.approx(0.40, rel=1e-6)

    def test_gpt_5_nano_includes_cache_read(self):
        cost = estimate_cost_usd(
            "openai/gpt-5-nano",
            {
                "input_tokens": 1_000_000,
                "output_tokens": 0,
                "cache_read_tokens": 1_000_000,
                "cache_write_tokens": 0,
            },
        )
        # 1M fresh @ 0.05 + 1M cache @ 0.005
        assert cost == pytest.approx(0.055, rel=1e-6)

    def test_minimax_m25_matches_table(self):
        cost = estimate_cost_usd(
            "openai/MiniMax/MiniMax-M2.5",
            {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_tokens": 0},
        )
        assert cost == pytest.approx(0.19 + 0.95, rel=1e-6)

    def test_qwen_35_plus_matches_global_table(self):
        cost = estimate_cost_usd(
            "openai/qwen3.5-plus",
            {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_tokens": 0},
        )
        assert cost == pytest.approx(0.115 + 0.688, rel=1e-6)

    def test_unknown_model_returns_none(self):
        assert (
            estimate_cost_usd(
                "unknown/x",
                {"input_tokens": 1000, "output_tokens": 1000, "cache_read_tokens": 0},
            )
            is None
        )


class TestEnrichUsageWithEstimatedCost:
    def test_keeps_provider_cost_when_positive(self):
        u = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "cost_usd": 0.42,
            "request_count": 1,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
        out = enrich_usage_with_estimated_cost("openai/gpt-5-nano", dict(u))
        assert out["cost_usd"] == pytest.approx(0.42)
        assert out.get("cost_usd_source") == "provider"

    def test_fills_when_provider_zero(self):
        u = {
            "input_tokens": 1_000_000,
            "output_tokens": 500_000,
            "total_tokens": 1_500_000,
            "cost_usd": 0.0,
            "request_count": 1,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
        out = enrich_usage_with_estimated_cost("openai/gpt-5-nano", u)
        assert out["cost_usd"] > 0
        assert out.get("cost_usd_source") == "estimated"

    def test_unknown_model_leaves_zero(self):
        u = {
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
            "cost_usd": 0.0,
            "request_count": 1,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
        out = enrich_usage_with_estimated_cost("vendor/unknown", u)
        assert out["cost_usd"] == 0.0
        assert out.get("cost_usd_source") == "unknown"
