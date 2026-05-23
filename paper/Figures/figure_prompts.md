# EvoClawBench Figure Prompts

These prompts preserve the image-generation direction for each paper figure.
The committed PDFs in this directory are deterministic vector renderings of the
same concepts so labels remain legible in the ACL manuscript.

## Fig. 1: EvoClawBench Overview

```text
Create a clean academic paper overview diagram for "EvoClawBench", vector-style, white background, ACL paper aesthetic. Show a left-to-right pipeline: Task Suite with repeated sub-problems and fixtures -> Runtime Adapter with OpenClaw and nanobot -> three evaluation lanes labeled Baseline, PreSkill, PostSkill -> fresh execution workspaces -> automated/hybrid graders -> metrics: score, token, cost, time, created skills, mutation violations. Make Baseline show direct execution with no skills, PreSkill show skill authoring before execution, PostSkill show first run, first_run_context.json, skill summary, second run. Use minimal readable labels, thin arrows, muted blue/green/orange accents, no decorative 3D, no fake numeric results.
```

## Fig. 2: Three-Mode Evaluation Protocol

```text
Draw a scientific workflow diagram comparing three EvoClawBench modes in horizontal swimlanes. Lane 1 Baseline: fresh workspace -> task execution -> grading, with a lock icon "skill creation forbidden". Lane 2 PreSkill: skill-creator seeded workspace -> generated SKILL.md -> copied into fresh workspace -> execution with skills -> grading -> before/after skill hash check. Lane 3 PostSkill: no-skill first execution -> grading and transcript summary -> first_run_context.json -> generated reusable SKILL.md -> copied into fresh workspace -> second execution -> grading -> mutation check. Clean vector style, English labels, paper-ready, white background, consistent arrows, no result numbers.
```

## Fig. 3: Task Suite Taxonomy / Repeated Sub-Problems

```text
Create a compact academic taxonomy figure for EvoClawBench task suite. Center title "Repeated Tool-Using Tasks". Around it group task categories as small labeled clusters: data transformation, log analysis, API scaffolding, test generation, config migration, security review, document extraction, database operations, Excel analytics, web extraction, document generation, data pipelines, email processing, invoice processing, shell automation, CI generation, dependency audit, environment config, metrics anomaly detection. Show each task as "5-10 related sub-problems" flowing from input fixtures to artifact outputs to automated or hybrid graders. Use a restrained scientific vector style, readable labels, no fake counts except "21 tasks" only if final count is confirmed.
```

## Fig. 4: Failure Case / Context Interference

```text
Create a qualitative academic failure-case diagram for EvoClawBench. Show PostSkill first run evidence on the left: prompt, output preview, transcript summary, grading details. Arrow to a generated SKILL.md in the middle that accidentally overfits file names, fixture-specific assumptions, or previous solution steps. Arrow to second execution on the right where prompt evidence and generated skill conflict, causing wrong outputs or lower score. Add callouts: "over-specific memory", "context interference", "transfer risk". Vector style, white background, minimal text, no cartoon elements, no fake task names.
```

## Appendix: Skill Artifact Anatomy

```text
Draw a small technical anatomy diagram of an agent skill package used by EvoClawBench. Show a folder named skills/<skill-name>/ containing SKILL.md with YAML frontmatter fields name and description, optional scripts/, optional references/. Show the package being loaded into an agent context during PreSkill or PostSkill reuse. Clean vector style, minimal labels, suitable for appendix, no implementation-specific fake paths.
```
