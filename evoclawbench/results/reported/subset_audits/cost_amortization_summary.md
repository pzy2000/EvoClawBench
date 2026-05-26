# Cost and Amortization Summary

## openclaw / openai/gpt-5.4-mini

- Source JSON: `0001_openai-gpt-5-4-mini_openclaw.json`
- Judge model: `openai/MiniMax/MiniMax-M2.7`
- Tasks: 12

| Mode | Score | Delta | Tokens | Cost USD | Time h | Requests | Delta / 1M extra tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 80.96 | 0.00 | 1942737 | 1.261524 | 0.305 | 84 |  |
| preskill | 79.77 | -1.19 | 7069653 | 3.744890 | 0.689 | 270 | -0.2321 |
| postskill | 79.21 | -1.75 | 7714592 | 4.127618 | 0.833 | 306 | -0.3032 |

| Mode | Token break-even | Cost break-even | Time break-even |
|---|---:|---:|---:|
| preskill | unavailable/never | unavailable/never | 14 |
| postskill | unavailable/never | unavailable/never | 9 |
