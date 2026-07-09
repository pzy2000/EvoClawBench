We thank the reviewer for the careful reading and for flagging concrete, actionable issues.

**W1 (single run, no CI).** This is a known limitation we already state in Limitations ("Experimental coverage"): one run per task/mode, with repeated seeds and confidence intervals left as future work. We prefer to keep this as an explicit limitation rather than paper over it with a small, non-representative multi-seed subset.

**W2 (100 tasks / 12-task hybrid subset).** 88 of the 100 official tasks are graded with fully deterministic automated checks over 502 sub-problems, so the effective statistical base is larger than "100" suggests; only 12 tasks use hybrid (automated + LLM-judge) grading. We already stress-tested exactly this 12-task hybrid subset against an alternate judge (36 task-mode pairs; Pearson $r=0.997$, 35/36 pairs within 0.05 absolute score), reported in the current manuscript.

**W3 (Table 2 boldface).** Agreed — done. We now bold the best-of-three-mode score in every row so the baseline/preskill/postskill contrast is visible at a glance.

**W4 (Section 3.4 code-style phrasing).** Agreed — done. The literal CLI invocation strings are moved to the appendix; Section 3.4 is now prose with a pointer to the appendix for exact syntax.

**W5 (OpenClaw vs. nanobot gap).** We investigated this and traced the anomalously low OpenClaw scores to transient instability on the upstream API provider/gateway side during the original `GPT-5.4 mini` runs, rather than to any inherent runtime-capability gap. A number of OpenClaw requests during that run window failed at the provider/gateway layer, which is consistent with the reported ~19% OpenClaw scores in Table 2 being dominated by dropped/failed calls rather than genuine task failures.

To resolve this, we re-ran a systematic 8-task subset (every 10th hardened task: `task_22/32/42/52/62/72/82/92`) on `GPT-5.4 mini` under OpenClaw once the provider/gateway was stable, and obtained the corrected results below:

| Mode | Original run (unstable gateway) | Re-run (stable gateway) | nanobot (unaffected) |
|---|---|---|---|
| Baseline | 0.00% (8/8 failed) | 82.81% | 92.50% |
| Preskill | 0.00% (8/8 failed) | 99.69% | 90.00% |
| Postskill | 0.00% (8/8 failed) | 79.69% | 92.50% |

After re-running under a stable gateway, OpenClaw and nanobot land in the same range (gap shrinks from ~90–100 points to ~5–13 points). We will re-run the full 100-task OpenClaw suite under a stable gateway for the camera-ready and update Table 2, Findings 1/2/4, and the abstract accordingly. We expect the qualitative conclusion (skill effects are selective and non-monotonic, not that one runtime is categorically far weaker) to survive, but the magnitude of the runtime contrast will shrink substantially. We are grateful this question led us to catch this.

**C1 (line numbers overlapping text).** This is the ACL/ARR review-mode `lineno` package (`acl.sty`'s `review` option), required for anonymous review; it disappears under the `final` option in camera-ready. Happy to adjust specific float placements if the reviewer can point to the worst pages.

**C2 (Figure 1/2 resolution).** We will regenerate both figures at higher resolution with fewer/larger labels for the revision.

**C3 (appendix single column).** Intentional: the appendix contains several wide longtables (task inventory, grading criteria) that do not fit ACL's two-column width, so we switch to `\onecolumn` only for the appendix — a common convention for appendix-only wide tables.
