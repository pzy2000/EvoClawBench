We thank the reviewer for the concrete suggestions.

**W1 (single run).** Agreed: Table 2 is descriptive and lacks full-suite CIs. Three 12-task executions show 5--6-point SDs, but Runs 2/3 changed execution settings and 5/72 cells had infrastructure errors. This measures operational sensitivity, not seed variance.

**W2 (100 tasks / 12 hybrid).** The 502 sub-problems improve grading resolution but are nested within 100 task-level units. Eighty-eight tasks are deterministic; regrading the 36 outputs from 12 hybrid tasks gives \(r=0.997\), with 35/36 differences below 0.05. This tests judge sensitivity only.

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

**C1.** Review-mode line numbers caused the overlap; we will adjust affected layout. They disappear in final mode.

**C2.** We will regenerate Figures 1/2 with fewer, larger labels.

**C3.** Appendix-only `\onecolumn` keeps wide longtables legible; we will ensure format compliance.
