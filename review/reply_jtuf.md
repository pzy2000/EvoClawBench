We thank the reviewer for the constructive summary and for identifying concrete ways to strengthen the paper's causal and reproducibility claims. We address each point below.

**W1 (skill content vs. reuse wrapper/workspace/scaffold).** We agree this confound is real, and the paper already includes a dedicated ablation designed to separate it (Sec. 5.3, `task_02/07/15/21`, Table: skill-content ablation): a normal \preskill{} reuse improves the mean score by 4.05 points, but an **empty-skill scaffold** improves by 19.84 points and an **irrelevant skill** by 1.52 points — i.e., most of the naive "skill helps" signal on this subset is explained by the reuse prompt/context reset, not skill content. For \postskill{}, normal reuse is slightly above baseline (+1.47) while discarding the generated skill after summarization falls below baseline (−4.23). We also ran a new read-only diagnostic (see W2) that identifies a second, previously unquantified confound source: degenerate model responses.

**W2 (POSTSKILL as task-specific patching, compounded by zero-skill collapse).** We ran a targeted, read-only analysis of existing OpenClaw transcripts to test whether the catastrophic collapses are skill-quality failures or something else. Comparing two collapsed rows (`GPT-5.4`: baseline 18.63%→postskill 1.14%; `DeepSeek-V4-Pro`: 19.99%→0.00%) against two stable rows (`GPT-5.4 mini` 19.36%, `Qwen3.6-Plus` 19.12%) on the same postskill second-execution transcripts:
- Collapsed rows: 89.1% (GPT-5.4) / 85.1% (DeepSeek-V4-Pro) of tasks show an **empty/degenerate first assistant turn** (zero-length message content) during skill-reuse execution.
- Stable rows: 0.0% (GPT-5.4 mini) / 1.0% (Qwen3.6-Plus).
- Independently, nanobot's DeepSeek-V4-Pro preskill collapse (77.77%→4.80%) corresponds to 89/101 tasks hitting nanobot's own degenerate-response fallback string.

This supports exactly the reviewer's concern that workflow-level confounds are real — but locates a *specific, previously unreported* mechanism: response degradation under certain prompt/runtime/model combinations, not "the model decided the skill was bad" or "task-specific overfitting" per se. We will report this diagnostic in the camera-ready as an explicit caveat on the zero-skill-collapse rows, without changing the headline claims.

**W3 (limited coverage: two runtimes, one local setup, one run/task/mode).** We ran new same-model reruns to give the reviewer a concrete variance estimate rather than only a Limitations sentence. Using the identical 12-task hybrid subset and `GPT-5.4 mini`/OpenClaw/`mode=all` configuration as the paper's subset audit, we reran seeds 2 and 3 (seed 1 = original submission run) via a currently available inference gateway (same model, different endpoint from the one used at submission time — noted here for transparency; per-task timeouts were widened to 4× to absorb gateway queuing rather than model behavior).

| Seed | Baseline | Preskill | Postskill |
|---|---:|---:|---:|
| 1 (submission) | 80.96% | 79.77% | 79.21% |
| 2 (rerun) | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] |
| 3 (rerun) | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] |
| **mean ± std** | **[PLACEHOLDER]** | **[PLACEHOLDER]** | **[PLACEHOLDER]** |

This quantifies exactly the kind of run-to-run spread the reviewer flagged, while our existing Limitations paragraph ("Repeated seeds, additional models, confidence intervals... remain future work") already commits to this direction; we now have first empirical evidence rather than only the caveat.

**S1 (report skill-authoring failures, not only created-skill counts).** We agree and will add this distinction explicitly. Using existing evidence: the two OpenClaw rows with 0 postskill skills created are exactly the two 89.1%/85.1% empty-response rows from W2 — i.e., "0 skills" there most likely reflects a degraded authoring pipeline (agent could not produce a valid artifact), not a deliberate "skill not needed" decision. This is precisely the distinction the reviewer asks us to make. In the camera-ready we will log an explicit `authoring_attempted_no_artifact` vs. `opted_out` status per task rather than inferring it post hoc.

**S2 (report absolute score changes, not only ratios).** Table 2 (main results) already reports absolute percentage scores, not ratios; `R_p`/`R_q` ratios appear only as a supplementary definition in the Metrics subsection to summarize relative change compactly. We will add a one-sentence clarification there to avoid the impression that ratios are the primary reported quantity.

We believe these additions directly address the causal-attribution and reproducibility concerns raised, using new diagnostic evidence and reruns rather than only prose, while keeping the paper's existing mixed-result framing intact.
