# EvoClawBench

**Benchmark for evaluating general agent task performance with and without reusable skills.**

EvoClawBench runs the same task suite through OpenClaw or nanobot and compares three
execution strategies:

- **baseline**: complete the task directly; skill creation and skill edits are forbidden.
- **preskill**: generate task-specific skills first, then execute the task in a fresh workspace
  using those skills; execution must not modify skills.
- **postskill**: execute once without skills, summarize reusable skills from that first run, then
  execute the same task again in a fresh workspace using those skills.

The default `--mode all` runs all three strategies and reports execution-only and end-to-end
performance.

## Decision Log

These are the v1 benchmark decisions selected during design review. They are intentionally placed
near the top because they define how results should be interpreted.

| Question | Selected answer | Impact |
|----------|-----------------|--------|
| What replaces the old `baseline/evolution/bench/both` semantics? | Direct replacement with `baseline`, `preskill`, `postskill`, and `all`; no legacy CLI mode compatibility. | New result JSON uses `baseline_results`, `preskill_results`, `postskill_results`, and `metrics`. |
| What is the default CLI mode? | `--mode all`. | A default run compares all three strategies in order: baseline -> preskill -> postskill. |
| Who creates or summarizes skills? | The same runtime and model being benchmarked. | Skill generation is part of agent performance, not an external judge/summarizer step. |
| What does `postskill` rerun in v1? | The same task with the same fixtures. | No similar-task variants are introduced in v1. |
| What counts as performance? | Task score, token usage, cost, and elapsed time. | Metrics are reported for both execution-only and end-to-end scopes. |
| Can baseline or execution phases edit skills? | No. Baseline and skill reuse execution phases must not create, edit, or delete skills. | Skill files are hashed before and after execution; mutations set `skill_mutation_violation=true`. |
| How does `postskill` learn from the first run? | The first workspace receives `.evoclawbench/first_run_context.json` with task, grading, output, and transcript summaries. | The summary phase uses first-run evidence without rerunning the task. |
| How much should tasks and graders change? | Keep existing tasks, assets, and grading behavior unless required by orchestration. | The benchmark change is focused on orchestration, prompts, skill flow, result shape, metrics, and docs. |

## Quick Start

```bash
cd evoclawbench
uv sync --extra dev

# Run the full three-way benchmark
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot

# Run a subset on OpenClaw
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime openclaw \
  --suite task_01_batch_data_transform,task_02_log_analysis

# Run one mode only
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode preskill

# Multiple runs per task
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --runs 3
```

## Modes

| Mode | Phases | Skill behavior |
|------|--------|----------------|
| `baseline` | execute -> grade | No skill creation or mutation |
| `preskill` | skill generation -> execute -> grade | Generation seeds `skills/skill-creator`; execution loads generated skills only |
| `postskill` | first execute -> grade -> skill summary -> second execute -> grade | Summary uses `.evoclawbench/first_run_context.json`; second execution loads summarized skills |
| `all` | baseline + preskill + postskill | Default full comparison |

Skill authoring phases are performed by the same runtime and model being benchmarked. Reuse
execution phases hash skill files before and after execution; if skills are added, removed, or
edited during execution, the result is marked with `skill_mutation_violation=true`.

## Supported Runtimes

| Runtime | CLI |
|---------|-----|
| **OpenClaw** | `openclaw agent --message` |
| **nanobot** | `nanobot run --message` |

Both runtimes use the `SKILL.md` format. Skill authoring requires the monorepo
`skills/skill-creator/` directory next to `evoclawbench/`.

## Metrics

The output JSON contains:

- `baseline_results`
- `preskill_results`
- `postskill_results`
- `metrics`

`metrics.execution_only` compares only the task execution phase:

- baseline execution
- preskill execution after skill generation
- postskill second execution after summary

`metrics.end_to_end` includes total cost of the full workflow:

- baseline single execution
- preskill skill generation + execution
- postskill first execution + skill summary + second execution

Both scopes report mean score, token/cost/time usage, and efficiency versus baseline. Postskill
also reports first-pass score, second-pass score, and second-vs-first improvement. Created-skill
counts and heuristic skill quality are reported separately for preskill and postskill.

## Tasks

Tasks live in `tasks/task_*.md`. Each task defines a prompt, workspace assets, grading criteria,
and usually 5-10 structurally similar sub-problems. Current categories include data transforms,
log analysis, API scaffolding, test generation, config migration, security review, document
extraction, Excel/report generation, web extraction, email/invoice/meeting-note processing,
shell automation, CI generation, environment config, and metrics anomaly detection.

## Results

Results are written to `results/` by default:

```json
{
  "benchmark": "evoclawbench",
  "model": "anthropic/claude-sonnet-4",
  "runtime": "nanobot",
  "mode": "all",
  "baseline_results": {},
  "preskill_results": {},
  "postskill_results": {},
  "metrics": {
    "execution_only": {},
    "end_to_end": {},
    "postskill": {},
    "created_skills": {},
    "skill_quality": {},
    "skill_mutation_violations": {}
  }
}
```

Each run also writes a `.trajectories.json` file containing transcripts, workspace summaries,
grading details, and errors for debugging.

## Project Structure

```text
evoclawbench/
├── scripts/
│   ├── benchmark.py       # Main orchestration
│   ├── lib_agent.py       # Runtime adapters, prompts, workspace/skill flow
│   ├── lib_grading.py     # Automated / LLM / hybrid grading
│   ├── lib_metrics.py     # Three-mode metrics and legacy helpers
│   └── lib_tasks.py       # Task loading
├── tasks/                 # Markdown task definitions
├── assets/                # Task fixtures
├── results/               # Output artifacts
├── workspaces/            # Per-run working directories
└── pyproject.toml
```

## Development

```bash
uv run pytest tests/ -v
uv run ruff check scripts/ tests/
uv run black scripts/ tests/
```
