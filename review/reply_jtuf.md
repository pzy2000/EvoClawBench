We thank the reviewer for the constructive summary and concrete suggestions. We address each point below.

**W1 (skill content vs. wrapper/workspace/scaffold).** Agreed. The four-task ablation (`task_02/07/15/21`) gives +4.05 points for normal \preskill{} reuse, +19.84 for an empty scaffold, and +1.52 for an irrelevant skill. For \postskill{}, normal reuse is +1.47, while discarding the summarized skill gives −4.23. As a single-run diagnostic, this does not estimate skill content's causal contribution; it shows wrapper/context-reset confounding can exceed the observed normal-skill change.

**W2a (task-specific patching).** Correct. PostSkill summarizes grading/output evidence and reruns the same fixtures; it measures within-task repair, not held-out transfer, and may encode a task patch. We will restrict "reusable" to fresh same-task execution and state that a train/eval split is required for generalization.

**W2b (zero-skill collapse).** A targeted, read-only transcript analysis addresses the separate workflow-collapse question. For two collapsed OpenClaw rows (`GPT-5.4`: 18.63%→1.14%; `DeepSeek-V4-Pro`: 19.99%→0.00%) and two comparison rows (`GPT-5.4 mini`: 19.36%; `Qwen3.6-Plus`: 19.12%), we applied the same measure to PostSkill second-execution transcripts:
- Collapsed rows: in 90/101 (89.1%) GPT-5.4 and 86/101 (85.1%) DeepSeek-V4-Pro task results, the transcript contains at least one assistant message and **every recorded assistant message has empty content**.
- Comparison rows: 0/101 (GPT-5.4 mini) and 1/101 (Qwen3.6-Plus) by the same measure.
- Independently, nanobot's DeepSeek-V4-Pro preskill collapse (77.77%→4.80%) corresponds to 89/101 tasks hitting nanobot's own degenerate-response fallback string.

This identifies an associated failure signature, not whether its cause is provider/gateway, adapter, concurrency, or prompt/runtime interaction; nor does it answer W2a. We will mark these rows execution-contaminated and not use them for skill-quality or inherent-runtime claims. The mixed-effect conclusion will rely only on valid rows and controls.

**W3 (limited coverage).** We added two `GPT-5.4 mini`/OpenClaw executions on the same 12 hybrid tasks. Run 1 is the submitted `0001_openai-gpt-5-4-mini_openclaw.json`; Runs 2/3 are local `seed2`/`seed3` `0001_venus-gpt-5-4-mini_openclaw.json` runs. They changed route, endpoint, judge, timeout, and transcript fallback, so they are operational repetitions, not controlled seeds:

| Run | Baseline | PreSkill | PostSkill |
|---|---:|---:|---:|
| 1 (submission) | 80.96% | 79.77% | 79.21% |
| 2 (rerun) | 77.05% | 69.61% | 68.54% |
| 3 (rerun) | 70.09% | 80.75% | 76.11% |
| **mean ± std** | **76.03 ± 5.51** | **76.71 ± 6.17** | **74.62 ± 5.49** |

The 5--6-point SDs are comparable to some mode gaps, but mix configuration variation and stochasticity; 5/72 rerun cells had agent-registration errors retained as zeros. The JSONs are local but not yet in the anonymous artifact, so they will not become paper evidence until exported with provenance. These are neither seed-variance estimates nor CIs; matched full-suite repeats remain necessary.

**S1 (authoring failures).** Agreed. Current logs cannot distinguish an invalid/missing artifact from explicit opt-out; reuse failures do not establish the authoring outcome. We will add `authoring_attempted_no_artifact` and `opted_out` statuses and mark current zeros ambiguous.

**S2 (absolute changes).** We will add PreSkill/PostSkill percentage-point deltas from Baseline and keep \(R_p,R_q\) secondary.

The revision will separate same-task repair, workflow failure, and skill effects, and report rerun limits explicitly.
