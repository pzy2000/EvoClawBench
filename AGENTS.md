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
- Paper result tables must record the source JSON and any known run caveats for reproducibility; do not describe completed result rows as unfinished.
- For the 2026-05-24 EvoClawBench paper table, the current complete OpenClaw `mode=all` rows are `0061_openai-gpt-5-4_openclaw.json`, `0062_openai-qwen3-6-plus_openclaw.json`, `0063_openai-deepseek-v4-pro_openclaw.json`, `0064_openai-minimax-minimax-m2-7_openclaw.json`, and `0065_openai-gpt-5-4-mini_openclaw.json`.
- `0063_openai-deepseek-v4-pro_openclaw.json` is treated as a complete result row for this paper batch per the current user decision; do not relabel it audit-only unless the experimental policy changes or a replacement run is selected.
- If a future paper edit includes an unfinished experiment, missing result mode, or rejected run, the table and prose must explicitly mark that status instead of writing it as a normal completed result.

### Paper Figure OCR PDF Conversion
- Scope: convert PNG figures actually referenced by `paper/main.tex` into searchable PDFs with copyable Chinese/English text. Do not treat unused PNG files in `paper/Figures/` as paper-used unless the LaTeX reference changes. In the current manuscript, `fig_suite_distribution.png` is not part of this pass because `paper/main.tex` includes `Figures/fig_suite_distribution.pdf`.
- Method:
```bash
cd paper/Figures
img2pdf <figure>.png -o <figure>.raw.pdf
ocrmypdf -l chi_sim+eng --deskew --output-type pdf \
  <figure>.raw.pdf <figure>.searchable.pdf
```
- Conversion record, 2026-05-25: used `/opt/homebrew/bin/img2pdf` and `/opt/homebrew/bin/ocrmypdf`; Tesseract language data included `chi_sim` and `eng`; `ocrmypdf` completed successfully with non-fatal Noto CJK font warnings; `paper/main.tex` now includes the `*.searchable.pdf` outputs instead of the source PNG files.
- Converted paper PNG figures:
  - `fig_overview_imagegen.png` -> `fig_overview_imagegen.raw.pdf` -> `fig_overview_imagegen.searchable.pdf`; verified 1 page, `pdftotext` extracted 1459 characters.
  - `fig_skill_anatomy_imagegen.png` -> `fig_skill_anatomy_imagegen.raw.pdf` -> `fig_skill_anatomy_imagegen.searchable.pdf`; verified 1 page, `pdftotext` extracted 1352 characters.
  - `fig_failure_case_imagegen.png` -> `fig_failure_case_imagegen.raw.pdf` -> `fig_failure_case_imagegen.searchable.pdf`; verified 1 page, `pdftotext` extracted 1872 characters.
  - `fig_protocol_imagegen.png` -> `fig_protocol_imagegen.raw.pdf` -> `fig_protocol_imagegen.searchable.pdf`; verified 1 page, `pdftotext` extracted 1444 characters.

### Changes to Paper (GOAL)
- Anticipated reviewer concern: "The paper overclaims self-evolution and hides the mixed/negative result behind a broad benchmark pitch." Location: `paper/main.tex` title, abstract, Introduction, Results, and Discussion. Change: replaced the earlier broad self-evolution title wording with narrower runtime skill creation/reuse language; rewrote the abstract to foreground the closed-loop evaluation question, three controlled strategies, 100-task/502-subproblem suite, JSON-backed OpenClaw local/worker/mode setup, and mixed result pattern; replaced remaining broad "self-evolution" phrasing with narrower runtime skill creation/reuse language. Evidence: current manuscript, current `0061`-`0065` result JSON metrics, and ARR review-form emphasis on soundness and adequately supported claims.
- User title/framing request: "The title should ask whether LLM agents can learn reusable skills from their own runs, without implying the answer is always positive." Location: `paper/main.tex` title, abstract, Introduction, Related Work, Discussion, and Ethical Considerations. Change: changed the title to `EvoClawBench: Can LLM Agents Learn Reusable Skills from Their Own Runs?`; aligned nearby prose so `\postskill{}` is the own-run learning condition and `\preskill{}` remains a pre-execution control; preserved the mixed-result stance that self-authored skills can regress, preserve, or improve quality and may add cost. Evidence: current manuscript wording and repository-local result tables/caveats already summarized in the paper.
- Anticipated reviewer concern: "The abstract and introduction contain unsupported breadth signaling and make the benchmark contribution sound broader than the evidence." Location: `paper/main.tex` abstract and Introduction. Change: shortened the long domain enumeration in the abstract, moved the broad task description to the construction section, and reframed novelty as a focused gap in same-runtime skill authoring, summarization, and reuse rather than an absolute first-ever claim. Evidence: existing `SkillsBench` citation, existing related-work bibliography, and official EMNLP paper-integrity warning against hallucinated or overbroad claims.
- Anticipated reviewer concern: "The related-work table may invite fact-check failures because benchmark sizes and broad Yes/Partial feature labels are easy to dispute across versions." Location: `paper/main.tex` Table 1. Change: replaced the detailed feature matrix with a high-level positioning table grouped by benchmark family, primary evaluation focus, and how skills enter evaluation. Evidence: existing verified bibliography entries and ARR/EMNLP expectations for careful citation and comparison.
- Anticipated reviewer concern: "The Related Work section does not clearly distinguish EvoClawBench from SkillsBench's curated and pre-solution self-generated skill settings." Location: `paper/main.tex` Related Work. Change: clarified that SkillsBench evaluates curated Skills and a pre-solution self-generated Skills condition, while EvoClawBench separates pre-execution skill authoring via `\preskill{}` from post-run own-evidence skill learning via `\postskill{}`; added a concise bridge sentence making the skill lifecycle itself the evaluated object. Evidence: current Related Work wording in `paper/main.tex` and the local `SkillsBench` citation `\citep{li2026skillsbench}` in `paper/references.bib`.
- Anticipated reviewer concern: "The task and fixture construction is under-described for reproducibility and responsible research review." Location: `paper/main.tex` Task Suite and Workspace/Fixtures subsections. Change: added that the loader includes a sanity task but the official suite excludes it; clarified repository-local/synthetic hard-mode fixtures, decoys, stale revisions, fixture immutability, and grader-visible artifact outputs. Evidence: `evoclawbench/tasks/task_*.md`, generated-task fixture wording, and the Responsible NLP checklist's artifact/data transparency prompts.
- Anticipated reviewer concern: "The evaluation protocol is not explicit enough about what execution-only and end-to-end metrics prove." Location: `paper/main.tex` Metrics subsection. Change: added an explicit explanation that execution-only metrics test final task benefit, while end-to-end metrics test whether authoring/summarization overhead is worth the cost. Evidence: `evoclawbench/README.md` metric definitions and current JSON `metrics.execution_only` / `metrics.end_to_end` objects.
- Anticipated reviewer concern: "The result table needs stronger provenance and caveat handling, and the hybrid-judge setting must not be presented as JSON provenance because the current JSON schema does not serialize it." Location: `paper/main.tex` Experimental Setup and Table 2 footnote. Change: recorded that all five source files contain 303 top-level task-mode results and no non-empty top-level error fields; noted the current source JSON filenames; marked `0061` and `0063` postskill token/cost efficiency as unavailable because their JSONs report zero postskill token usage; separated the hybrid judge name as run-command provenance rather than JSON provenance. Evidence: `jq` inspection of `0061`-`0065` under `evoclawbench/results/`, plus current repository run policy for the paper batch.
- Anticipated reviewer concern: "Skill-count analysis could confuse mutation-free failures with uncontrolled skill editing." Location: `paper/main.tex` Finding 4. Change: added that the five reported runs record zero skill mutation violations, so the observed regressions are not explained by reuse-phase skill editing. Evidence: `metrics.skill_mutation_violations` in `0061`-`0065`.
- Anticipated reviewer concern: "Limitations are too compressed for ARR review and omit obvious scope boundaries." Location: `paper/main.tex` Limitations. Change: expanded the section into transfer scope, experimental coverage, grading dependence, and runtime scope, explicitly naming same-fixture reruns, single-run configuration, lack of confidence intervals, local OpenClaw/nanobot reporting, and judge dependence. Evidence: current protocol description, current JSON configuration, and ARR Responsible NLP limitation guidance.
- Anticipated reviewer concern: "The paper lacks a direct ethical/societal-impact discussion for agent skill creation." Location: `paper/main.tex` new `Ethical Considerations` section. Change: added intended research use, synthetic/repository-local fixture framing, no human subjects/crowdworkers/new personal data, privacy/security/domain-risk caveats, dual-use concerns, and deployment safeguards such as human review, provenance, and disabling unsafe skills. Evidence: task fixture design, repository security guidance, and ARR Responsible NLP checklist prompts.
- Independent-review concern: "Artifact transparency is still under-specified for a benchmark/resource paper." Location: `paper/main.tex` new `Artifacts and Data Statement` section. Change: added the artifact contents (`evoclawbench/tasks`, `assets`, `scripts`, and the five reported `results` JSON files), the MIT license declared in `evoclawbench/pyproject.toml`, anonymous-review URL handling, and the fact that reported fixtures are benchmark cases rather than newly collected human-subject data. Evidence: local repository layout and `evoclawbench/pyproject.toml`.
- Anticipated reviewer concern: "Anonymous review submissions should not include acknowledgments stubs." Location: `paper/main.tex` before bibliography. Change: removed the `Acknowledgments` section that said "Omitted for anonymous review." Evidence: ARR common-submission-problem guidance that acknowledgements should not be included in anonymous submissions.
- Anticipated reviewer concern: "Reproducibility details are split across prose and JSON names." Location: `paper/main.tex` appendix. Change: added `Reproducibility Details for Reported Runs` with the serialized `mode=all`, `--workers 32`, `--environment local`, one-run-per-task setting, five source JSON filenames, result object names, explicit note that judge model is not serialized in those JSONs, and null-efficiency interpretation. Evidence: current benchmark JSON schema, `evoclawbench/README.md`, and the current source JSON files.
- Anticipated reviewer concern: "The appendix is too thin for a benchmark/resource paper and does not expose the actual evaluation prompts." Location: `paper/main.tex` appendix `Mode Prompt Prefixes` and `PostSkill First-Run Context`. Change: expanded the appendix with the baseline, preskill authoring, postskill summary, and skill-reuse prompt prefixes; added the prompt-assembly table and the serialized `.evoclawbench/first_run_context.json` fields used by the postskill summary phase. Evidence: `evoclawbench/scripts/lib_agent.py` prefix constants and `evoclawbench/scripts/benchmark.py` first-run context writer.
- Anticipated reviewer concern: "The claimed 100-task suite is not auditable from the paper." Location: `paper/main.tex` appendix `Official Task Inventory`, `Per-Task Prompt and Output Surfaces`, and `Per-Task Grading Surfaces`. Change: added generated appendix tables listing the 100 official tasks excluding `task_00_sanity`, ASCII-safe task names, family/category, grading type, subproblem count, fixture count/extensions, prompt focus, output surface, and representative grading criteria. Evidence: `TaskLoader` inspection of `evoclawbench/tasks/task_*.md`, confirming 101 loaded tasks, 100 official tasks, 502 official subproblems, 88 automated tasks, and 12 hybrid tasks.
- Anticipated reviewer concern: "Domain-family labels alone do not demonstrate meaningful benchmark diversity." Location: `paper/main.tex` appendix `Task Families and Fixture Mechanics`, `Generated Family Design Matrix`, `Hard-Mode Evidence Protocol`, and `Representative Output Schemas`. Change: added family-level descriptions of repeated structure, anti-shortcut mechanics, grader-visible artifacts, evidence-packet selection rules, channel derivation rules, fixture formats, and representative output schemas for generated hard-mode families. Evidence: generated task markdown prompts and hard-mode fixture protocol in `evoclawbench/tasks/task_22` through `task_100`.
- Anticipated reviewer concern: "Result provenance and integrity checks should be visible without reopening JSON files." Location: `paper/main.tex` appendix `Result JSON Schema`, `Result Validity Checklist`, `Reported Result Integrity Summary`, and `Reproducibility Details for Reported Runs`. Change: expanded the result schema, added a 5-row integrity table for `0061`-`0065` with mode/workers/result counts/mutation counts, and separated command provenance from serialized JSON fields. Evidence: `jq`/JSON inspection of the five current OpenClaw result files.
- Anticipated reviewer concern: "The appendix needs to be long enough to carry benchmark transparency rather than compressing critical details into the main text." Location: `paper/main.tex` appendix and compiled `paper/main.pdf`. Change: converted the appendix to one-column longtable layout, added `longtable`/`array` support, and compiled the manuscript to exactly 28 pages including bibliography and appendix. Evidence: `make` in `paper/` and `pdfinfo paper/main.pdf` reporting `Pages: 28`.
- Independent-review concern: "The expanded appendix has a visible page-25 overflow, three corrupted task-criteria rows, and prompt-prefix wording that could be read as more verbatim than the typeset excerpt." Location: `paper/main.tex` appendix `Mode Prompt Prefixes`, `Per-Task Grading Surfaces`, and the appendix sections after `Representative Output Schemas`. Change: restored the task-14, task-17, and task-19 grading criteria text; typeset the four prompt-prefix strings with preserved backticks while noting that trailing blank lines are omitted for typesetting; changed fixed-position appendix floats to flexible floats; inserted a page break after the representative schema longtable; and removed a later unnecessary page break so the compiled PDF remains exactly 28 pages without the page-25 overflow. Evidence: independent subagent review, rendered page-25 inspection, `paper/main.log` no longer reporting `Overfull \vbox`, and `pdfinfo paper/main.pdf` reporting `Pages: 28`.
- User layout concern: "Appendix prompt section should look better and be screenshot-verified for visual quality." Location: `paper/main.tex` appendix `Mode Prompt Prefixes` and compiled `paper/main.pdf` page 11. Change: replaced plain quote prompt blocks with consistent gray prompt boxes that put the phase label and runtime mode line in the header, preserved the prefix wording with `\detokenize`, and converted the prompt-assembly table from a floating table to an in-place captioned table so it appears after the prompt boxes rather than above the section heading. Evidence: screenshot inspection of pages 11, 12, 25, and 28; `make` in `paper/`; `paper/main.log` with no fatal errors or `Overfull \vbox`; and `pdfinfo paper/main.pdf` reporting `Pages: 28`.
- User layout concern: "Appendix tables should not look cramped or isolated, especially the representative output schema table." Location: `paper/main.tex` appendix tables around `Hard-Mode Evidence Protocol`, `Representative Output Schemas`, `Suite Distributions`, `Skill Artifact Structure`, `Result JSON Schema`, and `Reported Result Integrity Summary`. Change: added ragged-right table column types, converted appendix floats to in-place captioned tables/figure so tables remain under their section headings, removed the forced page break that isolated Table 11, combined the two suite-distribution tables into aligned side-by-side minipages, tightened the result-integrity table spacing, and inserted a natural final-section page break to keep the compiled manuscript at exactly 28 pages. Evidence: screenshot inspection of pages 24, 25, 26, 27, and 28; `make` in `paper/`; no fatal LaTeX errors or overfull hbox/vbox warnings in `paper/main.log`; and `pdfinfo paper/main.pdf` reporting `Pages: 28`.
- Anticipated reviewer concern: "The main result table conflates loaded-task counts with completed result objects and hides a reuse-integrity caveat." Location: `paper/main.tex` Experimental Setup, Table 2, Finding 4, appendix `Reported Result Integrity Summary`, and appendix `Reproducibility Details for Reported Runs`. Change: added a `Results` column with baseline/preskill/postskill object counts, clarified that `Loaded` is the loader count, corrected `0080` mutation integrity from `0/0` to `0/1`, and explicitly caveated `0080` as having 100 postskill result objects plus one postskill mutation violation instead of treating it as a clean mutation-free row. Evidence: `jq` inspection of `evoclawbench/results/0080_openai-minimax-minimax-m2-7_nanobot.json` showing `postskill_results|length == 100` and `metrics.skill_mutation_violations.postskill == 1`.
- Anticipated reviewer concern: "Cross-runtime score differences could be misread as a leaderboard or as proof that one runtime is inherently better." Location: `paper/main.tex` Finding 1 and Discussion. Change: added explicit language that runtime covers prompt wrapping, workspace setup, tool invocation, and usage extraction, and that benchmark reporting must include provenance, mutation checks, and end-to-end resource accounting rather than execution scores alone. Evidence: current OpenClaw/nanobot adapter descriptions and the runtime-specific score contrast in Table 2.
- Anticipated reviewer concern: "The subset cost, ablation, and judge robustness checks could be overinterpreted as definitive full-suite conclusions." Location: `paper/main.tex` abstract, contributions, `Subset Cost, Amortization, and Robustness Checks`, and judge-robustness paragraph. Change: added that the subset analyses are focused audits rather than replacements for the full-suite table, framed the ablations as single-run diagnostic controls for attribution rather than headline results, and stated that alternate-judge agreement reduces but does not remove judge dependence. Evidence: `evoclawbench/results/paper_subset_experiments/cost_amortization_summary.md`, `ablation_summary.md`, `judge_robustness_summary.md`, and `judge_robustness_gpt54mini_summary.md`.
- Anticipated reviewer concern: "Caveated runs and artifact audit paths are not explicit enough for reproducibility review." Location: `paper/main.tex` Limitations, `Artifacts and Data Statement`, and appendix reproducibility text. Change: added a `Run completeness and caveat handling` limitation explaining the non-splicing policy for `0076` and `0080`, and added artifact-audit wording that points reviewers from paper rows to exact source JSON files and caveats. Evidence: repository-local result JSON filenames, focused rerun files `0082` and `0083`, and the existing artifact layout under `evoclawbench/results/`.
- Anticipated reviewer/editor concern: "The main body risks exceeding the EMNLP/ARR long-paper page budget if detailed subset tables stay in the counted text." Location: `paper/main.tex` main `Subset Cost, Amortization, and Robustness Checks` subsection and new appendix `Subset Audit Details`. Change: moved the subset cost table, amortized break-even table, skill-content ablation table, and qualitative failure-mode figure from the main text to the appendix while keeping the main text summary and cross-references; this leaves Discussion and Limitations on page 8 and moves References to page 9 in the compiled PDF. Evidence: official EMNLP 2026 main-paper call listing long papers as 8 pages and current `pdftotext`/`pdfinfo` checks showing Discussion page 8, Limitations page 8, References page 9, and `paper/main.pdf` at 29 pages including appendix.
- Independent-review concern: "The `0080` caveat still underreports timeout status entries and two wording choices could invite unsupported-claim objections." Location: `paper/main.tex` Table 2 footnote, Finding 1, Limitations `Run completeness and caveat handling`, `Runtime scope`, and appendix `Reproducibility Details for Reported Runs`. Change: split the Table 2 footnote into source-file and known-caveat sentences; added that `0080` contains three baseline timeout status entries, two postskill timeout status entries under `task_94_marketing_campaign_qa`, 100 postskill result objects because `task_85_smart_home_support_diagnosis` is missing from full-run postskill results, and one postskill mutation violation; softened the shortcut-resistance sentence from an outcome claim to a design claim; replaced `all major claw frameworks` with `a wider set of agent runtimes`. Evidence: independent subagent review, `jq`/`rg` inspection of `evoclawbench/results/0080_openai-minimax-minimax-m2-7_nanobot.json`, and current `paper/main.tex` wording review.
- User layout/editor concern: "Table 2's source-files footnote is too large and pushes the manuscript page count." Location: `paper/main.tex` Table 2 and appendix `Reported Result Integrity Summary` / `Reproducibility Details for Reported Runs`. Change: removed the source-files/caveats footnote from below Table 2, kept the table itself focused on scores and result-object counts, and left the source JSON list plus caveat details in the appendix and limitations text. Evidence: `make` in `paper/`, `pdfinfo paper/main.pdf` reporting 29 pages after the removal, and appendix sections still listing the reported result files and known caveats.
- User wording request: "Remove provider prefixes from displayed model names in the paper." Location: `paper/main.tex` Table 2, Findings 1--3, and `Subset Cost, Amortization, and Robustness Checks`. Change: removed the provider prefix from the displayed model labels in the experimental results table and prose while preserving the underlying runtime/source-file provenance elsewhere. Evidence: `rg` confirmation in `paper/main.tex` and rebuilt `paper/main.pdf`.
- User naming/provenance request: "Use official published model names in displayed paper results, and fix the erroneous MiniMax/MiniMax-M2.7 prefix." Location: `paper/main.tex` Table 2, Findings 1--3, and `Subset Cost, Amortization, and Robustness Checks`. Change: changed displayed model labels to `GPT-5.4`, `GPT-5.4 mini`, `Qwen3.6-Plus`, `DeepSeek-V4-Pro`, and `MiniMax-M2.7` while preserving JSON filenames/API identifiers as provenance. Evidence: official provider naming sources cited in the user plan, `rg` confirmation in `paper/main.tex`, successful `make -B` in `paper/`, LaTeX log inspection, `pdfinfo paper/main.pdf`, and page-7 PDF screenshot inspection.
- User citation request: "Introduction first paragraph needs more and newer references, with repeated citation-format checks to avoid reference hallucination." Location: `paper/main.tex` Introduction and `paper/references.bib`. Change: rewrote the first Introduction paragraph into two cited claims with ten newly added, primary-source-verified references covering agentic worker systems/benchmarks and skill/procedural-learning work; kept the existing SkillsBench statistic paragraph separate. Evidence: arXiv API/title-page verification for `Composer 2 Technical Report`, OpenHands, TheAgentCompany, Magentic-One, Agent S2, AutoSkill, Trace2Skill, SkillX, SkillMaster, and From History to State; `make` in `paper/`; citation/log checks; and `pdfinfo paper/main.pdf`.
- User table-layout concern: "Loaded is not meaningful in the main results table, and table cells should be centered." Location: `paper/main.tex` Table 2. Change: removed the `Loaded` column from the main results table, moved the 101-task loader scope into the caption, and centered all table columns. Evidence: `make` in `paper/`, LaTeX log inspection, and `pdfinfo paper/main.pdf`.
- User opening-framing request: "Abstract and Introduction should begin from the current agent boom, the growth of agent benchmarks, their closed-loop skill-learning gap, and then introduce EvoClawBench." Location: `paper/main.tex` abstract and Introduction opening. Change: rewrote the abstract opening and first Introduction paragraphs to follow the agent-first benchmark funnel, using existing verified citations and moving the skill-definition paragraph after the benchmark-gap statement. Evidence: forced `make -B` in `paper/`, `pdfinfo paper/main.pdf` reporting 28 pages, and log/keyword checks for fatal errors, undefined citations/references, `Overfull \vbox`, and unsupported self-evolution wording.
- User layout concern: "Table 15 is aesthetically poor." Location: `paper/main.tex` appendix `Suite Distributions` and compiled `paper/main.pdf` Table 15. Change: replaced the combined distribution table with three compact tables: grading types and sub-problem counts as separate side-by-side tables, plus a three-column fixture-extension table below; used short captions and human-readable labels to avoid sparse cells, caption wrapping, and large blank regions. Evidence: `make` in `paper/`, LaTeX log inspection, `pdfinfo paper/main.pdf`, and screenshot inspection of the Table 15 page.
- User placement request: "Move the qualitative failure-case figure into the main text with corresponding prose." Location: `paper/main.tex` Finding 4, `Subset Cost, Amortization, and Robustness Checks`, Discussion, and appendix `Subset Audit Details`. Change: moved `fig_failure_case_imagegen.searchable.pdf` from the appendix into a main-text `figure*` after Finding 4; added正文 prose explaining why \postskill{} first-run evidence can overfit the second execution context; revised Discussion to reference the figure instead of repeating the same claim; and removed the appendix duplicate. Evidence: `make -B` in `paper/`, `pdfinfo paper/main.pdf` reporting 28 pages, log checks showing no fatal errors, undefined references/citations, or overfull hbox/vbox warnings, `pdftotext` confirming Figure 4 on page 8 and References on page 9, and screenshot inspection of page 8.
- User Figure 1 framing concern: "Do not emphasize specific claw runtimes in Figure 1 because only two runtimes were evaluated." Location: `paper/main.tex` Figure 1 caption, abstract contribution wording, `paper/Figures/figure_prompts.md`, and `paper/Figures/fig_overview_imagegen.*`. Change: regenerated Figure 1 with imagegen as a generic `Agent Runtime Interface` diagram instead of drawing named OpenClaw/nanobot runtime samples; updated the caption and figure prompt to use runtime-agnostic interface wording while leaving runtime names in Methods/Results provenance. Evidence: `img2pdf`/`ocrmypdf` regeneration, `make -B` in `paper/`, `pdfinfo paper/main.pdf` reporting 28 pages, log checks showing no fatal errors, undefined references/citations, or overfull hbox/vbox warnings, text checks showing no `OpenClaw`/`nanobot` in the Figure 1 PDF/caption/prompt surfaces, and page-3 screenshot inspection.

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
