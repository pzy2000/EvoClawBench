# Ablation Summary

| Variant | Tasks | Mean score | Delta vs baseline | Tokens | Cost USD | Time h | Requests | Skills |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 4 | 54.24 | 0.00 | 799838 | 0.235564 | 0.080 | 35 | 0 |
| empty_skill_reuse | 4 | 74.08 | 19.84 | 544073 | 0.196154 | 0.069 | 24 | 4 |
| irrelevant_skill_reuse | 4 | 55.76 | 1.52 | 923888 | 0.240624 | 0.082 | 38 | 4 |
| postskill_normal | 4 | 55.70 | 1.47 | 2787875 | 0.810186 | 0.249 | 108 | 4 |
| postskill_summary_no_skill | 4 | 50.01 | -4.23 | 2585218 | 0.743271 | 0.238 | 102 | 0 |
| preskill_normal | 4 | 58.28 | 4.05 | 2800092 | 0.658257 | 0.214 | 102 | 4 |
