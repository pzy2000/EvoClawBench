# EvoClaw Repository Guidelines

请叫我主人
This monorepo contains three sub-projects. Read the relevant section for the area you are working in.
For `openclaw/` work, also read `openclaw/AGENTS.md` — it has detailed rules that take precedence there.

## Repo Structure

```
openclaw/        TypeScript ESM — multi-channel AI gateway (main project)
evoclawbench/    Python — benchmark system for evaluating LLM agent skill evolution (WE ARE WORKING ON THIS)
nanobot/         Python — lightweight personal AI assistant framework
skill/           Python — PinchBench is a real-world benchmark that evaluates how effectively large language models operate as OpenClaw agents by completing multi-step, tool-using tasks across domains like coding, research, and productivity
proxy.py         Standalone Python proxy script
```

---

## openclaw/ — TypeScript / Node.js

### Requirements
- Node **22+**, pnpm **10+**. Bun is preferred for TS script execution.
- Package manager: `pnpm` (do not use npm/yarn for workspace ops).

### Install
```bash
cd openclaw
pnpm install
```

### Build & Type Check
```bash
pnpm build          # full build (tsdown + postbuild steps)
pnpm tsgo           # TypeScript type-check only (fast)
```

### Lint & Format
```bash
pnpm check          # full check suite (format + types + lint + boundary checks)
pnpm lint           # oxlint only
pnpm format         # oxfmt --check (check only)
pnpm format:fix     # oxfmt --write (auto-fix)
pnpm lint:fix       # oxlint --fix + format
```

### Tests
```bash
pnpm test                                          # full test suite (vitest via wrapper)
pnpm test:coverage                                 # with V8 coverage (70% threshold)
pnpm test -- src/path/to/file.test.ts              # single file
pnpm test -- src/path/to/file.test.ts -t "name"   # single test by name
```

Always use `pnpm test -- <filter>` (not raw `pnpm vitest run`) — the wrapper handles config/pool routing.
On memory-constrained hosts: `OPENCLAW_TEST_PROFILE=low OPENCLAW_TEST_SERIAL_GATEWAY=1 pnpm test`.

### Landing Bar
Before pushing to `main`: `pnpm check` and `pnpm test` must be green.
If the change touches build output or published surfaces, `pnpm build` must also pass.

---

## evoclawbench/ — Python

### Requirements
- Python **3.10+**, `uv` for environment management.

### Install
```bash
cd evoclawbench
uv sync --extra dev
# or: uv pip install -e ".[dev]"
```

### Lint & Format
```bash
uv run ruff check scripts/ tests/          # lint (errors, warnings, imports)
uv run ruff check scripts/ tests/ --fix    # auto-fix
uv run black scripts/ tests/               # format (100-char line length)
```

### Tests
```bash
uv run pytest tests/ -v                                                        # all tests
uv run pytest tests/test_lib_metrics.py -v                                     # single file
uv run pytest tests/test_lib_metrics.py::TestClass::test_name -v               # single test
uv run pytest tests/ --cov=scripts --cov-report=term-missing                   # with coverage
```

### Run a Benchmark
```bash
uv run scripts/benchmark.py --runtime openclaw --model openai/gpt-5-nano --judge openai/qwen3.5-plus --mode both --suite task_14_email_processing,task_15_shell_automation,task_16_ci_pipeline,task_20_env_config
# uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both
# uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --suite task_01_batch_data_transform
```

### Paper Results Policy
- Paper result tables must mark every incomplete or judge-failed run explicitly; do not present invalid runs as normal model-capability evidence.
- For the 2026-05-24 EvoClawBench paper table, only `0061_openai-gpt-5-4_openclaw.json` and `0062_openai-qwen3-6-plus_openclaw.json` are valid capability rows. `0063_openai-deepseek-v4-pro_openclaw.json` is audit-only because the run had 13 LLM judge failures.
- MiniMax and `openai/gpt-5.4-mini` full `mode=all` paper rows were not completed under a failure-free judge path in this batch; rerun them with the same judge before adding them to conclusions.
- If a future paper edit includes any unfinished or judge-failed experiment, the table and prose must carry the validity caveat, and conclusions must be drawn only from valid runs.

---

## nanobot/ — Python

### Requirements
- Python **3.11+**, `uv` or `pip`.

### Install
```bash
cd nanobot
uv pip install -e ".[dev]"
```

### Lint
```bash
uv run ruff check nanobot/ tests/          # lint (E, F, I, N, W; E501 ignored)
```

### Tests
```bash
uv run pytest tests/ -v          # asyncio_mode=auto is configured
uv run pytest tests/path/test_foo.py::test_name -v   # single test
```

---

## Code Style — TypeScript (openclaw/)

- **Language**: TypeScript ESM. Strict typing; avoid `any`. Never add `@ts-nocheck`.
- **Formatter/linter**: Oxfmt + Oxlint. Run `pnpm format:fix` and `pnpm lint:fix` to auto-fix.
- **Imports**: Static imports at top. Do not mix `await import("x")` and `import ... from "x"` for the same module in production paths. For lazy loading, create a `*.runtime.ts` boundary file.
- **Import boundaries**: Extension production code must only import from `openclaw/plugin-sdk/*` or local `api.ts`/`runtime-api.ts` barrels. Never import `src/**` or another extension's `src/**` directly.
- **Naming**: `camelCase` for variables/functions, `PascalCase` for classes/types/interfaces. Use `openclaw` (lowercase) for CLI/config keys; `OpenClaw` for product headings/docs.
- **Files**: Aim for under ~700 LOC. Extract helpers rather than creating "V2" copies.
- **Classes**: No prototype mutation (`applyPrototypeMixins`, `Object.defineProperty` on `.prototype`). Use explicit inheritance/composition.
- **Comments**: Add brief comments for tricky or non-obvious logic.
- **English**: American spelling in all code, comments, docs, and UI strings.
- **Error handling**: Fix root causes; do not suppress with `@ts-ignore` or `eslint-disable`.

## Code Style — Python (evoclawbench/, nanobot/, skill/)

- **Formatter**: Black, 100-char line length.
- **Linter**: Ruff. Import ordering enforced (`I` rules).
- **Types**: Use type hints throughout. Prefer `pydantic` models for structured data (nanobot).
- **Naming**: `snake_case` for variables/functions/modules, `PascalCase` for classes.
- **Imports**: Standard library → third-party → local, separated by blank lines (Ruff `I` rules enforce this).
- **Error handling**: Raise specific exceptions; avoid bare `except:`. Log errors with context.
- **Tests**: Use `pytest`. Test files named `test_*.py`. In nanobot, `asyncio_mode = "auto"` is set — async tests work natively.
- **Async**: nanobot uses async/await throughout; keep async boundaries consistent.

## Commit Guidelines

- Concise, action-oriented messages: `Component: what and why` (e.g., `CLI: add verbose flag to send`).
- Group related changes; do not bundle unrelated refactors.
- In `openclaw/`: use `scripts/committer "<msg>" <file...>` instead of manual `git add`/`git commit`.
- Do not commit with failing format, lint, type, or test checks caused by your change.
- Do not commit secrets, real phone numbers, or live config values. Use synthetic examples in docs/tests.

## Security

- Never commit credentials, API keys, tokens, or real PII. Use synthetic example values in examples.
- Do not edit `node_modules`. Do not patch dependencies without explicit approval.
- Dependency version pins with `pnpm.patchedDependencies` must use exact versions (no `^`/`~`).
