# Judge Robustness Summary

- Source JSON: `0001_openai-gpt-5-4-mini_openclaw.json`
- Original judge: `openai/MiniMax/MiniMax-M2.7`
- Alternate judge requested: `openrouter/anthropic/claude-opus-4.5`
- Fallback judge: `openai/qwen3.6-plus`
- Judge models used: `openai/qwen3.6-plus`
- Pairs: 36
- Pearson correlation: 0.997
- Mean absolute delta: 0.0141
- Within 0.05: 35
- Within 0.10: 36

| Task | Mode | Original | Alternate | Delta | Judge used |
|---|---|---:|---:|---:|---|
| task_18_dep_audit | preskill | 0.7920 | 0.8800 | 0.0880 | `openai/qwen3.6-plus` |
| task_07_doc_extraction | preskill | 0.7050 | 0.7500 | 0.0450 | `openai/qwen3.6-plus` |
| task_18_dep_audit | postskill | 0.8176 | 0.8560 | 0.0384 | `openai/qwen3.6-plus` |
| task_15_shell_automation | postskill | 0.1100 | 0.1400 | 0.0300 | `openai/qwen3.6-plus` |
| task_19_meeting_notes | preskill | 1.0000 | 0.9720 | -0.0280 | `openai/qwen3.6-plus` |
