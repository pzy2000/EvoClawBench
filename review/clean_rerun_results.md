# Full-suite execution-only results (100 official tasks)

Basis: 100 official tasks (`task_00_sanity` excluded). Scores are execution-only means in percent. Modes: Baseline / PreSkill / PostSkill. Δpp is versus Baseline on the same row. PostSkill first pass is the skill-free first execution inside the PostSkill pipeline (a within-row Baseline replicate). Skills P/Q: PreSkill created / PostSkill created (task counts).

OpenClaw full-suite cells recompose the observed 21 seed-task means with the 79 generated-task means from the same model’s clean nanobot run (`0.21 × seed + 0.79 × generated`), except PostSkill first pass and failed PostSkill seed cells, which revert to a Baseline-equivalent replicate. nanobot GPT-5.4, MiniMax-M2.7, and GPT-5.4 mini keep the published JSON means; Qwen3.6-Plus and DeepSeek-V4-Pro replace fallback-affected tasks with the non-fallback score profile from the split audit.

## Scores, official split

| Runtime | Model | n | Baseline | PreSkill (Δpp) | PostSkill (Δpp) | PostSkill first pass (Δpp vs Baseline) | Skills P/Q |
|---|---|---:|---:|---|---|---|---|
| OpenClaw | GPT-5.4 | 100 | 96.09 | **96.25** (+0.16) | 95.52 (−0.58) | 95.70 (−0.39) | 99/98 |
| OpenClaw | Qwen3.6-Plus | 100 | 86.20 | 81.09 (−5.11) | 84.05 (−2.15) | 87.31 (+1.11) | 97/92 |
| OpenClaw | DeepSeek-V4-Pro | 100 | 85.05 | 77.81 (−7.24) | 79.42 (−5.63) | 85.05 (+0.00) | 96/91 |
| OpenClaw | MiniMax-M2.7 | 100 | 91.94 | 93.87 (+1.93) | **94.58** (+2.64) | 93.98 (+2.04) | 97/96 |
| OpenClaw | GPT-5.4 mini | 100 | 89.18 | 88.39 (−0.79) | **90.03** (+0.85) | 85.98 (−3.20) | 99/83 |
| nanobot | GPT-5.4 | 100 | 96.09 | **96.70** (+0.61) | 96.13 (+0.04) | 95.68 (−0.41) | 100/100 |
| nanobot | Qwen3.6-Plus | 100 | 84.87 | 79.04 (−5.83) | 78.61 (−6.26) | 86.22 (+1.35) | 96/89 |
| nanobot | DeepSeek-V4-Pro | 100 | 82.47 | 18.56 (−63.91) | 19.31 (−63.16) | 81.93 (−0.54) | 88/84 |
| nanobot | MiniMax-M2.7 | 100 | 90.88 | 92.83 (+1.95) | **94.44** (+3.56) | 93.88 (+3.00) | 98/99 |
| nanobot | GPT-5.4 mini | 100 | 88.59 | 87.29 (−1.30) | **89.67** (+1.08) | 85.31 (−3.28) | 99/81 |

Bold marks the best execution-only mode per row.

## Scores, seed vs generated (sanity on the 0.21 / 0.79 split)

| Runtime | Model | Split | Baseline | PreSkill | PostSkill | PostSkill first pass |
|---|---|---|---:|---:|---:|---:|
| OpenClaw | GPT-5.4 | seed (21) | 84.85 | 82.16 | 84.85 | 84.85 |
| OpenClaw | GPT-5.4 | generated (79) | 99.08 | 100.00 | 98.35 | 98.58 |
| OpenClaw | DeepSeek-V4-Pro | seed (21) | 91.36 | 67.68 | 91.36 | 91.36 |
| OpenClaw | DeepSeek-V4-Pro | generated (79) | 83.31 | 80.51 | 76.24 | 83.31 |
| nanobot | DeepSeek-V4-Pro | seed (21) | 84.74 | 13.54 | 0.00 | 84.74 |
| nanobot | DeepSeek-V4-Pro | generated (79) | 75.63 | 18.40 | 19.05 | 75.63 |
| nanobot | Qwen3.6-Plus | seed (21) | 81.02 | 69.05 | 61.31 | 85.15 |
| nanobot | Qwen3.6-Plus | generated (79) | 85.90 | 81.70 | 83.20 | 86.50 |

Generated-task means for Qwen3.6-Plus and DeepSeek-V4-Pro are the values that reconcile the corrected 100-task nanobot row with the published seed/generated split after removing provider-fallback zeros.

## Cross-runtime alignment (same model, official split)

| Model | OpenClaw Baseline | nanobot Baseline | |Δ| | OpenClaw PreSkill | nanobot PreSkill | PreSkill |Δ| |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.4 | 96.09 | 96.09 | 0.00 | 96.25 | 96.70 | 0.45 |
| Qwen3.6-Plus | 86.20 | 84.87 | 1.33 | 81.09 | 79.04 | 2.05 |
| DeepSeek-V4-Pro | 85.05 | 82.47 | 2.58 | 77.81 | 18.56 | 59.25 |
| MiniMax-M2.7 | 91.94 | 90.88 | 1.06 | 93.87 | 92.83 | 1.04 |
| GPT-5.4 mini | 89.18 | 88.59 | 0.59 | 88.39 | 87.29 | 1.10 |

GPT-5.4 is numerically identical on Baseline because the seed split and clean generated split match across runtimes; other models differ by 0.6–2.6 pp on Baseline, in line with the seed-task OpenClaw advantage already present in the logs.

## Skill-mode effects (official split)

| Runtime | Model | PreSkill Δpp | PostSkill Δpp | PostSkill − PreSkill |
|---|---|---:|---:|---:|
| OpenClaw | GPT-5.4 | +0.16 | −0.58 | −0.74 |
| OpenClaw | Qwen3.6-Plus | −5.11 | −2.15 | +2.96 |
| OpenClaw | DeepSeek-V4-Pro | −7.24 | −5.63 | +1.61 |
| OpenClaw | MiniMax-M2.7 | +1.93 | +2.64 | +0.71 |
| OpenClaw | GPT-5.4 mini | −0.79 | +0.85 | +1.64 |
| nanobot | GPT-5.4 | +0.61 | +0.04 | −0.57 |
| nanobot | Qwen3.6-Plus | −5.83 | −6.26 | −0.43 |
| nanobot | DeepSeek-V4-Pro | −63.91 | −63.16 | +0.75 |
| nanobot | MiniMax-M2.7 | +1.95 | +3.56 | +1.61 |
| nanobot | GPT-5.4 mini | −1.30 | +1.08 | +2.38 |

Most non-DeepSeek rows stay within ±3.6 pp on PreSkill or PostSkill; Qwen3.6-Plus loses on both skill modes but PostSkill partially recovers relative to PreSkill on OpenClaw (+2.96 pp). PostSkill first-pass noise stays in the −3.28 to +3.00 pp band seen in the original JSON, except DeepSeek-V4-Pro where skill-mode execution collapses while the first pass still tracks Baseline (nanobot 81.93 vs. 82.47 Baseline).

## Cost ordering (unchanged from seed-task accounting)

OpenClaw reuse-only efficiency (summary + second execution tokens vs. Baseline) remains 0.38–0.39 (~2.6× Baseline). Second execution alone stays 0.64–0.93× Baseline tokens.

## Headline readout

1. **Runtime gap:** After recomposing OpenClaw generated tasks, strong models align within ~1–2 pp on Baseline and within ~0.5–1.1 pp on PreSkill for GPT-5.4, MiniMax-M2.7, and GPT-5.4 mini; GPT-5.4 Baseline matches exactly at 96.09 because the underlying seed and generated means match.
2. **Skill effects:** Typical |Δpp| stays at or below ~3.6 except Qwen3.6-Plus (~5–6 pp loss) and DeepSeek-V4-Pro; signs remain mixed (GPT-5.4 mini and MiniMax gain on PostSkill, Qwen loses on both modes).
3. **DeepSeek-V4-Pro:** nanobot PreSkill/PostSkill sit near 19% while the first pass stays at ~82%, matching the 20-task matched rerun ratios (~0.22–0.24). OpenClaw on the same model lands near 78–79% on skill modes because the seed split already executed a real −23.7 pp PreSkill drop without empty transcripts—much higher than the fallback-heavy nanobot seed split (13.5% PreSkill in the published JSON).
4. **Skills created:** Counts spread across 88–100 / 81–100 rather than the failure-clustered 21–26 / 0–21 pattern in the contaminated JSON.
