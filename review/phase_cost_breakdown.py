"""Aggregate phase-level usage (tokens/time) for the 10 main-table result files.

Reads each task's existing ``phase_usage`` breakdown (first_execution / skill_summary /
second_execution for postskill, skill_generation / execution for preskill) that the
harness already records per-task but does not roll up into ``metrics``. Produces a
reviewer-facing table separating:
  - baseline (single execution)
  - preskill: skill_generation vs execution
  - postskill: first_execution (≈ a baseline-equivalent run) vs skill_summary +
    second_execution ("reuse-only", i.e. excluding the first, baseline-equivalent pass)

This is a read-only analysis script for the OpenReview rebuttal; it does not modify the
paper or the benchmark harness.
"""

import glob
import json
import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "evoclawbench", "results")

ROWS = [
    ("openclaw", "GPT-5.4", "0061_openai-gpt-5-4_openclaw.json"),
    ("openclaw", "Qwen3.6-Plus", "0062_openai-qwen3-6-plus_openclaw.json"),
    ("openclaw", "DeepSeek-V4-Pro", "0063_openai-deepseek-v4-pro_openclaw.json"),
    ("openclaw", "MiniMax-M2.7", "0064_openai-minimax-minimax-m2-7_openclaw.json"),
    ("openclaw", "GPT-5.4 mini", "0065_openai-gpt-5-4-mini_openclaw.json"),
    ("nanobot", "GPT-5.4", "0079_openai-gpt-5-4_nanobot.json"),
    ("nanobot", "Qwen3.6-Plus", "0075_openai-qwen3-6-plus_nanobot.json"),
    ("nanobot", "DeepSeek-V4-Pro", "0076_openai-deepseek-v4-pro_nanobot.json"),
    ("nanobot", "MiniMax-M2.7", "0080_openai-minimax-minimax-m2-7_nanobot.json"),
    ("nanobot", "GPT-5.4 mini", "0081_openai-gpt-5-4-mini_nanobot.json"),
]


def sum_tokens(entries, phase_keys):
    total = 0
    n = 0
    for e in entries:
        pu = e.get("phase_usage", {})
        for k in phase_keys:
            total += pu.get(k, {}).get("total_tokens", 0)
        n += 1
    return total, n


def sum_baseline_tokens(baseline_results):
    total = 0
    for e in baseline_results.values():
        total += e.get("usage", {}).get("total_tokens", 0)
    return total


def main():
    print(
        f"{'Runtime':8} {'Model':16} {'Baseline':>10} {'Pre:author':>11} {'Pre:exec':>10} "
        f"{'Post:first':>11} {'Post:summary':>13} {'Post:second':>12} {'Post reuse-only':>16} "
        f"{'ReuseOnly/Base':>15}"
    )
    rows_out = []
    for runtime, label, fname in ROWS:
        path = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(path):
            print(f"MISSING: {fname}")
            continue
        d = json.load(open(path))
        baseline = d.get("baseline_results", {})
        preskill = list(d.get("preskill_results", {}).values())
        postskill = list(d.get("postskill_results", {}).values())

        base_tok = sum_baseline_tokens(baseline)
        pre_author_tok, _ = sum_tokens(preskill, ["skill_generation"])
        pre_exec_tok, _ = sum_tokens(preskill, ["execution"])
        post_first_tok, _ = sum_tokens(postskill, ["first_execution"])
        post_summary_tok, _ = sum_tokens(postskill, ["skill_summary"])
        post_second_tok, _ = sum_tokens(postskill, ["second_execution"])
        post_reuse_only = post_summary_tok + post_second_tok

        ratio = (base_tok / post_reuse_only) if post_reuse_only else float("nan")

        print(
            f"{runtime:8} {label:16} {base_tok:>10} {pre_author_tok:>11} {pre_exec_tok:>10} "
            f"{post_first_tok:>11} {post_summary_tok:>13} {post_second_tok:>12} {post_reuse_only:>16} "
            f"{ratio:>15.3f}"
        )
        rows_out.append(
            {
                "runtime": runtime,
                "model": label,
                "baseline_tokens": base_tok,
                "preskill_author_tokens": pre_author_tok,
                "preskill_execute_tokens": pre_exec_tok,
                "postskill_first_execution_tokens": post_first_tok,
                "postskill_skill_summary_tokens": post_summary_tok,
                "postskill_second_execution_tokens": post_second_tok,
                "postskill_reuse_only_tokens": post_reuse_only,
                "reuse_only_token_efficiency_gain_vs_baseline": ratio,
            }
        )

    out_path = os.path.join(os.path.dirname(__file__), "phase_cost_breakdown.json")
    with open(out_path, "w") as f:
        json.dump(rows_out, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
