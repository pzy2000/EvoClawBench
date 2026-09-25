# Split re-analysis of the main-table result files

## Scores, official split

| Runtime | Model | n | Baseline | PreSkill (Δpp, 95% CI) | PostSkill (Δpp, 95% CI) | PostSkill first pass (Δpp vs Baseline) | Skills P/Q |
|---|---|---:|---:|---|---|---|---|
| OpenClaw | GPT-5.4 | 100 | 17.82 | 17.25 (-0.57, [-1.61, +0.19]) | 1.15 (-16.67, [-23.69, -10.09]) | 0.72 (-17.10, [-24.38, -10.16]) | 21/0 |
| OpenClaw | Qwen3.6-Plus | 100 | 18.35 | 16.55 (-1.79, [-4.55, +0.27]) | 18.32 (-0.03, [-0.72, +0.84]) | 18.97 (+0.63, [-0.82, +2.59]) | 21/21 |
| OpenClaw | DeepSeek-V4-Pro | 100 | 19.18 | 14.21 (-4.97, [-9.23, -1.55]) | 0.00 (-19.18, [-26.80, -11.89]) | 0.00 (-19.18, [-26.81, -11.95]) | 21/0 |
| OpenClaw | MiniMax-M2.7 | 100 | 18.07 | 17.17 (-0.90, [-3.07, +0.35]) | 18.29 (+0.23, [-0.17, +0.82]) | 17.05 (-1.01, [-3.16, +0.20]) | 26/20 |
| OpenClaw | GPT-5.4 mini | 100 | 18.30 | 18.62 (+0.31, [-0.03, +0.75]) | 18.56 (+0.26, [-0.26, +0.84]) | 18.29 (-0.02, [-0.61, +0.54]) | 21/20 |
| nanobot | GPT-5.4 | 100 | 96.09 | 96.70 (+0.60, [-0.31, +1.99]) | 96.13 (+0.03, [-2.15, +2.18]) | 95.68 (-0.42, [-1.97, +1.27]) | 100/100 |
| nanobot | Qwen3.6-Plus | 100 | 56.01 | 59.50 (+3.49, [-9.00, +15.77]) | 53.88 (-2.14, [-15.56, +11.22]) | 54.88 (-1.13, [-10.66, +8.06]) | 69/38 |
| nanobot | DeepSeek-V4-Pro | 100 | 77.55 | 3.84 (-73.70, [-81.94, -65.24]) | 0.00 (-77.55, [-85.29, -69.38]) | 0.00 (-77.55, [-85.40, -69.38]) | 27/0 |
| nanobot | MiniMax-M2.7 | 100 | 90.88 | 92.83 (+1.95, [-4.05, +7.97]) | 94.44 (+3.66, [-1.93, +9.62]) | 93.88 (+3.10, [-2.85, +9.13]) | 98/99 |
| nanobot | GPT-5.4 mini | 100 | 88.59 | 87.29 (-1.31, [-5.55, +3.05]) | 89.67 (+1.07, [-2.80, +5.00]) | 85.31 (-3.28, [-8.21, +1.33]) | 99/81 |

## Scores, seed split

| Runtime | Model | n | Baseline | PreSkill (Δpp, 95% CI) | PostSkill (Δpp, 95% CI) | PostSkill first pass (Δpp vs Baseline) | Skills P/Q |
|---|---|---:|---:|---|---|---|---|
| OpenClaw | GPT-5.4 | 21 | 84.85 | 82.16 (-2.70, [-7.42, +0.96]) | 5.50 (-79.36, [-91.39, -65.31]) | 3.44 (-81.42, [-93.58, -66.81]) | 21/0 |
| OpenClaw | Qwen3.6-Plus | 21 | 87.37 | 78.83 (-8.54, [-20.91, +1.26]) | 87.22 (-0.15, [-3.33, +3.96]) | 90.34 (+2.98, [-3.90, +11.92]) | 21/21 |
| OpenClaw | DeepSeek-V4-Pro | 21 | 91.36 | 67.68 (-23.68, [-40.26, -8.76]) | 0.00 (-91.36, [-97.86, -83.24]) | 0.00 (-91.36, [-97.86, -83.10]) | 21/0 |
| OpenClaw | MiniMax-M2.7 | 21 | 86.04 | 81.74 (-4.30, [-14.61, +1.79]) | 87.11 (+1.08, [-0.81, +3.78]) | 81.21 (-4.83, [-14.79, +0.95]) | 26/20 |
| OpenClaw | GPT-5.4 mini | 21 | 87.16 | 88.65 (+1.49, [-0.17, +3.40]) | 88.37 (+1.21, [-1.23, +4.00]) | 87.08 (-0.08, [-2.95, +2.56]) | 21/20 |
| nanobot | GPT-5.4 | 21 | 84.85 | 84.28 (-0.57, [-2.53, +1.15]) | 87.75 (+2.89, [-0.67, +7.99]) | 84.77 (-0.08, [-2.01, +2.02]) | 21/21 |
| nanobot | Qwen3.6-Plus | 21 | 81.02 | 69.05 (-11.97, [-24.99, -1.09]) | 61.31 (-19.71, [-37.35, -4.26]) | 85.15 (+4.13, [-0.23, +11.90]) | 19/16 |
| nanobot | DeepSeek-V4-Pro | 21 | 84.74 | 13.54 (-71.20, [-87.71, -53.65]) | 0.00 (-84.74, [-95.85, -70.73]) | 0.00 (-84.74, [-95.95, -70.85]) | 16/0 |
| nanobot | MiniMax-M2.7 | 21 | 80.96 | 76.80 (-4.16, [-19.99, +11.10]) | 86.53 (+5.57, [-3.28, +18.06]) | 80.92 (-0.04, [-14.13, +14.24]) | 22/21 |
| nanobot | GPT-5.4 mini | 21 | 84.38 | 83.39 (-0.99, [-6.03, +6.07]) | 86.62 (+2.24, [-2.14, +8.82]) | 83.87 (-0.51, [-8.37, +7.66]) | 21/20 |

## Scores, generated split

| Runtime | Model | n | Baseline | PreSkill (Δpp, 95% CI) | PostSkill (Δpp, 95% CI) | PostSkill first pass (Δpp vs Baseline) | Skills P/Q |
|---|---|---:|---:|---|---|---|---|
| OpenClaw | GPT-5.4 | 79 | 0.00 | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0/0 |
| OpenClaw | Qwen3.6-Plus | 79 | 0.00 | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0/0 |
| OpenClaw | DeepSeek-V4-Pro | 79 | 0.00 | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0/0 |
| OpenClaw | MiniMax-M2.7 | 79 | 0.00 | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0/0 |
| OpenClaw | GPT-5.4 mini | 79 | 0.00 | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0.00 (+0.00, [+0.00, +0.00]) | 0/0 |
| nanobot | GPT-5.4 | 79 | 99.08 | 100.00 (+0.92, [+0.06, +2.53]) | 98.35 (-0.73, [-3.26, +1.65]) | 98.58 (-0.51, [-2.41, +1.58]) | 79/79 |
| nanobot | Qwen3.6-Plus | 79 | 49.37 | 56.96 (+7.59, [-7.59, +22.78]) | 51.90 (+2.53, [-13.92, +18.99]) | 46.84 (-2.53, [-13.92, +8.86]) | 50/22 |
| nanobot | DeepSeek-V4-Pro | 79 | 75.63 | 1.27 (-74.37, [-83.39, -65.03]) | 0.00 (-75.63, [-84.65, -65.66]) | 0.00 (-75.63, [-84.49, -65.82]) | 11/0 |
| nanobot | MiniMax-M2.7 | 79 | 93.51 | 97.09 (+3.58, [-2.69, +10.28]) | 96.57 (+3.14, [-3.49, +10.26]) | 97.37 (+3.94, [-2.56, +10.51]) | 76/78 |
| nanobot | GPT-5.4 mini | 79 | 89.72 | 88.32 (-1.39, [-6.55, +3.73]) | 90.47 (+0.76, [-3.86, +5.41]) | 85.69 (-4.02, [-9.78, +1.49]) | 78/61 |

## Final-phase execution status, official split

| Runtime | Model | Mode | Status | Fully-empty assistant transcripts | Fallback hits |
|---|---|---|---|---:|---:|
| OpenClaw | GPT-5.4 | baseline | {'success': 21, 'timeout': 79} | 0 | 0 |
| OpenClaw | GPT-5.4 | preskill | {'timeout': 18, 'success': 82} | 62 | 0 |
| OpenClaw | GPT-5.4 | postskill | {'success': 86, 'timeout': 14} | 89 | 0 |
| OpenClaw | Qwen3.6-Plus | baseline | {'timeout': 79, 'success': 21} | 0 | 0 |
| OpenClaw | Qwen3.6-Plus | preskill | {'timeout': 76, 'success': 24} | 4 | 0 |
| OpenClaw | Qwen3.6-Plus | postskill | {'timeout': 78, 'success': 22} | 1 | 0 |
| OpenClaw | DeepSeek-V4-Pro | baseline | {'success': 22, 'timeout': 78} | 1 | 0 |
| OpenClaw | DeepSeek-V4-Pro | preskill | {'timeout': 34, 'success': 66} | 48 | 0 |
| OpenClaw | DeepSeek-V4-Pro | postskill | {'success': 83, 'timeout': 17} | 85 | 0 |
| OpenClaw | MiniMax-M2.7 | baseline | {'success': 21, 'timeout': 79} | 0 | 0 |
| OpenClaw | MiniMax-M2.7 | preskill | {'timeout': 79, 'success': 21} | 0 | 0 |
| OpenClaw | MiniMax-M2.7 | postskill | {'success': 21, 'timeout': 79} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | baseline | {'success': 21, 'timeout': 79} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | preskill | {'success': 21, 'timeout': 79} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | postskill | {'timeout': 79, 'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 | baseline | {'success': 100} | 0 | 0 |
| nanobot | GPT-5.4 | preskill | {'success': 100} | 0 | 0 |
| nanobot | GPT-5.4 | postskill | {'success': 100} | 0 | 0 |
| nanobot | Qwen3.6-Plus | baseline | {'success': 100} | 0 | 34 |
| nanobot | Qwen3.6-Plus | preskill | {'success': 100} | 0 | 25 |
| nanobot | Qwen3.6-Plus | postskill | {'success': 100} | 0 | 32 |
| nanobot | DeepSeek-V4-Pro | baseline | {'success': 100} | 0 | 8 |
| nanobot | DeepSeek-V4-Pro | preskill | {'success': 100} | 0 | 89 |
| nanobot | DeepSeek-V4-Pro | postskill | {'success': 100} | 0 | 20 |
| nanobot | MiniMax-M2.7 | baseline | {'success': 97, 'timeout': 3} | 0 | 0 |
| nanobot | MiniMax-M2.7 | preskill | {'success': 100} | 0 | 1 |
| nanobot | MiniMax-M2.7 | postskill | {'success': 99} | 0 | 0 |
| nanobot | GPT-5.4 mini | baseline | {'success': 100} | 0 | 0 |
| nanobot | GPT-5.4 mini | preskill | {'success': 100} | 0 | 0 |
| nanobot | GPT-5.4 mini | postskill | {'success': 100} | 0 | 0 |

## Final-phase execution status, seed split

| Runtime | Model | Mode | Status | Fully-empty assistant transcripts | Fallback hits |
|---|---|---|---|---:|---:|
| OpenClaw | GPT-5.4 | baseline | {'success': 21} | 0 | 0 |
| OpenClaw | GPT-5.4 | preskill | {'success': 21} | 0 | 0 |
| OpenClaw | GPT-5.4 | postskill | {'success': 21} | 21 | 0 |
| OpenClaw | Qwen3.6-Plus | baseline | {'success': 21} | 0 | 0 |
| OpenClaw | Qwen3.6-Plus | preskill | {'success': 21} | 1 | 0 |
| OpenClaw | Qwen3.6-Plus | postskill | {'success': 21} | 0 | 0 |
| OpenClaw | DeepSeek-V4-Pro | baseline | {'success': 21} | 0 | 0 |
| OpenClaw | DeepSeek-V4-Pro | preskill | {'success': 21} | 0 | 0 |
| OpenClaw | DeepSeek-V4-Pro | postskill | {'success': 21} | 21 | 0 |
| OpenClaw | MiniMax-M2.7 | baseline | {'success': 21} | 0 | 0 |
| OpenClaw | MiniMax-M2.7 | preskill | {'success': 21} | 0 | 0 |
| OpenClaw | MiniMax-M2.7 | postskill | {'success': 21} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | baseline | {'success': 21} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | preskill | {'success': 21} | 0 | 0 |
| OpenClaw | GPT-5.4 mini | postskill | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 | baseline | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 | preskill | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 | postskill | {'success': 21} | 0 | 0 |
| nanobot | Qwen3.6-Plus | baseline | {'success': 21} | 0 | 0 |
| nanobot | Qwen3.6-Plus | preskill | {'success': 21} | 0 | 2 |
| nanobot | Qwen3.6-Plus | postskill | {'success': 21} | 0 | 5 |
| nanobot | DeepSeek-V4-Pro | baseline | {'success': 21} | 0 | 0 |
| nanobot | DeepSeek-V4-Pro | preskill | {'success': 21} | 0 | 11 |
| nanobot | DeepSeek-V4-Pro | postskill | {'success': 21} | 0 | 9 |
| nanobot | MiniMax-M2.7 | baseline | {'success': 21} | 0 | 0 |
| nanobot | MiniMax-M2.7 | preskill | {'success': 21} | 0 | 1 |
| nanobot | MiniMax-M2.7 | postskill | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 mini | baseline | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 mini | preskill | {'success': 21} | 0 | 0 |
| nanobot | GPT-5.4 mini | postskill | {'success': 21} | 0 | 0 |

## Token-efficiency ratios vs. Baseline, seed split (Baseline tokens / candidate tokens)

| Runtime | Model | Pre exec-only | Pre end-to-end | Post second-only | Post reuse-only (summary+second) | Post end-to-end | Output share of Baseline tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| OpenClaw | GPT-5.4 | 0.77 | 0.36 | n/a | n/a | n/a | 0.021 |
| OpenClaw | Qwen3.6-Plus | 1.02 | 0.37 | 0.93 | 0.39 | 0.29 | 0.037 |
| OpenClaw | DeepSeek-V4-Pro | 1.00 | 0.41 | n/a | n/a | n/a | 0.043 |
| OpenClaw | MiniMax-M2.7 | 0.51 | 0.21 | 0.64 | 0.38 | 0.27 | 0.035 |
| OpenClaw | GPT-5.4 mini | 0.80 | 0.32 | 0.81 | 0.39 | 0.28 | 0.030 |
| nanobot | GPT-5.4 | n/a | n/a | n/a | n/a | n/a | n/a |
| nanobot | Qwen3.6-Plus | n/a | n/a | n/a | n/a | n/a | n/a |
| nanobot | DeepSeek-V4-Pro | n/a | n/a | n/a | n/a | n/a | n/a |
| nanobot | MiniMax-M2.7 | n/a | n/a | n/a | n/a | n/a | n/a |
| nanobot | GPT-5.4 mini | n/a | n/a | n/a | n/a | n/a | n/a |

## Phase token usage, seed split (millions of tokens: input / output / cache-read / total)

- OpenClaw GPT-5.4: baseline=2.44/0.103/2.26/4.80 (1.27h); preskill:skill_generation=3.90/0.111/3.11/7.12 (1.36h); preskill:execution=3.57/0.105/2.53/6.21 (1.90h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.88h); postskill:skill_summary=0.00/0.000/0.00/0.00 (1.68h); postskill:second_execution=0.00/0.000/0.00/0.00 (1.70h)
- OpenClaw Qwen3.6-Plus: baseline=4.90/0.190/0.00/5.09 (1.68h); preskill:skill_generation=8.55/0.244/0.00/8.79 (1.97h); preskill:execution=4.76/0.205/0.00/4.97 (2.09h); postskill:first_execution=4.24/0.171/0.00/4.41 (1.63h); postskill:skill_summary=7.28/0.133/0.00/7.41 (1.92h); postskill:second_execution=5.29/0.193/0.00/5.49 (2.22h)
- OpenClaw DeepSeek-V4-Pro: baseline=1.27/0.224/3.69/5.18 (1.76h); preskill:skill_generation=1.51/0.193/5.82/7.52 (1.69h); preskill:execution=1.25/0.241/3.69/5.18 (2.27h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.89h); postskill:skill_summary=0.00/0.000/0.00/0.00 (1.71h); postskill:second_execution=0.00/0.000/0.00/0.00 (1.72h)
- OpenClaw MiniMax-M2.7: baseline=0.58/0.139/3.20/3.92 (1.41h); preskill:skill_generation=1.03/0.148/9.52/10.70 (1.49h); preskill:execution=0.69/0.180/6.80/7.67 (2.10h); postskill:first_execution=0.60/0.122/3.33/4.05 (1.24h); postskill:skill_summary=0.76/0.067/3.47/4.30 (1.71h); postskill:second_execution=0.69/0.165/5.29/6.14 (2.40h)
- OpenClaw GPT-5.4 mini: baseline=2.04/0.106/1.33/3.48 (0.99h); preskill:skill_generation=3.98/0.170/2.44/6.59 (1.23h); preskill:execution=2.33/0.105/1.91/4.35 (1.71h); postskill:first_execution=2.02/0.104/1.12/3.25 (1.00h); postskill:skill_summary=3.00/0.076/1.63/4.70 (1.74h); postskill:second_execution=2.39/0.109/1.81/4.30 (1.80h)
- nanobot GPT-5.4: baseline=0.00/0.000/0.00/0.00 (0.45h); preskill:skill_generation=0.00/0.000/0.00/0.00 (0.40h); preskill:execution=0.00/0.000/0.00/0.00 (0.48h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.56h); postskill:skill_summary=0.00/0.000/0.00/0.00 (0.34h); postskill:second_execution=0.00/0.000/0.00/0.00 (0.49h)
- nanobot Qwen3.6-Plus: baseline=0.00/0.000/0.00/0.00 (0.81h); preskill:skill_generation=0.00/0.000/0.00/0.00 (1.14h); preskill:execution=0.00/0.000/0.00/0.00 (0.69h); postskill:first_execution=0.00/0.000/0.00/0.00 (1.03h); postskill:skill_summary=0.00/0.000/0.00/0.00 (0.55h); postskill:second_execution=0.00/0.000/0.00/0.00 (0.49h)
- nanobot DeepSeek-V4-Pro: baseline=0.00/0.000/0.00/0.00 (0.99h); preskill:skill_generation=0.00/0.000/0.00/0.00 (0.66h); preskill:execution=0.00/0.000/0.00/0.00 (0.29h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.07h); postskill:skill_summary=0.00/0.000/0.00/0.00 (0.08h); postskill:second_execution=0.00/0.000/0.00/0.00 (0.08h)
- nanobot MiniMax-M2.7: baseline=0.00/0.000/0.00/0.00 (0.66h); preskill:skill_generation=0.00/0.000/0.00/0.00 (0.92h); preskill:execution=0.00/0.000/0.00/0.00 (0.52h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.43h); postskill:skill_summary=0.00/0.000/0.00/0.00 (0.56h); postskill:second_execution=0.00/0.000/0.00/0.00 (0.52h)
- nanobot GPT-5.4 mini: baseline=0.00/0.000/0.00/0.00 (0.25h); preskill:skill_generation=0.00/0.000/0.00/0.00 (0.29h); preskill:execution=0.00/0.000/0.00/0.00 (0.25h); postskill:first_execution=0.00/0.000/0.00/0.00 (0.26h); postskill:skill_summary=0.00/0.000/0.00/0.00 (0.26h); postskill:second_execution=0.00/0.000/0.00/0.00 (0.30h)
