"""
Estimated API cost (USD) from token counts when the runtime reports cost_usd == 0.

Rates are documented in MODEL_PRICING_META and should be refreshed periodically from:
  - OpenAI: https://platform.openai.com/docs/pricing (gpt-5-nano Standard)
  - Alibaba Cloud Model Studio (Global): Qwen3.5-Plus min input/output per 1M USD
  - MiniMax: public API pricing for MiniMax-M2.5 (input / output / cache)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True)
class ModelPricingProfile:
    """USD per 1,000,000 tokens."""

    input_per_million: float
    output_per_million: float
    cache_read_per_million: float = 0.0
    cache_write_per_million: float = 0.0
    notes: str = ""


# Keys are internal profile ids returned by resolve_pricing_profile_id().
MODEL_PRICING: Dict[str, ModelPricingProfile] = {
    "gpt-5-nano": ModelPricingProfile(
        input_per_million=0.05,
        cache_read_per_million=0.005,
        output_per_million=0.40,
        notes="OpenAI API Standard pricing (platform.openai.com/docs/pricing), 2026-03",
    ),
    "qwen3.5-plus": ModelPricingProfile(
        input_per_million=0.115,
        output_per_million=0.688,
        cache_read_per_million=0.115,
        notes=(
            "Alibaba Model Studio Global (US) table: Qwen3.5-Plus "
            "min $0.115/M input, $0.688/M output; cache billed as input if unknown."
        ),
    ),
    "minimax-m2.5": ModelPricingProfile(
        input_per_million=0.19,
        cache_read_per_million=0.03,
        output_per_million=0.95,
        notes="MiniMax M2.5 API list pricing (minimax.io / provider sheets), 2026-03",
    ),
}

MODEL_PRICING_META = {
    "last_reviewed": "2026-03-31",
    "currencies": "USD per 1M tokens unless noted",
    "profiles": {k: {"notes": v.notes} for k, v in MODEL_PRICING.items()},
}


def resolve_pricing_profile_id(model_id: str) -> Optional[str]:
    """Map a user/runtime model string to a pricing profile key."""
    raw = (model_id or "").strip().lower()
    if not raw:
        return None

    # Uniform separators
    compact = raw.replace(" ", "")
    for sep in ("/", "\\"):
        compact = compact.replace(sep, "/")

    if "gpt-5-nano" in compact:
        return "gpt-5-nano"

    if "qwen3.5-plus" in compact or compact.endswith("qwen3.5-plus"):
        return "qwen3.5-plus"

    if "minimax" in compact and "m2.5" in compact:
        return "minimax-m2.5"

    return None


def estimate_cost_usd(model_id: str, usage: Mapping[str, Any]) -> Optional[float]:
    """Return estimated total USD for this usage, or None if model is unknown."""
    profile_id = resolve_pricing_profile_id(model_id)
    if profile_id is None:
        return None
    profile = MODEL_PRICING.get(profile_id)
    if profile is None:
        return None

    inp = int(usage.get("input_tokens") or 0)
    out = int(usage.get("output_tokens") or 0)
    cr = int(usage.get("cache_read_tokens") or 0)
    cw = int(usage.get("cache_write_tokens") or 0)

    scale = 1.0 / 1_000_000.0
    cost = (
        inp * profile.input_per_million * scale
        + out * profile.output_per_million * scale
        + cr * profile.cache_read_per_million * scale
        + cw * profile.cache_write_per_million * scale
    )
    return float(cost)


def enrich_usage_with_estimated_cost(model_id: str, usage: Dict[str, Any]) -> Dict[str, Any]:
    """Attach cost_usd and cost_usd_source: provider | estimated | unknown."""
    out = dict(usage)
    reported = float(out.get("cost_usd") or 0.0)
    if reported > 1e-12:
        out["cost_usd"] = reported
        out["cost_usd_source"] = "provider"
        return out

    est = estimate_cost_usd(model_id, out)
    if est is not None and est > 0.0:
        out["cost_usd"] = est
        out["cost_usd_source"] = "estimated"
        return out

    out["cost_usd_source"] = "unknown"
    return out
