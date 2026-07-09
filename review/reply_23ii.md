We thank the reviewer for the careful, detailed reading.

**Single run / variance.** We agree that Table 2 does not estimate execution variance. Alternate-judge checks regrade fixed outputs and test only grader sensitivity: on 12 hybrid tasks (36 outputs), two judges give Pearson \(r=0.997\) (mean \(|\Delta|=0.014\)) and \(r=0.951\). Separately, three executions of the 12-task `GPT-5.4 mini`/OpenClaw subset have descriptive SDs of 5.51/6.17/5.49 points for Baseline/PreSkill/PostSkill. Runs 2/3 changed route, endpoint, judge, timeout, and transcript fallback; 5/72 cells had infrastructure errors. Thus these SDs describe operational sensitivity, not controlled seed variance or confidence intervals.

**Same sub-problems.** Correct: PostSkill v1 reruns the same task/fixtures and measures within-task distillation or repair, not held-out transfer. Because its summary receives grading and output evidence, it may encode a task-specific patch. We will narrow "reusable" to fresh same-task execution; a train/eval sub-problem split is required to test transfer.

**Catastrophic drops with 0 skills.** Transcript inspection finds a workflow-failure signature but not one root cause. In 90/101 (89.1%) `GPT-5.4` and 86/101 (85.1%) `DeepSeek-V4-Pro` OpenClaw PostSkill results, every recorded assistant message has empty content; comparison rows have 0/101 and 1/101. Nanobot `DeepSeek-V4-Pro` PreSkill likewise hits its degenerate-response fallback in 89/101 tasks. This is consistent with provider/gateway, adapter, concurrency, or prompt/runtime failure; these rows cannot diagnose skill quality or inherent runtime capability.

Zero-skill counts remain ambiguous: current logs cannot distinguish an invalid/missing artifact from an explicit opt-out, and the analysis above examines reuse, not authoring. We will mark them unresolved and log `authoring_attempted_no_artifact` versus `opted_out`.

Diagnostic reproductions are not corrected replacements. OpenClaw run `0084` scores 45.1/90.2/92.3 (PostSkill first/second: 94.1/92.3) over 101 loader tasks, but changes route, endpoint, judge, and workers and has one mutation violation per skill mode. Nanobot `0084` scores 9.7/18.5/76.7 (79.5/76.7 first/second) on only 12 hybrid tasks, with a changed route/judge/workers and a grading compatibility fix. They show the collapses are not invariant, but are not protocol-matched substitutes. We will caveat/exclude contaminated rows and replace them only after matched, mutation-clean reruns.

**Table 7 (+19.84 empty scaffold).** This successful four-task wrapper ablation is not equivalent to zero-skill rows with degenerate executions. It shows wrapper/context-reset confounding can be material, but cannot estimate skill content's causal contribution.

**Cost/usage.**
- PostSkill end-to-end = first execution + summary/authoring + second execution; execution-only isolates the second. We will also report summary+second after treating the first run as sunk, and second-only marginal reuse.
- For three OpenClaw rows with intact usage, summary+second consumes 2.4--2.7\(\times\) Baseline total-token units. We will add input/output/cache components and limit this claim to those rows.
- Finding-3 ratios are all OpenClaw; we will label them. Nanobot's zero-token records occur even on successful tasks, so we will mark missing adapter usage rather than infer API failure.

**Workspace isolation.** Isolation is per task phase, not sub-problem: all sub-problems share one phase session/workspace, while PreSkill author/reuse and PostSkill first/summary/second phases use fresh workspaces. We will clarify the text and Figure 1.
