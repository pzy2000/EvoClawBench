# EvoClawBench EMNLP Subset Experiment TODO

Last updated: 2026-05-25 Asia/Shanghai.

## Scope

- Primary model/runtime: `openai/gpt-5.4-mini` on `openclaw`.
- Primary judge: `openai/MiniMax/MiniMax-M2.7`.
- Alternate judge: `openrouter/anthropic/claude-opus-4.5`; fallback is `openai/qwen3.6-plus` if unavailable.
- Hybrid subset: `task_02_log_analysis,task_06_code_review,task_07_doc_extraction,task_11_web_extraction,task_13_data_pipeline,task_14_email_processing,task_15_shell_automation,task_16_ci_pipeline,task_17_invoice_processing,task_18_dep_audit,task_19_meeting_notes,task_21_metrics_anomaly`.
- Ablation subset: `task_02_log_analysis,task_07_doc_extraction,task_15_shell_automation,task_21_metrics_anomaly`.

## Checklist

- [x] Instrumentation
  - [x] Serialize `judge_model` into new benchmark result JSON files.
  - [x] Fix future EvoClawBench nanobot usage capture from `sessions/*.jsonl` when provider usage is present in session messages.
  - [x] Add focused regression tests.
- [x] Analysis scripts
  - [x] Add `scripts/analyze_cost_and_amortization.py`.
  - [x] Add `scripts/run_ablation_subset.py`.
  - [x] Add `scripts/analyze_judge_robustness.py`.
  - [x] Add focused tests for the new analysis logic.
- [x] Experiment artifacts
  - [x] Main subset result JSON: `results/paper_subset_experiments/0001_openai-gpt-5-4-mini_openclaw.json`.
    - Command: `uv run scripts/benchmark.py --runtime openclaw --model openai/gpt-5.4-mini --judge openai/MiniMax/MiniMax-M2.7 --mode all --workers 8 --environment local --suite task_02_log_analysis,task_06_code_review,task_07_doc_extraction,task_11_web_extraction,task_13_data_pipeline,task_14_email_processing,task_15_shell_automation,task_16_ci_pipeline,task_17_invoice_processing,task_18_dep_audit,task_19_meeting_notes,task_21_metrics_anomaly --output-dir results/paper_subset_experiments --no-progress`.
    - Status: completed 2026-05-25 02:13 Asia/Shanghai.
    - Caveat: OpenClaw row has nonzero token accounting and serializes `judge_model`; trajectory file is empty because this run did not collect trajectory payloads.
  - [x] Cost/amortization summary JSON: `results/paper_subset_experiments/cost_amortization_summary.json`.
    - Status: generated from `0001_openai-gpt-5-4-mini_openclaw.json`.
    - Caveat: subset preskill/postskill scores are below baseline, and token/USD break-even is `never`; wall-clock break-even appears only after repeated reuse.
  - [x] Cost/amortization summary Markdown: `results/paper_subset_experiments/cost_amortization_summary.md`.
  - [x] Ablation summary JSON/Markdown: `results/paper_subset_experiments/ablation_summary.{json,md}`.
    - Status: generated from 4-task ablation subset.
    - Caveat: empty-skill scaffold outperformed normal/irrelevant skill on this small subset, so the paper must not attribute gains solely to learned skill content.
  - [x] Judge robustness summary JSON/Markdown: `results/paper_subset_experiments/judge_robustness_summary.{json,md}`.
    - Status: generated for 36 task-mode pairs from the 12 hybrid-task subset.
    - Caveat: requested `openrouter/anthropic/claude-opus-4.5` returned 401; run used fallback `openai/qwen3.6-plus`. The corrected regrade reuses serialized automated sub-scores and replaces only the LLM-judge component; agreement with MiniMax is high (Pearson 0.9970, MAD 0.0141).
  - [x] Additional judge robustness JSON/Markdown: `results/paper_subset_experiments/judge_robustness_gpt54mini_summary.{json,md}`.
    - Status: generated for the same 36 task-mode pairs using `openai/gpt-5.4-mini` with no fallback.
    - Caveat: agreement is lower than the qwen fallback but still broadly consistent (Pearson 0.9512, MAD 0.0609, 30/36 within 0.10).
- [x] Paper
  - [x] Add subset cost, amortization, ablation, and judge robustness discussion to `paper/main.tex`.
    - Status: added `Subset Cost, Amortization, and Robustness Checks` under Results with three tables and fallback-judge caveat.
  - [x] Compile `paper/main.pdf`.
    - Status: `cd paper && make` completed; `pdfinfo main.pdf` reports 29 pages.
    - Caveat: page count increased from the previous 28-page build because the Results section now includes the new subset subsection and tables.

## Caveats To Preserve

- Current full-suite nanobot result rows report zero token/cost usage and remain usage-unavailable unless rerun after the nanobot usage-capture fix.
- Current full-suite OpenClaw rows `0061` and `0063` report zero postskill token usage; treat those postskill token/cost efficiencies as unavailable.
- Full-suite JSONs created before the instrumentation change do not serialize `judge_model`; new subset JSONs must.
- The EvoClawBench nanobot loader can now read future `sessions/*.jsonl` usage fields, but old full-suite nanobot rows did not persist provider usage in those session files.
