We thank the reviewer for the careful reading and for flagging concrete, actionable issues.

**W1 (single run, no CI).** Agreed: Table 2 is descriptive and cannot provide full-suite CIs. Three executions of a 12-task `GPT-5.4 mini`/OpenClaw subset show SDs of about 5--6 points, but Runs 2/3 changed route, endpoint, judge, timeout, and transcript fallback, with 5/72 infrastructure-error cells. We therefore treat this only as operational sensitivity, not controlled seed variance or a substitute for full-suite repeats.

**W2 (100 tasks / 12 hybrid).** The suite has 100 task-level units with 502 nested sub-problems; these improve grading resolution but are not 502 independent observations. Eighty-eight tasks are deterministic and 12 hybrid. Regrading the fixed 36 hybrid outputs gives \(r=0.997\), with 35/36 pairs within 0.05. This tests judge sensitivity, not task-set generalizability or execution variance.

**W3 (Table 2 boldface).** Agreed — done. We now bold the best-of-three-mode score in every row so the baseline/preskill/postskill contrast is visible at a glance.

**W4 (Section 3.4 code-style phrasing).** Agreed — done. The literal CLI invocation strings are moved to the appendix; Section 3.4 is now prose with a pointer to the appendix for exact syntax.

**W5 (OpenClaw vs. nanobot).** We agree that Table 2 does not support an inherent-runtime interpretation. On the eight hardened tasks below, all original `GPT-5.4 mini` executions timed out; other rows also contain empty assistant content. These are execution-chain failures, but logs cannot isolate provider/gateway, adapter, concurrency, timeout, or prompt/runtime interaction.

We reran `task_22/32/42/52/62/72/82/92` diagnostically. Conditions changed, so these are not corrected full-suite scores:

| Mode | Submission export | Diagnostic OpenClaw rerun | Nanobot comparison |
|---|---|---|---|
| Baseline | 0.00% (8/8 timed out) | 82.81% | 92.50% |
| PreSkill | 0.00% (8/8 timed out) | 99.69% | 90.00% |
| PostSkill | 0.00% (8/8 timed out) | 79.69% | 92.50% |

The columns are slices of full-suite runs `0065`, temporary diagnostic run `0001_venus-gpt-5-4-mini_openclaw.json`, and full-suite run `0081`; they differ in runtime, route, endpoint, workers, timeout, and transcript handling. The diagnostic is not in the anonymous artifact and will not become paper evidence until exported with provenance.

The mode gaps are 9.69/9.69/12.81 points; OpenClaw is higher in PreSkill. Two baseline cases clarify the original zeros:
- `task_32`: run `0065` timed out after 277.6 s, produced none of the five required reports, and scored zero on all deterministic checks. The diagnostic completed with tool use, produced all reports, and passed every file/schema/field check (1.0).
- `task_92`: run `0065` timed out after 305.8 s with no reports. The diagnostic produced five valid reports but scored 0.5: only `forecast_delta` was correct; four semantic fields were wrong. Thus the grader distinguishes partial correctness rather than rewarding file creation alone.

These cases show execution failure, not ungradable tasks, but cannot explain all five rows or exclude every interaction. We withdraw the inherent OpenClaw--nanobot interpretation, caveat contaminated rows, and replace them only with matched full-suite reruns. The narrower mixed/non-monotonic skill conclusion will rely only on valid rows.

**C1.** Line numbers come from ACL review mode, but overlap is still a defect. We will adjust affected floats/lines; numbering disappears in final mode.

**C2.** We will regenerate Figures 1/2 at higher resolution with fewer/larger labels.

**C3.** Appendix-only `\onecolumn` keeps the wide task-inventory/grading longtables legible; we will ensure final-format compliance.
