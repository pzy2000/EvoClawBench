# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**EvoClawBench** is a benchmark system that evaluates whether LLM agents can recognize repeating patterns across sub-problems within a single task and create reusable skills (SKILL.md files) at runtime — a capability called "auto-evolution."

The core evaluation mechanism compares agent performance in two primary modes:
- **Baseline mode**: Agent is forbidden from creating skills (baseline pass rate)
- **Evolution mode**: Agent is encouraged to create skills (evolution pass rate)

**Bench mode** runs tasks with no benchmark-injected prompt prefix and seeds `workspace/skills/skill-creator/` from `<repo>/skills/skill-creator` (next to the `evoclawbench/` root). Use it when you want the raw task prompt plus a bundled skill-creator tree. Output lands in `bench_results`; composite fail2pass/EvoScore metrics apply only to `--mode both`.

The **fail2pass ratio** (`evolution_pass_rate / baseline_pass_rate`) measures whether skill creation improves performance. Values > 1.0 indicate skill creation benefits the agent.

## Architecture

### Core Design Patterns

1. **Task Structure**: Each task (task_*.md) contains:
   - YAML frontmatter with metadata (id, grading_type, timeout_seconds, sub_problems count)
   - A single **Prompt** section describing all sub-problems (agents process them sequentially in one session)
   - **Expected Behavior** section (expected task approach)
   - **Sub-Problems** section (numbered list of 5-10 structurally similar variations)
   - **Grading Criteria** checklist
   - **Automated Checks** (Python function that scores outputs)
   - **LLM Judge Rubric** (for hybrid grading)

2. **Workspace Management**:
   - Each task run gets an isolated workspace: `/tmp/evoclawbench/{run_id}/{task_id}_{mode}/`
   - In **evolution mode**, `workspace/skills/` directory is created (where agent writes SKILL.md files)
   - In **baseline mode**, `skills/` directory is NOT created (prevents skill creation)
   - In **bench mode**, `workspace/skills/skill-creator/` is populated via `shutil.copytree` from `(skill_dir.parent / "skills" / "skill-creator")`; missing bundle raises `FileNotFoundError`
   - Asset files are copied from `assets/{task_name}/*` into the workspace

3. **Dual Runtime Support**:
   - **OpenClaw**: Agents invoked via `openclaw agent --agent {id} --message "{prompt}"`
   - **nanobot**: Agents invoked via `nanobot run --message "{prompt}"`
   - Both runtimes store skills in SKILL.md format
   - Agent execution is abstracted in `lib_agent.py:execute_task()` dispatcher

4. **Metrics Pipeline**:
   - **Automated grading** (`lib_grading.py:grade_task`): Python `grade(transcript, workspace_path)` function returns dict of scores
   - **Sub-problem scoring**: Grading keys like `sub_1_exists`, `sub_2_valid` are aggregated into `sub_problem_scores` list
   - **Consistency score**: Measures variance across sub-problem scores (higher = more uniform performance)
   - **Efficiency gain**: Baseline tokens / evolution tokens
   - **EvoScore**: Weighted composite (40% pass_rate + 20% fail2pass + 20% consistency + 10% efficiency + 10% skill_quality)

### Key Module Dependencies

- **lib_tasks.py**: Parses task Markdown files into Task objects with sub-problems
- **lib_agent.py**: Executes tasks on OpenClaw/nanobot, prepares isolated workspaces, extracts token usage
- **lib_grading.py**: Runs automated grade functions, extracts sub-problem scores, evaluates skill quality
- **lib_metrics.py**: Computes fail2pass ratio, consistency, efficiency gain, aggregates results
- **benchmark.py**: Orchestrates full benchmark runs (loads tasks → runs baseline mode → runs evolution mode → computes metrics → saves JSON)

## Common Development Tasks

### Run tests
```bash
# All tests
uv run pytest tests/ -v

# Single test file
uv run pytest tests/test_lib_metrics.py -v

# Single test
uv run pytest tests/test_lib_metrics.py::TestComputeFail2Pass::test_basic_improvement -v

# Run with coverage (install pytest-cov first)
uv run pytest tests/ --cov=scripts --cov-report=term-missing
```

### Linting
```bash
# Check code style (Ruff handles import ordering, warnings, errors)
uv run ruff check scripts/ tests/

# Fix auto-fixable issues
uv run ruff check scripts/ tests/ --fix

# Format code (Black, 100-char line length)
uv run black scripts/ tests/
```

### Run a benchmark
```bash
# Full benchmark: both baseline and evolution modes
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both

# Just one task
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --suite task_01_batch_data_transform

# Baseline mode only
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode baseline

# Multiple runs per task for statistical significance
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both --runs 3

# Longer timeout for slower models
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --timeout-multiplier 2.0
```

### Add a new task

1. Copy `tasks/TASK_TEMPLATE.md` to `tasks/task_NN_name.md`
2. Set YAML frontmatter: `id`, `name`, `category`, `grading_type` (automated/llm_judge/hybrid), `timeout_seconds`, `sub_problems` count
3. Create fixture files in `assets/task_name/` and reference them in workspace_files (as plain strings: `"assets/task_name/file.txt"`)
4. Write a detailed **Prompt** describing all sub-problems
5. List sub-problems in **Sub-Problems** section (### Sub-Problem 1: Title, ### Sub-Problem 2: Title, etc.)
6. Write **Grading Criteria** checklist
7. Implement **Automated Checks** Python function:
   - Takes `transcript` (list of OpenClaw message events) and `workspace_path` (str)
   - Returns dict of numeric scores (keys like `sub_1_exists`, `sub_2_valid`, etc.)
   - Use `sub_N_*` key pattern so grading engine can aggregate into `sub_problem_scores`
8. Test: `uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --suite task_NN_name`

## Important Implementation Details

### Workspace File Handling

`lib_agent.py:prepare_workspace()` handles TWO formats for workspace_files:
1. **String format** (current tasks): `"assets/foo/bar.txt"` → copies to `workspace/inputs/bar.txt`
2. **Dict format** (for future use): `{"source": "assets/foo/bar.txt", "dest": "data/bar.txt"}`
3. **Content format** (inline): `{"path": "config.json", "content": "{...}"}`

All three must be supported for backward compatibility.

### Mode Prefix Injection

`lib_agent.py:get_mode_prefix()` returns system prompt prefixes:
- **Baseline**: "You must NOT create any skills or SKILL.md files..."
- **Evolution**: "You are encouraged to create reusable skills..."
- **Bench**: `""` (no prefix; task prompt only)

These are prepended to the task prompt BEFORE sending to the agent (except bench). Workspace layout for skills is controlled by `prepare_workspace()` mode (`baseline` / `evolution` / `bench`).

### Sub-Problem Scoring Aggregation

Grading functions should return keys like:
- `sub_1_exists: 1.0`, `sub_1_valid: 0.5` → averaged per sub-problem → `sub_problem_scores[0] = 0.75`
- `sub_2_exists: 1.0`, `sub_2_valid: 1.0` → `sub_problem_scores[1] = 1.0`

`lib_grading.py:_extract_sub_problem_scores()` parses these automatically using regex pattern `sub_(\d+)_`.

### Skill Quality Heuristic

`lib_grading.py:grade_skill_quality()` scores skills (0-1) based on:
- Has frontmatter name (0.2) and description (0.2)
- Content > 100 chars (0.2), > 500 chars (+0.1)
- Has scripts/ directory (0.2)
- Has references/ directory (+0.1)

Skills can be manually evaluated by LLM judge if higher precision is needed.

## File Conventions

- **Task files** (tasks/task_*.md): YAML frontmatter must include `sub_problems` field (count of sub-problems)
- **Asset files** (assets/{task_name}/*): Referenced as plain strings in workspace_files
- **Grading code**: Wrapped in ```python ... ``` code blocks within Automated Checks section
- **SKILL.md format**: Matches standard OpenClaw/nanobot format (YAML frontmatter + markdown body)

## Test Coverage

The test suite (95 tests, 100% passing):
- **Unit tests** for each module (lib_tasks, lib_metrics, lib_grading, lib_agent)
- **Integration tests** that load all 9 task files, verify YAML syntax, check asset files exist, compile grading code

Run full test suite before submitting PRs: `uv run pytest tests/ -v`
