---
name: crm-pipeline-hygiene-hardmode
description: Derive strict JSON CRM pipeline hygiene reports from evidence packets and mixed-format fixtures. Use when a task mentions packet_manifest and records, approved versus superseded packets, checksum validation, CSV/JSON/YAML/text/HTML fixtures, channel maps, stale opportunities, forecast deltas, campaign errors, action items, executive summaries, or a short-SLA batch of case_XX fixtures that must be solved deterministically in one reusable pass.
---

# CRM Pipeline Hygiene Hard Mode

Use this skill to solve fixture-backed CRM hygiene tasks that hide decoy packets, draft rows, superseded packets, and invalid checksums.

## Do this first

1. Read the task-specific schema and channel map.
2. Parse each fixture into two collections only:
   - `packet_manifest`
   - `records`
3. Select exactly one eligible packet.
4. Keep only `final` records from that selected packet.
5. Reduce channels by type.
6. Emit only the required JSON fields.

For multi-case batches, prefer the bundled script instead of manual extraction.

## Supported fixture formats

- **CSV**: use rows where `section=manifest` and `section=record`; ignore `section=protocol` except as metadata.
- **JSON/YAML**: read `packet_manifest` and `records` directly.
- **Text**: parse `MANIFEST {json}` and `RECORD {json}` lines.
- **HTML**: extract JSON from `<script type="application/json" data-section="...">` blocks.

## Packet selection rule

A packet is eligible only if all conditions hold:

- `state == "approved"`
- `superseded_by` is empty or null
- `checksum == sha256("evoclawbench-difficulty-hardening-20260524-v4|<task_id>|<case_id>|<packet_id>|<nonce>")[:16]`

If multiple packets remain, choose in this order:

1. highest `revision`
2. highest `source_weight`
3. lowest `packet_id`

Never use rows from unselected, superseded, draft, or invalid-checksum packets.

## Record filter

After packet selection, keep only records where:

- `packet_id` equals the selected packet id
- `status == "final"`

## Reducers by channel type

### Numeric

For each `numeric_delta` row:

- compute `amount_minor / scale`
- negate it if `operator == "subtract"`
- sum contributions
- emit integers only for count-like fields
- otherwise round to two decimals

### List

Apply `list_action` rows in revision order, using source order as a stable tiebreaker:

- `include`: add `value`
- `remove`: remove `target`, else `value`
- `alias`: replace `target` with `value`

Emit sorted unique strings.

### Dict

Sum `dict_delta.delta` by `bucket` and omit zero-valued buckets.

### Boolean

Emit `true` only if every `boolean_gate` row has `observed == expected`.

### Text

Choose the `text_candidate` with the largest `score - penalty`.
Break ties by lexicographically smallest `candidate`.
Emit the chosen candidate exactly.

## Output discipline

Emit valid JSON with exactly the required fields and nothing extra.
Do not include helper metadata, packet ids, notes, or provenance unless the task explicitly asks.

Example fixed schema:

```json
{
  "stale_opportunities": [],
  "forecast_delta": 0,
  "campaign_errors": [],
  "action_items": [],
  "executive_summary": ""
}
```

## Bundled deterministic solver

Use `scripts/crm_pipeline_hygiene.py` for batch execution.

Example:

```bash
python3 skills/crm-pipeline-hygiene-hardmode/scripts/crm_pipeline_hygiene.py \
  assets/generated_tasks/task_92_crm_pipeline_hygiene \
  outputs \
  --summary
```

Optional override if the task id used in checksums differs from the input directory name:

```bash
python3 skills/crm-pipeline-hygiene-hardmode/scripts/crm_pipeline_hygiene.py \
  <input-dir> <output-dir> --task-id task_92_crm_pipeline_hygiene
```

## Quality checks

Before finishing, verify all of these:

- every expected `case_XX_report.json` exists
- each output parses as JSON
- each output has exactly the required keys
- lists are sorted and unique
- text came from max `score - penalty`
- no draft or foreign-packet rows leaked in
- checksums were validated, not assumed

## Common failure modes

- selecting an approved packet without checksum validation
- failing to reject approved-but-superseded packets
- mixing rows from multiple packets
- keeping selected-packet rows whose status is not `final`
- applying list actions without revision ordering
- choosing text by raw score instead of `score - penalty`
- emitting extra fields outside the strict schema
