"""Read-only diagnostic: quantify empty/degenerate assistant completions in
postskill second-execution transcripts, contrasting collapsed rows against
stable rows in the OpenClaw main-results table.

This script only reads existing result JSON files under
evoclawbench/results/; it does not run any new experiments.
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "evoclawbench" / "results"

ROWS = [
    ("0065_openai-gpt-5-4-mini_openclaw.json", "postskill_results", "GPT-5.4 mini / OpenClaw / postskill (19.36%, stable)"),
    ("0062_openai-qwen3-6-plus_openclaw.json", "postskill_results", "Qwen3.6-Plus / OpenClaw / postskill (19.12%, stable)"),
    ("0061_openai-gpt-5-4_openclaw.json", "postskill_results", "GPT-5.4 / OpenClaw / postskill (1.14%, COLLAPSE)"),
    ("0063_openai-deepseek-v4-pro_openclaw.json", "postskill_results", "DeepSeek-V4-Pro / OpenClaw / postskill (0.00%, COLLAPSE)"),
]

NANOBOT_ROWS = [
    ("0076_openai-deepseek-v4-pro_nanobot.json", "baseline_results", "DeepSeek-V4-Pro / nanobot / baseline (77.77%, stable)"),
    ("0076_openai-deepseek-v4-pro_nanobot.json", "preskill_results", "DeepSeek-V4-Pro / nanobot / preskill (4.80%, COLLAPSE)"),
    ("0076_openai-deepseek-v4-pro_nanobot.json", "postskill_results", "DeepSeek-V4-Pro / nanobot / postskill (0.99%, COLLAPSE)"),
]


def empty_completion_rate(fname: str, mode: str) -> tuple[int, int]:
    """Fraction of task-mode results whose assistant turn(s) had empty content
    (OpenClaw-style message.content == [])."""
    data = json.loads((RESULTS_DIR / fname).read_text())
    payload = data[mode]
    empty = 0
    total = 0
    for _task_id, entry in payload.items():
        for result in entry.get("results", []):
            total += 1
            transcript = result.get("transcript", [])
            assistant_msgs = [
                t
                for t in transcript
                if t.get("type") == "message" and t.get("message", {}).get("role") == "assistant"
            ]
            if assistant_msgs and all(
                len(m["message"].get("content") or []) == 0 for m in assistant_msgs
            ):
                empty += 1
    return empty, total


def no_response_fallback_rate(fname: str, mode: str) -> tuple[int, int]:
    """Fraction of task-mode results whose nanobot transcript text contains
    the nanobot-native degenerate-response fallback string."""
    data = json.loads((RESULTS_DIR / fname).read_text())
    payload = data[mode]
    hits = 0
    total = 0
    for _task_id, entry in payload.items():
        for result in entry.get("results", []):
            total += 1
            transcript = result.get("transcript", [])
            texts = []
            for t in transcript:
                for item in t.get("message", {}).get("content", []) or []:
                    if isinstance(item, dict) and item.get("type") == "text":
                        texts.append(item.get("text", ""))
            if "no response to give" in " ".join(texts):
                hits += 1
    return hits, total


def main():
    print("## OpenClaw postskill second-execution: empty assistant-completion rate\n")
    print("| Row | Empty completions | Rate |")
    print("|---|---:|---:|")
    for fname, mode, label in ROWS:
        empty, total = empty_completion_rate(fname, mode)
        print(f"| {label} | {empty}/{total} | {empty / total:.1%} |")

    print("\n## nanobot: 'no response to give' fallback rate (DeepSeek-V4-Pro)\n")
    print("| Row | Fallback hits | Rate |")
    print("|---|---:|---:|")
    for fname, mode, label in NANOBOT_ROWS:
        hits, total = no_response_fallback_rate(fname, mode)
        print(f"| {label} | {hits}/{total} | {hits / total:.1%} |")


if __name__ == "__main__":
    main()
