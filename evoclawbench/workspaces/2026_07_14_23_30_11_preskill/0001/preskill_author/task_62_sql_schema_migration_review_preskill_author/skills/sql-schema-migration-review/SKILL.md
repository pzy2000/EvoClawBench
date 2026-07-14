---
name: sql-schema-migration-review
description: Review hard-mode SQL schema migration evidence fixtures and produce strict JSON reports with fields row_count, quality_failures, metric_delta, rule_ids, experiment_winner. Use when fixtures may be CSV, JSON, YAML, JSONL/text, or HTML and the task requires selecting the valid approved packet by checksum/revision/source_weight rules, filtering final records, applying numeric/list/dict/boolean/text evidence protocols, and writing one report per case quickly in a batch.
---

# SQL Schema Migration Review

Use the bundled solver for this task family.

## Files and outputs

- Input fixtures usually live under `assets/generated_tasks/<task_id>/`, but callers can pass any directory with case files via `--input-dir`.
- Output files should be `outputs/<case_id>_report.json` unless the user explicitly asks for a different target.
- Never modify fixtures.

## Fast path

Run:

```bash
python3 skills/sql-schema-migration-review/scripts/solve_batch.py \
  --input-dir assets/generated_tasks/task_62_sql_schema_migration_review \
  --output-dir outputs
```

Add `--dry-run` to print JSON instead of writing files.

## Protocol to implement

1. Parse fixture format.
   - JSON/YAML: read `packet_manifest` and `records`.
   - CSV: rows with `section=manifest` and `section=record`; ignore optional `section=protocol` metadata rows.
   - Text/JSONL: lines whose first token is `MANIFEST` or `RECORD`, followed by JSON.
   - HTML: extract JSON from `<script type="application/json" data-section="manifest">` and `<script type="application/json" data-section="records">` blocks.
2. Select candidate packets from `packet_manifest` where:
   - `state == approved`
   - `superseded_by` is empty/null
   - checksum equals the first 16 hex chars of:
     `sha256("evoclawbench-difficulty-hardening-20260524-v4|<task_id>|<case_id>|<packet_id>|<nonce>")`
3. If more than one packet remains, choose:
   - highest `revision`
   - then highest `source_weight`
   - then lowest `packet_id` lexicographically
4. Keep only `records` where:
   - `packet_id` equals the selected packet
   - `status == final`
5. Channel handling:
   - Numeric: sum signed `amount_minor / scale`; negate rows with `operator=subtract`.
   - Count-like fields must be integers.
   - Non-count numeric outputs round to 2 decimals.
   - Lists: process in revision order if a per-record revision exists, otherwise preserve file order. `include` adds `value`; `remove` removes `target` or `value`; `alias` replaces `target` with `value`. Emit sorted unique strings.
   - Dicts: sum `dict_delta.delta` by `bucket`; omit zero buckets.
   - Booleans: `true` only if every selected `boolean_gate` has `observed == expected`.
   - Text: choose candidate with max `score - penalty`; break ties by lexicographically smallest `candidate` and emit exact text.
6. Map channels to report fields:
   - `N1 -> row_count`
   - `L1 -> quality_failures`
   - `N2 -> metric_delta`
   - `L2 -> rule_ids`
   - `T1 -> experiment_winner`

## Output contract

Write JSON objects with exactly these keys:

```json
{
  "row_count": 0,
  "quality_failures": [],
  "metric_delta": 0.0,
  "rule_ids": [],
  "experiment_winner": ""
}
```

No extra fields. Keep JSON valid.

## Sanity checks

Before trusting results, verify:

- selected packet is not superseded
- selected packet checksum validates
- no draft/unselected packet records leaked in
- `row_count` is integer-valued
- list outputs are sorted unique strings
- report keys are exact and complete

## When not to use the script

Only skip the script if the environment lacks Python 3 or the fixture shape is clearly outside this protocol. Otherwise prefer the script for consistency and speed.
