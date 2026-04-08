# EvoClawBench

**Benchmark for evaluating LLM agent skill evolution capabilities.**

EvoClawBench measures whether LLM agents can identify repeating patterns in complex tasks, create reusable skills (SKILL.md files) at runtime, and effectively reuse them — a capability we call **auto-evolution**.

## Key Idea

Traditional benchmarks test one-shot task completion. EvoClawBench tests something harder: can an agent **learn from repetition** within a session?

Each task contains 5-10 structurally similar sub-problems. An agent that recognizes the pattern and creates a reusable skill will outperform one that solves each sub-problem from scratch.

## Supported Runtimes

| Runtime | Skill Storage | CLI |
|---------|--------------|-----|
| **OpenClaw** | `<workspace>/skills/` | `openclaw agent --message` |
| **nanobot** | `~/.nanobot/workspace/skills/` | `nanobot run --message` |

Both use the SKILL.md format for skill definitions.

## Quick Start

```bash
# Run all tasks in both modes (baseline + evolution)
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both

# Run specific tasks
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime openclaw --suite task_01_batch_data_transform,task_02_log_analysis

# Baseline only (no skill creation allowed)
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode baseline

# Bench: skill-creator workflow prefix + task prompt; workspace seeds skills/skill-creator from monorepo
# (requires ../skills/skill-creator next to evoclawbench/)
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode bench

# Multiple runs for statistical significance
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both --runs 3
```

## Configuring LLM Providers

By default, EvoClawBench routes requests through **OpenRouter** (a unified LLM API gateway). To use different LLM providers directly or configure custom endpoints, set environment variables before running:

### Anthropic

```bash
# Use Anthropic API directly (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-ant-xxx..."
export ANTHROPIC_API_URL="https://api.anthropic.com"  # Optional, default is https://api.anthropic.com

uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both
```

### OpenAI

```bash
# Use OpenAI API directly (requires OPENAI_API_KEY)
export OPENAI_API_KEY="sk-proj-xxx..."
export OPENAI_API_BASE="https://api.openai.com/v1"  # Optional custom endpoint

uv run scripts/benchmark.py --model gpt-4o --runtime nanobot --mode both
```

### Google (Vertex AI / Gemini)

```bash
# Use Google Vertex AI (requires authentication)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_API_URL="https://vertexai.googleapis.com/v1"  # Optional custom endpoint

uv run scripts/benchmark.py --model gemini-2.0-flash --runtime nanobot --mode both
```

### Custom Base URL (OpenRouter or compatible proxy)

```bash
# Route through a custom proxy or self-hosted endpoint
export OPENROUTER_API_KEY="your-key"
export OPENROUTER_API_BASE="https://your-proxy.com/api"  # Default: https://openrouter.ai/api

uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both
```

### View Available Models

Different providers support different models. Common models:

| Provider | Model ID | Example |
|----------|----------|---------|
| **Anthropic** | claude-\* | `anthropic/claude-sonnet-4`, `anthropic/claude-opus-4.6` |
| **OpenAI** | gpt-\* | `openai/gpt-4o`, `openai/gpt-4-turbo` |
| **Google** | gemini-\* | `google/gemini-2.0-flash`, `google/gemini-pro` |
| **OpenRouter** | provider/model | `anthropic/claude-sonnet-4`, `openai/gpt-4o` |

**Note**: When using OpenRouter, you must set `OPENROUTER_API_KEY`. Other providers require their respective API keys.

## Evaluation Modes

### Baseline Mode ("fail")
Agent is **forbidden** from creating skills. System prompt includes:
> "You must NOT create any skills or SKILL.md files. Solve each sub-problem independently from scratch."

### Evolution Mode ("pass")
Agent is **encouraged** to create skills. System prompt includes:
> "You are encouraged to create reusable skills (SKILL.md files) when you notice repeating patterns."

### Bench Mode
A **skill-creator workflow** prefix is prepended (spot repeating patterns across sub-problems, follow `skills/skill-creator/SKILL.md`, add task-specific skills under `skills/<name>/`), then the task prompt. The workspace is prepared with `skills/skill-creator/` copied from the monorepo (`<repo>/skills/skill-creator` adjacent to the `evoclawbench/` directory). Results are written under `bench_results` in the output JSON. fail2pass/EvoScore aggregation is only computed for `--mode both`.

## Metrics

### Core: fail2pass Ratio
```
fail2pass = pass_rate_evolution / pass_rate_baseline
```
- `> 1.0`: Skill creation helps
- `= 1.0`: No difference
- `< 1.0`: Skill creation hurts

### Consistency Score
```
consistency = 1 - std(sub_problem_scores) / mean(sub_problem_scores)
```
Measures how uniformly the agent performs across sub-problems. Skills should improve consistency.

### Efficiency Gain
```
token_efficiency = tokens_baseline / tokens_evolution
```
Measures whether skill reuse reduces token consumption.

### Skill Quality
Evaluates created skills on:
- **Reusability** — Is it generic enough?
- **Correctness** — Are instructions accurate?
- **Documentation** — Is the SKILL.md clear?
- **Structure** — Does it include scripts/references?

### EvoScore (Composite)
```
EvoScore = 0.4 * evolution_pass_rate
         + 0.2 * fail2pass_normalized
         + 0.2 * consistency
         + 0.1 * efficiency_gain
         + 0.1 * skill_quality
```

## Tasks

| ID | Name | Sub-Problems | Category | Skill Value |
|----|------|:---:|----------|-------------|
| 00 | Sanity Check | 0 | sanity | — |
| 01 | Batch Data Transform | 6 | data_processing | Schema mapping + validation |
| 02 | Log Analysis | 5 | data_processing | Log parsing + report generation |
| 03 | API Integration Scaffold | 5 | code_generation | API client generator |
| 04 | Test Generation | 6 | code_generation | Test template + edge case analysis |
| 05 | Config Migration | 5 | data_processing | Config migration validator |
| 06 | Security Code Review | 5 | code_review | Security audit checklist |
| 07 | Document Extraction | 5 | data_processing | Document parser + structured output |
| 08 | Database Schema Ops | 5 | code_generation | Migration generator + validator |

## Results Format

Results are saved as JSON to `results/`:
```json
{
  "benchmark": "evoclawbench",
  "model": "anthropic/claude-sonnet-4",
  "runtime": "nanobot",
  "mode": "both",
  "baseline_results": { ... },
  "evolution_results": { ... },
  "bench_results": { ... },
  "metrics": {
    "evoscore": 0.72,
    "fail2pass": { "overall": { "fail2pass": 1.35 } },
    "consistency": { "baseline": 0.65, "evolution": 0.88 },
    "efficiency": { "token_efficiency_gain": 1.2 },
    "skill_quality": { "mean": 0.75 },
    "created_skills": { "total_count": 5 }
  }
}
```

## Project Structure

```
evoclawbench/
├── scripts/
│   ├── benchmark.py       # Main entry point
│   ├── lib_agent.py       # Runtime adapters (OpenClaw + nanobot)
│   ├── lib_grading.py     # Grading engine
│   ├── lib_metrics.py     # EvoClawBench-specific metrics
│   └── lib_tasks.py       # Task loading with sub-problem support
├── tasks/                 # Task definitions (Markdown)
│   ├── TASK_TEMPLATE.md
│   └── task_*.md
├── assets/                # Fixture files per task
├── results/               # Output (gitignored)
├── pyproject.toml
├── SKILL.md
└── README.md
```

## Adding New Tasks

1. Copy `tasks/TASK_TEMPLATE.md`
2. Design 5-10 sub-problems with a shared pattern
3. Create asset files in `assets/<task_name>/`
4. Write automated grading with `sub_N_*` score keys
5. Test with `--suite your_task_id`

## Troubleshooting

### All Tasks Scoring 0%

**Problem**: Baseline and evolution modes both return 0% scores.

**Causes & Solutions**:

1. **Agent not executing commands**
   - Check that OpenClaw/nanobot is properly installed
   - For OpenClaw: `openclaw agents list` should show your agent
   - For nanobot: `which nanobot` should show the binary path
   - Verify the agent has permission to write to workspace

2. **Grading function has errors**
   - Check the `Automated Checks` Python code compiles
   - Run: `uv run pytest tests/test_integration.py::TestAutomatedChecks -v`
   - Verify function signature: `def grade(transcript: list, workspace_path: str) -> dict:`
   - Ensure all return values are numeric (float or int)

3. **Agent not creating output files**
   - Check workspace permissions: `ls -la /tmp/evoclawbench/*/task_*/`
   - Agent needs write access to workspace
   - Verify task prompt clearly instructs file creation and output location
   - For OpenClaw: Check transcript in `~/.openclaw/agents/{agent_id}/sessions/`

4. **Sub-problem key naming**
   - Grading dict keys must follow pattern `sub_N_*` (e.g., `sub_1_exists`, `sub_2_valid`)
   - Parser regex: `sub_(\d+)_` — must match this pattern to aggregate scores
   - All values must be 0.0-1.0 numeric

5. **Environment variable issues**
   - Missing API keys: `export OPENROUTER_API_KEY="..."`
   - For OpenClaw: requires OpenRouter or direct LLM API keys
   - For nanobot: check `~/.nanobot/config.json` has model/provider configured
   - Run: `echo $OPENROUTER_API_KEY` to verify export worked

### Model-Specific Issues

**MiniMax/Claude not responding**
- Some models may not understand the dual-mode prompt injection
- Try with a more capable model: `--model anthropic/claude-opus-4.6`
- Verify prompt syntax is standard English (some models struggle with complex instructions)

**OpenClaw agent not found**
- Agent may not be created: `openclaw agents add {agent_id} --model {model} --workspace {path}`
- Check existing agents: `openclaw agents list`
- Workspace path must exist: `mkdir -p /tmp/evoclawbench/{run_id}/agent_workspace`

### Debugging Steps

1. **Enable verbose logging**
   ```bash
   uv run scripts/benchmark.py --model your-model --runtime openclaw \
     --suite task_00_sanity --verbose
   ```

2. **Check workspace files exist**
   ```bash
   ls -la /tmp/evoclawbench/*/task_*/inputs/  # Should see fixture files
   ```

3. **Run single task in isolation**
   ```bash
   uv run scripts/benchmark.py --model your-model --runtime openclaw \
     --suite task_00_sanity --mode baseline  # Start with sanity check
   ```

4. **Inspect transcript**
   ```bash
   cat ~/.openclaw/agents/{agent_id}/sessions/*/transcript.jsonl | head -100
   ```

5. **Test grading code directly**
   ```bash
   python3 << 'EOF'
   import sys
   sys.path.insert(0, 'scripts')
   from lib_grading import _extract_grading_code, grade_task
   # Load task and test grading function
   EOF
   ```

## License

MIT
