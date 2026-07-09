We thank the reviewer for the detailed comments.

**Single run / variance.** Agreed: Table 2 does not estimate execution variance. Regrading 36 fixed hybrid outputs tests only judge sensitivity (\(r=0.997\), mean \(|\Delta|=0.014\); second judge \(r=0.951\)). Three 12-task executions give Baseline/PreSkill/PostSkill SDs of 5.51/6.17/5.49 points, but Runs 2/3 changed several settings and 5/72 cells had infrastructure errors. These describe operational sensitivity, not seed variance or CIs.

**Same sub-problems.** Correct: PostSkill v1 measures same-task repair, not held-out transfer, and its grading/output evidence may produce task-specific patches. We will narrow "reusable" accordingly; transfer requires a train/eval split.

**Catastrophic drops with 0 skills.** In 90/101 `GPT-5.4` and 86/101 `DeepSeek-V4-Pro` OpenClaw PostSkill results, every recorded assistant message is empty; comparison rows have 0/101 and 1/101. Nanobot `DeepSeek-V4-Pro` PreSkill hits its fallback in 89/101 tasks. This identifies execution-pipeline failure, not its root cause; these rows cannot support skill-quality or runtime-capability claims.

Zero-skill counts remain ambiguous because logs cannot distinguish failed authoring from opt-out. We will add explicit authoring-status logging.

Diagnostic run `0084` does not reproduce the collapses, but is not a replacement: OpenClaw changes route/endpoint/judge/workers and has one mutation violation per skill mode; nanobot covers only 12 hybrid tasks and changes route/judge/workers after a grading fix. We will caveat contaminated rows and replace them only with matched, mutation-clean reruns.

**Table 7.** The four-task empty-scaffold ablation is not equivalent to degenerate zero-skill runs. It shows material wrapper/reset confounding, not a causal skill-content estimate.

**Cost.**
- We will report full PostSkill cost, summary+second with the first run treated as sunk, and second-only marginal reuse.
- For three intact OpenClaw rows, summary+second uses 2.4--2.7\(\times\) Baseline tokens; we will add input/output/cache splits.
- Finding-3 ratios are OpenClaw-only. Nanobot zero-token records are missing adapter usage, not evidence of API failure.

**Workspace isolation.** Isolation is per task phase, not sub-problem. Sub-problems share one phase workspace; skill phases use fresh workspaces. We will clarify the text and Figure 1.
