# Judge Robustness Summary

- Source JSON: `0001_openai-gpt-5-4-mini_openclaw.json`
- Original judge: `openai/MiniMax/MiniMax-M2.7`
- Alternate judge requested: `openai/gpt-5.4-mini`
- Fallback judge: `none`
- Judge models used: `openai/gpt-5.4-mini`
- Pairs: 36
- Pearson correlation: 0.9512
- Mean absolute delta: 0.0609
- Within 0.05: 24
- Within 0.10: 30

| Task | Mode | Original | Alternate | Delta | Judge used |
|---|---|---:|---:|---:|---|
| task_11_web_extraction | baseline | 0.9972 | 0.6000 | -0.3972 | `openai/gpt-5.4-mini` |
| task_11_web_extraction | preskill | 0.9800 | 0.6800 | -0.3000 | `openai/gpt-5.4-mini` |
| task_18_dep_audit | baseline | 0.8800 | 0.7216 | -0.1584 | `openai/gpt-5.4-mini` |
| task_21_metrics_anomaly | preskill | 1.0000 | 0.8500 | -0.1500 | `openai/gpt-5.4-mini` |
| task_15_shell_automation | baseline | 0.1900 | 0.0840 | -0.1060 | `openai/gpt-5.4-mini` |
