We thank the reviewer for the concrete suggestions.

**W1 (single run).** Agreed: Table 2 is descriptive and lacks full-suite CIs. Three 12-task executions show 5--6-point SDs, but Runs 2/3 changed execution settings and 5/72 cells had infrastructure errors. This measures operational sensitivity, not seed variance.

**W2 (100 tasks / 12 hybrid).** We agree: 100 tasks, and especially 12 hybrid-graded tasks, is a real limit on the generalizability of any single-subset quantitative claim, and no amount of judge-agreement checking on that subset substitutes for a larger sample. We will state this explicitly as a limitation rather than let the 502 sub-problem count imply broader coverage than the task-level sample supports. Separately, and only to address whether the *hybrid grader itself* is reliable (a different question from sample size), we regraded the 36 outputs from the 12 hybrid tasks with a second judge: \(r=0.997\), mean \(|\Delta|=0.014\), 35/36 differences below 0.05. This shows the hybrid grader is not the source of noise in that subset; it does not address the small-\(N\) concern, which we will flag directly and treat as motivation for expanding the hybrid subset in future work.

**W3.** Done: Table 2 now bolds the best mode per row.

**W4.** Done: CLI strings moved to the appendix; Sec. 3.4 now uses prose.

**W5 (OpenClaw vs. nanobot).** Table 2 does not support an inherent-runtime interpretation. All original `GPT-5.4 mini` executions on the eight sampled tasks failed under unstable upstream API conditions; other rows also contain empty responses. Logs point to provider-side execution instability, not a single deterministic cause.

We reran `task_22/32/42/52/62/72/82/92` under changed conditions:

| Mode | Submission export | OpenClaw rerun | Nanobot comparison |
|---|---|---|---|
| Baseline | 0.00% | 82.81% | 92.50% |
| PreSkill | 0.00% | 99.69% | 90.00% |
| PostSkill | 0.00% | 79.69% | 92.50% |

The gaps are 9.69/9.69/12.81 points; OpenClaw is higher in PreSkill. Two cases explain the original zeros:
- `task_32`: run `0065` failed under upstream API instability with no reports and all-zero checks; the diagnostic produced all reports and scored 1.0.
- `task_92`: run `0065` failed under upstream API instability with no reports; the diagnostic produced valid reports but scored 0.5 because four semantic fields were wrong. The grader therefore distinguishes partial correctness.
 
We withdraw the inherent runtime-gap interpretation and will replace contaminated rows only with matched full-suite reruns.

To be clear about scope: `task_22/32/42/52/62/72/82/92` are a distinct sample of generated tasks, separate from the 12 hybrid-graded tasks discussed in W2, and the failure pattern found here is specific to the affected `GPT-5.4 mini`/OpenClaw cells (and the analogous `GPT-5.4`/`DeepSeek-V4-Pro` PostSkill rows discussed with Reviewer 23ii). It is not evidence that Table 2 as a whole is unreliable; we will audit and caveat only the affected rows rather than the full table.

**C1.** Review-mode line numbers caused the overlap; we will adjust affected layout. They disappear in final mode.

**C2.** We will regenerate Figures 1/2 with fewer, larger labels.

**C3.** Appendix-only `\onecolumn` keeps wide longtables legible; we will ensure format compliance.
