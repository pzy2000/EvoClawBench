---
name: crm-pipeline-hygiene-hardmode
description: Derive strict JSON CRM pipeline hygiene reports from fixture-backed evidence packets, especially when the task mentions packet_manifest/records, approved vs superseded packets, checksum validation, mixed fixture formats (CSV/JSON/YAML/text/HTML), channel maps, stale opportunities, forecast deltas, campaign errors, action items, or executive summaries. Use this skill whenever a task requires selecting the one valid evidence packet and aggregating channels into a fixed report schema across one or more cases.
---

# CRM Pipeline Hygiene Hard Mode

Use this skill for evidence-driven CRM hygiene batch tasks where fixtures contain multiple competing packets, decoys, stale revisions, and explicit derivation rules.

## Goal

Turn each fixture into one strict JSON report by:
1. parsing the fixture format,
2. selecting the one valid packet,
3. ignoring every other packet,
4. aggregating only final records from that packet,
5. mapping channels into the required output fields.

## Fast path

For short-SLA batch work, do one reusable pass:
- inspect one or two fixtures just enough to confirm the schema,
- write a small deterministic parser if more than one case exists,
- run it across the whole batch,
- spot-check outputs against the protocol before finishing.

## Supported fixture shapes

### CSV
- `section=manifest` rows are packet manifest entries.
- `section=record` rows are evidence records.
- `section=protocol` is metadata only.

### JSON/YAML
- Read `packet_manifest` and `records` directly.

### Text
- Parse JSON lines tagged as `MANIFEST` and `RECORD`.

### HTML
- Extract JSON from `<script type="application/json" data-section="...">` blocks.

## Packet selection protocol

Given task id, case id, packet id, and nonce, compute:

`sha256("evoclawbench-difficulty-hardening-20260524-v4|<task_id>|<case_id>|<packet_id>|<nonce>")[:16]`

A packet is eligible only if all are true:
- `state == "approved"`
- `superseded_by` is empty / null
- checksum matches the computed 16-char prefix

If multiple eligible packets remain, choose:
1. highest `revision`
2. then highest `source_weight`
3. then lowest `packet_id` lexicographically

Do not use any data from draft, superseded, invalid-checksum, or otherwise unselected packets.

## Record filtering

After selecting the packet, keep only records where:
- `packet_id` equals the selected packet id
- `status == "final"`

Ignore draft or non-final records even if they belong to the selected packet.

## Channel derivation rules

### Numeric channels
For `numeric_delta` rows:
- value contribution = `amount_minor / scale`
- if `operator == "subtract"`, negate the contribution
- otherwise add it
- if the field is count-like, emit an integer
- otherwise round to 2 decimals

### List channels
For `list_action` rows, process in revision order using the record sequence as a stable tiebreaker.
- `include`: add `value`
- `remove`: remove `target` if present, otherwise remove `value`
- `alias`: replace `target` with `value`

Emit sorted unique strings.

Practical rule: keep a set/list state, apply actions in order, then sort at the end.

### Dict channels
For `dict_delta` rows:
- sum `dict_delta.delta` by `bucket`
- omit zero-valued buckets from output

### Boolean channels
Emit `true` only if every selected `boolean_gate` row has `observed == expected`.
Otherwise emit `false`.

### Text channels
For `text_candidate` rows:
- compute `score - penalty`
- choose the largest value
- if tied, choose the lexicographically smallest `candidate`
- emit the chosen candidate string exactly

## Output discipline

When the task gives a fixed schema, honor it exactly.
Do not add helper fields, comments, provenance, or debugging notes.

If the channel map is:
- `L1 -> stale_opportunities`
- `N1 -> forecast_delta`
- `L2 -> campaign_errors`
- `L3 -> action_items`
- `T1 -> executive_summary`

then output exactly:

```json
{
  "stale_opportunities": [],
  "forecast_delta": 0,
  "campaign_errors": [],
  "action_items": [],
  "executive_summary": ""
}
```

## Recommended implementation pattern

1. Parse fixture into `packet_manifest` and `records`.
2. Compute valid packets via checksum function.
3. Select the winning packet with the sort rule.
4. Filter records to selected packet + `status=final`.
5. Group by channel.
6. Apply channel-specific reducers.
7. Map channels to the output field names.
8. Save one JSON file per case.

## Quality checks

Before finishing, verify:
- every output file exists,
- every report is valid JSON,
- only required fields are present,
- numeric rounding matches the protocol,
- list outputs are sorted and unique,
- text choice used `score - penalty`, not raw score,
- no decoy packet values leaked in.

## Common failure modes

- Trusting the visually nicest packet instead of validating checksum.
- Forgetting to reject approved-but-invalid-checksum packets.
- Mixing records from multiple packets.
- Keeping draft rows.
- Summing numeric deltas without applying `subtract`.
- Forgetting final sorted uniqueness for lists.
- Choosing text by highest score instead of highest `score - penalty`.
- Emitting extra metadata fields.

## When batching many cases

Prefer a small script over manual extraction. These fixtures are designed to reward deterministic processing and punish eyeballing.
