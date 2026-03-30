## Evolution Guardrails A/B Test

This repository uses a prompt prefix in [`evoclawbench/scripts/lib_agent.py`](../scripts/lib_agent.py) to switch between Baseline and Evolution modes.

We added Evolution guardrails to reduce regressions observed in:
`task_02_log_analysis`, `task_03_api_scaffold`, `task_09_excel_analytics`.

This doc describes how to run an A/B comparison and what “success” means.

## Variants

### Variant A (control)
Evolution mode with the original, minimal Evolution prefix only.

Enable by setting:

```bash
export EVOLAW_DISABLE_EVOLUTION_GUARDRAILS=1
```

### Variant B (treatment)
Evolution mode with guardrails and mandatory self-check checklist (default).

Enable by unsetting or setting:

```bash
unset EVOLAW_DISABLE_EVOLUTION_GUARDRAILS
```

## Recommended Runs

Use the same model and runtime for both variants.

Run a small suite that includes the regression tasks:

```bash
uv run scripts/benchmark.py --runtime openclaw --mode evolution --suite task_02_log_analysis,task_03_api_scaffold,task_09_excel_analytics --runs 3
```

If you want full-suite validation:

```bash
uv run scripts/benchmark.py --runtime openclaw --mode both --runs 3
```

## Acceptance Criteria (practical)

### Must-have
- `task_09_excel_analytics` Evolution **mean_score > 0.0** (files are produced, no early-stop zero output)
- `task_03_api_scaffold` Evolution improves the two missing dimensions:
  - `error_handling` becomes non-zero for most subproblems
  - `retry` becomes non-zero for most subproblems

### Nice-to-have
- Overall `fail2pass` improves versus Variant A
- No statistically meaningful regressions in tasks that were already perfect in Evolution

## Notes
- Guardrails are prompt-only. They do not change graders or task files.
- If Variant B improves `task_03` and `task_09` but hurts efficiency, consider tightening the checklist wording rather than removing it.

