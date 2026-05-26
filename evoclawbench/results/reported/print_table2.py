"""Print the paper Table 2 rows from sanitized reported-result JSON files."""

from __future__ import annotations

import json
from pathlib import Path


ROWS = [
    ("OpenClaw", "GPT-5.4", "table2_row_01.json"),
    ("OpenClaw", "Qwen3.6-Plus", "table2_row_02.json"),
    ("OpenClaw", "DeepSeek-V4-Pro", "table2_row_03.json"),
    ("OpenClaw", "MiniMax-M2.7", "table2_row_04.json"),
    ("OpenClaw", "GPT-5.4 mini", "table2_row_05.json"),
    ("Nanobot", "GPT-5.4", "table2_row_06.json"),
    ("Nanobot", "Qwen3.6-Plus", "table2_row_07.json"),
    ("Nanobot", "DeepSeek-V4-Pro", "table2_row_08.json"),
    ("Nanobot", "MiniMax-M2.7", "table2_row_09.json"),
    ("Nanobot", "GPT-5.4 mini", "table2_row_10.json"),
]


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{100 * value:.2f}"


def main() -> None:
    base = Path(__file__).resolve().parent
    print("| Runtime | Model | Baseline | PreSkill | PostSkill | Skills |")
    print("|---|---|---:|---:|---:|---:|")
    for runtime, model, filename in ROWS:
        data = json.loads((base / filename).read_text())
        scores = data["metrics"]["execution_only"]["mean_scores"]
        skills = data["metrics"]["created_skills"]
        skill_text = f"{skills['preskill_count']} / {skills['postskill_count']}"
        print(
            f"| {runtime} | `{model}` | {pct(scores.get('baseline'))} | "
            f"{pct(scores.get('preskill'))} | {pct(scores.get('postskill'))} | "
            f"{skill_text} |"
        )


if __name__ == "__main__":
    main()
