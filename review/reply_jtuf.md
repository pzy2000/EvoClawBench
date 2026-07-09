We thank the reviewer for the constructive summary and concrete suggestions. We address each point below.

**W1 (skill content vs. reuse wrapper/workspace/scaffold).** We agree this confound is real; the paper already includes a dedicated ablation to separate it (Sec. 5.3, `task_02/07/15/21`): normal \preskill{} reuse improves the mean score by 4.05 points, but an **empty-skill scaffold** improves by 19.84 points and an **irrelevant skill** by 1.52 points — most of the naive "skill helps" signal is explained by the reuse prompt/context reset, not skill content. For \postskill{}, normal reuse is slightly above baseline (+1.47) while discarding the generated skill after summarization falls below baseline (−4.23). W2 below adds a second, previously unquantified confound source.

**W2 (POSTSKILL as task-specific patching, compounded by zero-skill collapse).** We ran a targeted, read-only transcript analysis to test whether the catastrophic collapses are skill-quality failures or something else. Comparing two collapsed rows (`GPT-5.4`: baseline 18.63%→postskill 1.14%; `DeepSeek-V4-Pro`: 19.99%→0.00%) against two stable rows (`GPT-5.4 mini` 19.36%, `Qwen3.6-Plus` 19.12%) on the same postskill second-execution transcripts:
- Collapsed rows: 89.1% (GPT-5.4) / 85.1% (DeepSeek-V4-Pro) of tasks show an **empty/degenerate first assistant turn** during skill-reuse execution.
- Stable rows: 0.0% (GPT-5.4 mini) / 1.0% (Qwen3.6-Plus).
- Independently, nanobot's DeepSeek-V4-Pro preskill collapse (77.77%→4.80%) corresponds to 89/101 tasks hitting nanobot's own degenerate-response fallback string.

This confirms the reviewer's concern that workflow-level confounds are real, but locates a *specific, previously unreported* mechanism — response degradation under certain prompt/runtime/model combinations — rather than "the skill was bad" or "task-specific overfitting" per se. We will report this as an explicit caveat on the zero-skill-collapse rows in the camera-ready, without changing the headline claims.

**W3 (limited coverage: two runtimes, one local setup, one run/task/mode).** We ran new same-model reruns to turn this into a concrete variance estimate. Using the same 12-task hybrid subset and `GPT-5.4 mini`/OpenClaw/`mode=all` configuration as the paper's subset audit, we reran seeds 2 and 3 (seed 1 = submission run) via a currently available inference gateway — same model, different endpoint from submission time, noted here for transparency.

| Seed | Baseline | Preskill | Postskill |
|---|---:|---:|---:|
| 1 (submission) | 80.96% | 79.77% | 79.21% |
| 2 (rerun) | 77.05% | 69.61% | 68.54% |
| 3 (rerun) | 70.09% | 80.75% | 76.11% |
| **mean ± std** | **76.03 ± 5.51** | **76.71 ± 6.17** | **74.62 ± 5.49** |

This quantifies the run-to-run spread the reviewer flagged: absolute scores swing by roughly ±5-6 points across seeds for the *same* model/task/mode — comparable in magnitude to some skill-vs-baseline gaps reported in the paper. For transparency: 5 of 72 task-mode cells (7%) across these reruns hit transient infra errors (agent-registration races on the shared gateway); we kept them as 0-score cells rather than dropping them, so std is a conservative (upper-bound) variance estimate. Our Limitations paragraph already flags repeated seeds as future work; we now provide first empirical evidence rather than only the caveat.

**S1 (report skill-authoring failures, not only created-skill counts).** We agree. The two OpenClaw rows with 0 postskill skills created are exactly the two 89.1%/85.1% empty-response rows from W2 — "0 skills" there most likely reflects a degraded authoring pipeline (no valid artifact produced), not a deliberate "skill not needed" decision, which is precisely the distinction the reviewer asks for. In the camera-ready we will log an explicit `authoring_attempted_no_artifact` vs. `opted_out` status per task rather than inferring it post hoc.

**S2 (report absolute score changes, not only ratios).** Table 2 already reports absolute percentage scores; `R_p`/`R_q` ratios appear only as a supplementary Metrics-subsection definition. We will add a clarifying sentence there to avoid the impression that ratios are the primary reported quantity.

These additions directly address the causal-attribution and reproducibility concerns using new diagnostic evidence and reruns, while keeping the paper's mixed-result framing intact.
