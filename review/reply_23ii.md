We thank the reviewer for the detailed comments.

**Single run / variance.** Agreed: Table 2 lacks variance estimates. Regrading 36 fixed hybrid outputs tests only judge sensitivity (\(r=0.997\), mean \(|\Delta|=0.014\); second judge \(r=0.951\)). Three 12-task executions give Baseline/PreSkill/PostSkill SDs of 5.51/6.17/5.49, but Runs 2/3 changed settings and 5/72 cells had infrastructure errors. This is operational sensitivity, not seed variance or CIs.

**Same sub-problems.** Correct: PostSkill v1 measures same-task repair, not held-out transfer. We will narrow "reusable" accordingly and split sub-problems into a train subset (visible during authoring) and a held-out eval subset for the revision, removing the repair confound.

**0-skill drops vs. Table 7.** Not contradictory: in 90/101 `GPT-5.4` and 86/101 `DeepSeek-V4-Pro` OpenClaw PostSkill second executions, every assistant message is empty (vs. 0/101, 1/101 in comparison rows); nanobot `DeepSeek-V4-Pro` PreSkill hits its fallback in 89/101 tasks. Table 7's empty-scaffold (+19.84) instead comes from a normally executing pipeline with an intentionally empty artifact — different conditions (non-executing vs. executing), not one contradictory outcome.

We since ran a matched 20-task rerun of these three rows (same route family, `mode=all`, 32 workers, current OpenClaw/nanobot builds). The literal fallback string does not recur (0/20 everywhere), but severe collapse still does: `DeepSeek-V4-Pro` PreSkill/Baseline is 0.06 (OpenClaw)/0.23 (nanobot), PostSkill/Baseline 0.19/0.24, 0 mutation violations, and on OpenClaw 0 skills created in PostSkill yet still 3/20 fully-empty second-pass transcripts — directly reproducing the reviewer's "0-skill still collapses" case. `GPT-5.4` instead collapsed on PreSkill this time (ratio 0.09) while PostSkill recovered above Baseline (1.15x), with 2/20 and 5/20 mutation violations we had not previously flagged. The collapse is real and recurs, but which phase collapses is itself unstable across reruns/backends — evidence for instability rather than one deterministic cause. We will report this, add success/failure status logging, and stop treating any single row as clean, mutation-free evidence.

**Table 7 causality.** The four-task ablation is a single-run diagnostic: it shows wrapper/reset effects can be large relative to skill content, but is not powered for a causal skill-content estimate; we will state this scope explicitly.

**Cost.** We agree end-to-end framing is unfair to PostSkill and will make summary+second (first run sunk) and second-only marginal reuse the primary efficiency metrics, not end-to-end totals. From existing per-task `phase_usage` fields (no new experiment):

| Model | Baseline | PreSkill author | PreSkill exec | PostSkill 1st exec | PostSkill summary | PostSkill 2nd exec | Reuse-only | Baseline/reuse-only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.6-Plus | 5,526,752 | 9,352,731 | 5,228,487 | 4,848,001 | 7,754,522 | 5,731,045 | 13,485,567 | 0.410 |
| MiniMax-M2.7 | 4,059,607 | 11,224,760 | 8,106,279 | 4,263,403 | 4,702,735 | 6,433,952 | 11,136,687 | 0.365 |
| GPT-5.4 mini | 3,904,034 | 7,350,407 | 4,997,946 | 3,850,169 | 5,361,288 | 4,875,251 | 10,236,539 | 0.381 |

Excluding the first pass entirely, reuse-only still costs \(\sim\)2.4--2.7\(\times\) Baseline tokens. `GPT-5.4`/`DeepSeek-V4-Pro` rows are omitted (PostSkill corrupted, see above); nanobot rows are omitted because per-task `usage.total_tokens` \(\approx 0\) for these models, a pre-existing adapter gap, not near-zero cost. We will add input/output/cache splits and mark omitted cells in the revision. Finding-3 ratios on page 7 are OpenClaw-only for the same reason.

**Workspace isolation.** Isolation is per task phase, not sub-problem: sub-problems share one phase workspace; skill phases use fresh workspaces. We will clarify the text and Figure 1.
