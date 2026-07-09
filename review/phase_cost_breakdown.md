# Phase-level usage breakdown (supplementary analysis for rebuttal to Reviewer 23ii)

Read-only post-processing of the existing per-task `phase_usage` fields already recorded
in the main-table result JSON files (`evoclawbench/results/0061-0065,0075,0076,0079-0081`).
These fields exist per task but are not currently rolled up into the top-level `metrics`
object, so this script (`phase_cost_breakdown.py`) aggregates them directly. Produced to
answer the reviewer's request to separate "first run" (≈ baseline-equivalent) cost from
"skill creation + second run" ("reuse-only") cost for PostSkill.

Token counts are the harness's recorded `total_tokens` units summed over all 101 loader
tasks. Input, output, and cache-read components remain available separately in the source
JSON and should be reported separately when comparing provider cost.

| Runtime | Model | Baseline | PreSkill: author | PreSkill: execute | PostSkill: first_execution | PostSkill: skill_summary | PostSkill: second_execution | PostSkill reuse-only (summary+second) | Baseline / reuse-only |
|---|---|---|---|---|---|---|---|---|---|
| OpenClaw | GPT-5.4 | 4,925,264 | 7,394,934 | 6,239,972 | 0* | 0* | 0* | 0* | n/a* |
| OpenClaw | Qwen3.6-Plus | 5,526,752 | 9,352,731 | 5,228,487 | 4,848,001 | 7,754,522 | 5,731,045 | 13,485,567 | 0.410 |
| OpenClaw | DeepSeek-V4-Pro | 5,198,191 | 7,661,468 | 5,200,278 | 0* | 0* | 0* | 0* | n/a* |
| OpenClaw | MiniMax-M2.7 | 4,059,607 | 11,224,760 | 8,106,279 | 4,263,403 | 4,702,735 | 6,433,952 | 11,136,687 | 0.365 |
| OpenClaw | GPT-5.4 mini | 3,904,034 | 7,350,407 | 4,997,946 | 3,850,169 | 5,361,288 | 4,875,251 | 10,236,539 | 0.381 |
| Nanobot | GPT-5.4 / Qwen3.6-Plus / DeepSeek-V4-Pro / MiniMax-M2.7 / GPT-5.4 mini | 0** | 0** | 0** | 0** | 0** | 0** | 0** | n/a** |

\* Zero because these two rows' PostSkill phases were corrupted in the original run (see
main rebuttal text). Diagnostic reruns exist but are not protocol-matched replacements.

\** Nanobot's per-task `usage.total_tokens` is 0 for essentially all tasks in these five
files even when the task is graded correct, i.e. this is a pre-existing usage-extraction
gap in the nanobot adapter for these model/provider combinations, not something this
rebuttal analysis can retroactively recover.

## Headline number for the rebuttal

For the three OpenClaw rows with intact PostSkill data (Qwen3.6-Plus, MiniMax-M2.7, GPT-5.4
mini), even when we exclude the first, baseline-equivalent execution pass entirely and only
count "skill summarization + second (reused) execution" against a plain Baseline run, the
reuse-only portion still uses **roughly 2.4-2.7x as many tokens as Baseline**
(baseline/reuse-only token-efficiency ratio 0.365-0.410, i.e. inverse ≈ 2.4-2.7). This is the
requested "only skill creation + second run" comparison, computed directly from the
existing per-task `phase_usage` records without needing a new experiment.
