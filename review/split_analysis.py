"""Read-only re-analysis of the ten main-table result files.

Splits every row into the 21 seed tasks (task_01-task_21), the 79 generated hard-mode
tasks (task_22-task_100), and the 100 official tasks (task_00_sanity excluded), and
reports per split:

  - mean execution-only score per mode and percentage-point deltas vs. Baseline,
  - paired task-bootstrap 95% CIs for the deltas (task-sampling uncertainty only),
  - the PostSkill first-pass score, which is a second skill-free execution of the
    same tasks and therefore a within-row Baseline replicate,
  - final-phase execution status counts, fully-empty OpenClaw assistant transcripts,
    and nanobot "no response to give" fallbacks,
  - created-skill counts,
  - phase-level token usage (input / output / cache-read / total) and wall time.

It only reads files under evoclawbench/results/ and writes split_analysis.{json,md}
next to this script.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "evoclawbench" / "results"
OUT_DIR = Path(__file__).resolve().parent

ROWS = [
    ("OpenClaw", "GPT-5.4", "0061_openai-gpt-5-4_openclaw.json"),
    ("OpenClaw", "Qwen3.6-Plus", "0062_openai-qwen3-6-plus_openclaw.json"),
    ("OpenClaw", "DeepSeek-V4-Pro", "0063_openai-deepseek-v4-pro_openclaw.json"),
    ("OpenClaw", "MiniMax-M2.7", "0064_openai-minimax-minimax-m2-7_openclaw.json"),
    ("OpenClaw", "GPT-5.4 mini", "0065_openai-gpt-5-4-mini_openclaw.json"),
    ("nanobot", "GPT-5.4", "0079_openai-gpt-5-4_nanobot.json"),
    ("nanobot", "Qwen3.6-Plus", "0075_openai-qwen3-6-plus_nanobot.json"),
    ("nanobot", "DeepSeek-V4-Pro", "0076_openai-deepseek-v4-pro_nanobot.json"),
    ("nanobot", "MiniMax-M2.7", "0080_openai-minimax-minimax-m2-7_nanobot.json"),
    ("nanobot", "GPT-5.4 mini", "0081_openai-gpt-5-4-mini_nanobot.json"),
]

MODES = ("baseline", "preskill", "postskill")
SPLITS = {
    "official": lambda n: 1 <= n <= 100,
    "seed": lambda n: 1 <= n <= 21,
    "generated": lambda n: 22 <= n <= 100,
}
PHASES = {
    "preskill": ("skill_generation", "execution"),
    "postskill": ("first_execution", "skill_summary", "second_execution"),
}
TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_read_tokens", "total_tokens")
FALLBACK = "no response to give"
N_BOOT = 10000


def task_num(task_id: str) -> int:
    return int(re.match(r"task_(\d+)", task_id).group(1))


def score(entry: dict) -> float:
    if "mean_score" in entry:
        return float(entry["mean_score"])
    grades = entry.get("grades") or []
    if not grades:
        return 0.0
    return sum(g["score"] / (g.get("max_score") or 1.0) for g in grades) / len(grades)


def transcript_texts(result: dict) -> list[str]:
    texts = []
    for item in result.get("transcript") or []:
        message = item.get("message") if isinstance(item, dict) else None
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text", ""))
    return texts


def fully_empty(result: dict) -> bool:
    msgs = [
        t["message"]
        for t in result.get("transcript") or []
        if isinstance(t, dict)
        and t.get("type") == "message"
        and isinstance(t.get("message"), dict)
        and t["message"].get("role") == "assistant"
    ]
    return bool(msgs) and all(not (m.get("content") or []) for m in msgs)


def paired_ci(diffs: list[float], rng: random.Random) -> tuple[float, float]:
    if not diffs:
        return (float("nan"), float("nan"))
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT))
    return (means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT) - 1])


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def analyze(runtime: str, model: str, fname: str, rng: random.Random) -> dict:
    data = json.loads((RESULTS_DIR / fname).read_text())
    per_mode = {m: data.get(f"{m}_results") or {} for m in MODES}
    row: dict = {"runtime": runtime, "model": model, "source": fname, "splits": {}}

    for split, keep in SPLITS.items():
        out: dict = {}
        base = {t: score(e) for t, e in per_mode["baseline"].items() if keep(task_num(t))}
        out["n_tasks"] = len(base)
        for mode in MODES:
            entries = {t: e for t, e in per_mode[mode].items() if keep(task_num(t))}
            scores = {t: score(e) for t, e in entries.items()}
            status: dict[str, int] = {}
            empty = fallback = 0
            skills = 0
            for entry in entries.values():
                for res in entry.get("results") or []:
                    status[res.get("status", "unknown")] = status.get(res.get("status"), 0) + 1
                    empty += fully_empty(res)
                    fallback += FALLBACK in " ".join(transcript_texts(res))
                skills += len(entry.get("created_skills") or [])
            info = {
                "n": len(scores),
                "mean_pct": 100 * mean(list(scores.values())),
                "status": status,
                "fully_empty_transcripts": empty,
                "fallback_hits": fallback,
                "created_skills": skills,
            }
            if mode != "baseline":
                shared = sorted(set(scores) & set(base))
                diffs = [100 * (scores[t] - base[t]) for t in shared]
                info["delta_pp"] = mean(diffs)
                info["delta_ci95_pp"] = paired_ci(diffs, rng)
            if mode == "postskill":
                first = {
                    t: float(e["first_pass_mean_score"])
                    for t, e in entries.items()
                    if e.get("first_pass_mean_score") is not None
                }
                shared = sorted(set(first) & set(base))
                rep = [100 * (first[t] - base[t]) for t in shared]
                info["first_pass_mean_pct"] = 100 * mean(list(first.values()))
                info["first_pass_minus_baseline_pp"] = mean(rep)
                info["first_pass_minus_baseline_ci95_pp"] = paired_ci(rep, rng)
                info["first_pass_vs_baseline_mean_abs_task_diff_pp"] = mean([abs(x) for x in rep])
                second_vs_first = [
                    100 * (scores[t] - first[t]) for t in sorted(set(first) & set(scores))
                ]
                info["second_minus_first_pp"] = mean(second_vs_first)
            out[mode] = info

        usage: dict = {"baseline": {k: 0 for k in TOKEN_KEYS}}
        usage["baseline"]["time_s"] = 0.0
        for t, e in per_mode["baseline"].items():
            if not keep(task_num(t)):
                continue
            u = e.get("usage") or {}
            for k in TOKEN_KEYS:
                usage["baseline"][k] += u.get(k, 0) or 0
            usage["baseline"]["time_s"] += e.get("execution_time") or 0.0
        for mode, phases in PHASES.items():
            for phase in phases:
                acc = {k: 0 for k in TOKEN_KEYS}
                acc["time_s"] = 0.0
                for t, e in per_mode[mode].items():
                    if not keep(task_num(t)):
                        continue
                    pu = (e.get("phase_usage") or {}).get(phase) or {}
                    for k in TOKEN_KEYS:
                        acc[k] += pu.get(k, 0) or 0
                    acc["time_s"] += pu.get("total_execution_time_seconds", 0.0) or 0.0
                usage[f"{mode}:{phase}"] = acc
        out["usage"] = usage
        row["splits"][split] = out
    return row


def fmt_ci(ci: tuple[float, float]) -> str:
    return f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"


def to_markdown(rows: list[dict]) -> str:
    lines = ["# Split re-analysis of the main-table result files", ""]
    for split in SPLITS:
        lines += [
            f"## Scores, {split} split",
            "",
            (
                "| Runtime | Model | n | Baseline | PreSkill (Δpp, 95% CI) | PostSkill (Δpp, 95% CI) "
                "| PostSkill first pass (Δpp vs Baseline) | Skills P/Q |"
            ),
            "|---|---|---:|---:|---|---|---|---|",
        ]
        for r in rows:
            s = r["splits"][split]
            b, p, q = s["baseline"], s["preskill"], s["postskill"]
            lines.append(
                f"| {r['runtime']} | {r['model']} | {s['n_tasks']} | {b['mean_pct']:.2f} "
                f"| {p['mean_pct']:.2f} ({p['delta_pp']:+.2f}, {fmt_ci(p['delta_ci95_pp'])}) "
                f"| {q['mean_pct']:.2f} ({q['delta_pp']:+.2f}, {fmt_ci(q['delta_ci95_pp'])}) "
                f"| {q['first_pass_mean_pct']:.2f} ({q['first_pass_minus_baseline_pp']:+.2f}, "
                f"{fmt_ci(q['first_pass_minus_baseline_ci95_pp'])}) "
                f"| {p['created_skills']}/{q['created_skills']} |"
            )
        lines.append("")
    for split in ("official", "seed"):
        lines += [
            f"## Final-phase execution status, {split} split",
            "",
            "| Runtime | Model | Mode | Status | Fully-empty assistant transcripts | Fallback hits |",
            "|---|---|---|---|---:|---:|",
        ]
        for r in rows:
            for mode in MODES:
                m = r["splits"][split][mode]
                lines.append(
                    f"| {r['runtime']} | {r['model']} | {mode} | {m['status']} "
                    f"| {m['fully_empty_transcripts']} | {m['fallback_hits']} |"
                )
        lines.append("")
    lines += [
        "## Token-efficiency ratios vs. Baseline, seed split (Baseline tokens / candidate tokens)",
        "",
        (
            "| Runtime | Model | Pre exec-only | Pre end-to-end | Post second-only | Post reuse-only "
            "(summary+second) | Post end-to-end | Output share of Baseline tokens |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        u = r["splits"]["seed"]["usage"]
        tot = {k: v["total_tokens"] for k, v in u.items()}
        base = tot["baseline"]

        def ratio(x: int, base: int = base) -> str:
            return f"{base / x:.2f}" if base and x else "n/a"

        pre_e2e = tot["preskill:skill_generation"] + tot["preskill:execution"]
        reuse = tot["postskill:skill_summary"] + tot["postskill:second_execution"]
        post_e2e = reuse + tot["postskill:first_execution"]
        out_share = f"{u['baseline']['output_tokens'] / base:.3f}" if base else "n/a"
        lines.append(
            f"| {r['runtime']} | {r['model']} | {ratio(tot['preskill:execution'])} | {ratio(pre_e2e)} "
            f"| {ratio(tot['postskill:second_execution'])} | {ratio(reuse)} | {ratio(post_e2e)} "
            f"| {out_share} |"
        )
    lines += [
        "",
        "## Phase token usage, seed split (millions of tokens: input / output / cache-read / total)",
        "",
    ]
    for r in rows:
        u = r["splits"]["seed"]["usage"]
        parts = []
        for key, vals in u.items():
            parts.append(
                f"{key}={vals['input_tokens'] / 1e6:.2f}/{vals['output_tokens'] / 1e6:.3f}/"
                f"{vals['cache_read_tokens'] / 1e6:.2f}/{vals['total_tokens'] / 1e6:.2f}"
                f" ({vals['time_s'] / 3600:.2f}h)"
            )
        lines.append(f"- {r['runtime']} {r['model']}: " + "; ".join(parts))
    return "\n".join(lines) + "\n"


def main() -> None:
    rng = random.Random(20260925)
    rows = [analyze(rt, m, f, rng) for rt, m, f in ROWS]
    (OUT_DIR / "split_analysis.json").write_text(json.dumps(rows, indent=2))
    md = to_markdown(rows)
    (OUT_DIR / "split_analysis.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
