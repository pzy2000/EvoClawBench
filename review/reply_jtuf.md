We thank the reviewer for the concrete suggestions.

**W1 (skill content vs. wrapper).** The four-task ablation gives +4.05 points for normal PreSkill, +19.84 for an empty scaffold, and +1.52 for an irrelevant skill. For PostSkill, normal reuse is +1.47; discarding the skill gives −4.23. Given the single-run, four-task sample, we read this as suggestive evidence that wrapper/reset effects can be large relative to skill content, rather than as a causal estimate of skill content's contribution; we will state this scope explicitly and treat a larger, controlled ablation as necessary future work for a stronger causal claim.

**W2a (task-specific patching).** Correct: PostSkill summarizes grading/output evidence and reruns the same fixtures. It measures same-task repair, not held-out transfer. We will narrow "reusable" accordingly; generalization requires a train/eval split.

**W2b (zero-skill collapse, as referenced in W3).** In PostSkill second executions, every recorded assistant message is empty for 90/101 GPT-5.4 and 86/101 DeepSeek-V4-Pro tasks, versus 0/101 and 1/101 in comparison rows. Nanobot DeepSeek-V4-Pro PreSkill hits its fallback in 89/101 tasks. A matched 20-task rerun of these three rows no longer shows that literal fallback string, but severe collapse still occurs (DeepSeek-V4-Pro PreSkill/Baseline 0.06--0.23, PostSkill/Baseline 0.19--0.24, 0 mutation violations, still 3/20 fully-empty transcripts with 0 skills created on OpenClaw PostSkill); GPT-5.4 instead collapsed on PreSkill this time, with mutation violations we had not previously flagged. So the collapse is not one deterministic mechanism — it recurs but the failing phase shifts across reruns/backends. These rows cannot be used to separate skill-content effects from workflow effects, exactly the isolation gap raised in W1.

**W3 (limited coverage).** We added two `GPT-5.4 mini`/OpenClaw executions on the same 12 hybrid tasks. Runs 2/3 changed route, endpoint, judge, timeout, and transcript handling, so they are operational repetitions, not controlled seeds:

| Run | Baseline | PreSkill | PostSkill |
|---|---:|---:|---:|
| 1 (submission) | 80.96% | 79.77% | 79.21% |
| 2 (rerun) | 77.05% | 69.61% | 68.54% |
| 3 (rerun) | 70.09% | 80.75% | 76.11% |
| **mean ± std** | **76.03 ± 5.51** | **76.71 ± 6.17** | **74.62 ± 5.49** |

The 5--6-point SDs mix configuration variation and stochasticity; 5/72 rerun cells had registration errors retained as zeros. These are neither seed-variance estimates nor CIs. We will add the local source JSONs to the anonymous artifact and retain matched full-suite repeats as necessary.

**S1 (authoring failures).** Current logs cannot distinguish failed authoring from opt-out. We will add explicit statuses and mark existing zero counts ambiguous.

**S2 (absolute changes).** We will add percentage-point deltas from Baseline and keep the ratio metrics \(R_p, R_q\) (PreSkill/Baseline, PostSkill/Baseline score ratios) secondary.
