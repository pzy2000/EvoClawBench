---
name: facilities-maintenance-hardmode
description: Solve facilities maintenance prioritization fixtures that use the evoclawbench hard-mode evidence protocol. Use this whenever a task asks you to derive `priority_assets`, `maintenance_due`, `anomaly_ids`, `diagnostic_codes`, or `dispatch_required` from packet manifests plus records, especially when fixtures may be JSON, YAML, CSV, JSONL text, or HTML with embedded JSON and the instructions mention approved packets, supersession checks, checksum validation, revision-ordered list actions, boolean gates, or channel maps.
---

# Facilities Maintenance Hard-Mode

Use this skill for facilities maintenance prioritization cases that hide the real answer behind packet selection and channel-specific reduction rules.

## Goal
Convert each fixture into one JSON report with exactly these fields:
- `priority_assets`
- `maintenance_due`
- `anomaly_ids`
- `diagnostic_codes`
- `dispatch_required`

The channel map is normally:
- `L1` -> `priority_assets`
- `L2` -> `maintenance_due`
- `L3` -> `anomaly_ids`
- `L4` -> `diagnostic_codes`
- `B1` -> `dispatch_required`

Always prefer the fixture's own `channel_map` if present.

## Procedure

1. Load the fixture according to its container format.
2. Read `packet_manifest` and `records`.
3. Select the one valid packet:
   - `state == approved`
   - `superseded_by` is empty
   - checksum equals the first 16 hex chars of:
     `sha256("evoclawbench-difficulty-hardening-20260524-v4|<task_id>|<case_id>|<packet_id>|<nonce>")`
   - if multiple packets remain, choose highest `revision`, then highest `source_weight`, then lowest `packet_id`
4. Keep only records whose `packet_id` matches the selected packet and whose `status == final`.
5. Reduce records by channel and record kind:
   - **List channels**: apply `list_action` rows in ascending revision order; preserve action effects across rows, then emit sorted unique strings.
     - `include`: add `value`
     - `remove`: remove `target` if present, otherwise `value`
     - `alias`: replace `target` with `value`
   - **Boolean channels**: emit `true` only if every selected `boolean_gate` row has `observed == expected`.
6. Write output JSON with exactly the required five fields and no extras.

## Format loaders

### JSON / YAML
Use top-level `packet_manifest` and `records`.

### CSV
Rows are partitioned by `section`:
- `section=manifest` => packet manifest rows
- `section=record` => evidence record rows
- `section=protocol` may exist; ignore unless you need metadata

If complex cells contain JSON strings, parse them before reduction.

### Text / JSONL
Read line by line:
- `MANIFEST` lines contain JSON payloads for manifest entries
- `RECORD` lines contain JSON payloads for records

### HTML
Extract JSON from:
- `<script type="application/json" data-section="manifest">...</script>`
- `<script type="application/json" data-section="records">...</script>`

## Guardrails

- Never copy from draft packets.
- Never use packets with bad checksums.
- Never use records from superseded or unselected packets.
- Never include draft records.
- Do not infer missing values from decoys.
- Sort final list outputs lexicographically.
- Keep `dispatch_required` as a JSON boolean, not a string.

## Reusable implementation note
If many cases must be solved quickly, script it. A deterministic parser is safer and faster than hand-extracting every record.
