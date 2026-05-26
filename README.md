# EvoClawBench Anonymous Review Artifact

This branch is a minimal double-anonymous review artifact for EvoClawBench. It contains the benchmark package, synthetic fixtures, task definitions, graders, tests, the skill-creator bundle required by skill-authoring modes, and sanitized reported-result exports.

The repository intentionally excludes unrelated monorepo projects, local editor state, raw execution logs, TeX source history, trajectory dumps, crawler dumps, and local runtime workspaces.

## Contents

- `evoclawbench/tasks/`: 101 loader tasks, including `task_00_sanity`; the paper reports the 100 non-sanity official tasks.
- `evoclawbench/assets/`: synthetic benchmark fixtures used by the tasks.
- `evoclawbench/scripts/`: benchmark runner, runtime adapters, grading, metrics, analysis, and plotting scripts.
- `evoclawbench/tests/`: unit and integration-style tests for local benchmark logic.
- `skills/skill-creator/`: skill-authoring bundle required by `preskill` and `postskill`.
- `evoclawbench/results/reported/`: sanitized JSON and summary files for the paper's reported rows and subset audits.

All names, emails, and company-like records inside benchmark fixtures are synthetic examples for controlled tasks.

## Install

```bash
cd evoclawbench
uv sync --extra dev
```

## Test

```bash
uv run pytest tests/ -v
uv run ruff check scripts/ tests/
```

## Run

The benchmark can run against external OpenClaw or nanobot runtime executables. Configure any model credentials through the runtime environment; no credentials are stored in this artifact.

```bash
uv run scripts/benchmark.py --runtime nanobot --model openai/gpt-5.4-mini --mode all --suite task_01_batch_data_transform
uv run scripts/benchmark.py --runtime openclaw --model openai/gpt-5.4-mini --mode all --suite task_01_batch_data_transform
```

The reported paper rows used local subprocess execution with `--mode all --workers 32 --environment local`. Because external model APIs and runtimes are not bundled, exact reruns require equivalent runtime installation and model access.

## Reported Results

The sanitized result exports preserve aggregate metadata, metrics, per-task grades, per-task usage, status counts, timeout flags, and skill mutation flags. Raw transcripts, stdout/stderr, local workspace paths, and detailed generated-skill contents are removed.

Table 2 source rows are stored as neutral `table2_row_*.json` files. Each JSON keeps
the original source filename in its `source_file` field for provenance.

- `table2_row_01.json`: original source `0061_openai-gpt-5-4_openclaw.json`
- `table2_row_02.json`: original source `0062_openai-qwen3-6-plus_openclaw.json`
- `table2_row_03.json`: original source `0063_openai-deepseek-v4-pro_openclaw.json`
- `table2_row_04.json`: original source `0064_openai-minimax-minimax-m2-7_openclaw.json`
- `table2_row_05.json`: original source `0065_openai-gpt-5-4-mini_openclaw.json`
- `table2_row_06.json`: original source `0079_openai-gpt-5-4_nanobot.json`
- `table2_row_07.json`: original source `0075_openai-qwen3-6-plus_nanobot.json`
- `table2_row_08.json`: original source `0076_openai-deepseek-v4-pro_nanobot.json`
- `table2_row_09.json`: original source `0080_openai-minimax-minimax-m2-7_nanobot.json`
- `table2_row_10.json`: original source `0081_openai-gpt-5-4-mini_nanobot.json`

Recompute the displayed table from sanitized JSON:

```bash
cd evoclawbench/results/reported
python print_table2.py
```

Subset audit summaries copied from the paper-subset experiment outputs are in
`evoclawbench/results/reported/subset_audits/`.

## Anonymous Review Notes

Use Anonymous GitHub's term-replacement settings as a final guardrail for any private author identifiers, local path fragments, email addresses, and paper-authoring service identifiers known to the submitters. These terms are intentionally not listed in this artifact.
