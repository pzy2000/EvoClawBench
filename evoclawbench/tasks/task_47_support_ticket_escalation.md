---
id: task_47_support_ticket_escalation
name: Support Ticket Escalation
category: support_product
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: support_product
task_family: Support/Product
grader_family: support_product
workspace_files:
  - assets/generated_tasks/task_47_support_ticket_escalation/case_01.json
  - assets/generated_tasks/task_47_support_ticket_escalation/case_02.json
  - assets/generated_tasks/task_47_support_ticket_escalation/case_03.json
  - assets/generated_tasks/task_47_support_ticket_escalation/case_04.json
  - assets/generated_tasks/task_47_support_ticket_escalation/case_05.json
---

# Support Ticket Escalation

Process five hard-mode fixture-backed support/product cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode support ticket escalation fixture files under `assets/generated_tasks/task_47_support_ticket_escalation/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `priority_queue`, `duplicate_groups`, `themes`, `sla_breaches`, `reply_template`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `priority_queue` (list)
- `L2` -> `duplicate_groups` (list)
- `L3` -> `themes` (list)
- `L4` -> `sla_breaches` (list)
- `T1` -> `reply_template` (text)

Hard-mode evidence protocol:
0. JSON/YAML fixtures expose `packet_manifest` and `records` directly; CSV fixtures use
`section=manifest` and `section=record` rows and may include a metadata `section=protocol` row;
text fixtures use `MANIFEST`/`RECORD` JSON lines;
HTML fixtures store JSON in `<script type="application/json" data-section="...">` blocks.
1. Identify the selected packet from `packet_manifest`. Use only packets with `state=approved`, no `superseded_by`, and a valid checksum equal to the first 16 hex characters of `sha256("evoclawbench-difficulty-hardening-20260524-v4|<task_id>|<case_id>|<packet_id>|<nonce>")`. If more than one packet remains, choose the highest `revision`, then highest `source_weight`, then lowest `packet_id`.
2. Use only `records` whose `packet_id` is the selected packet and whose `status` is `final`.
3. Numeric channels: apply each `numeric_delta` as signed `amount_minor / scale`, subtracting rows whose `operator` is `subtract`; count-like fields must be integers, other numeric fields must be rounded to two decimals.
4. List channels: apply `list_action` rows in revision order. `include` adds `value`, `remove` removes `target` or `value`, and `alias` replaces `target` with `value`. Emit sorted unique strings.
5. Dict channels: sum `dict_delta.delta` by `bucket` and omit zero-valued buckets.
6. Boolean channels: emit `true` only if every selected `boolean_gate` has `observed` equal to `expected`.
7. Text channels: choose the `text_candidate` with the largest `score - penalty`; break ties by the lexicographically smallest candidate string and emit the candidate exactly.

Do not copy values from unselected, draft, superseded, invalid-checksum, or decoy packets. Do not modify the input fixtures; only write files under `outputs/`.

---

## Expected Behavior

1. Parse each fixture format into packet manifest rows and evidence records.
2. Validate packet checksums and discard draft, superseded, invalid, and decoy packets before aggregation.
3. Apply the channel-specific derivation rules for numeric, list, dict, boolean, and text outputs.
4. Write one strict JSON report per case under `outputs/`, preserving the required schema exactly.
5. Recheck all five reports against the selected-packet evidence rather than trusting visible decoys.

---

## Sub-Problems

### Sub-Problem 1: North Region Batch
- Input: `assets/generated_tasks/task_47_support_ticket_escalation/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_47_support_ticket_escalation/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_47_support_ticket_escalation/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_47_support_ticket_escalation/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_47_support_ticket_escalation/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `priority_queue` with the correctly derived value.
- [ ] Each report includes `duplicate_groups` with the correctly derived value.
- [ ] Each report includes `themes` with the correctly derived value.
- [ ] Each report includes `sla_breaches` with the correctly derived value.
- [ ] Each report includes `reply_template` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'duplicate_groups': ['DUPGRO-01-33',
                                  'DUPGRO-01-41',
                                  'DUPGRO-01-64',
                                  'DUPGRO-01-95'],
             'priority_queue': ['PRIQUE-01-33', 'PRIQUE-01-59', 'PRIQUE-01-61', 'PRIQUE-01-81'],
             'reply_template': 'policy_clarification',
             'sla_breaches': ['SLABRE-01-102', 'SLABRE-01-49', 'SLABRE-01-73', 'SLABRE-01-78'],
             'themes': ['THE-01-49', 'THE-01-56', 'THE-01-68', 'THE-01-78']},
 'case_02': {'duplicate_groups': ['DUPGRO-02-33',
                                  'DUPGRO-02-41',
                                  'DUPGRO-02-64',
                                  'DUPGRO-02-95'],
             'priority_queue': ['PRIQUE-02-33', 'PRIQUE-02-59', 'PRIQUE-02-61', 'PRIQUE-02-81'],
             'reply_template': 'technical_escalation',
             'sla_breaches': ['SLABRE-02-102', 'SLABRE-02-49', 'SLABRE-02-73', 'SLABRE-02-78'],
             'themes': ['THE-02-49', 'THE-02-56', 'THE-02-68', 'THE-02-78']},
 'case_03': {'duplicate_groups': ['DUPGRO-03-33',
                                  'DUPGRO-03-41',
                                  'DUPGRO-03-64',
                                  'DUPGRO-03-95'],
             'priority_queue': ['PRIQUE-03-33', 'PRIQUE-03-59', 'PRIQUE-03-61', 'PRIQUE-03-81'],
             'reply_template': 'technical_escalation',
             'sla_breaches': ['SLABRE-03-102', 'SLABRE-03-49', 'SLABRE-03-73', 'SLABRE-03-78'],
             'themes': ['THE-03-49', 'THE-03-56', 'THE-03-68', 'THE-03-78']},
 'case_04': {'duplicate_groups': ['DUPGRO-04-33',
                                  'DUPGRO-04-41',
                                  'DUPGRO-04-64',
                                  'DUPGRO-04-95'],
             'priority_queue': ['PRIQUE-04-33', 'PRIQUE-04-59', 'PRIQUE-04-61', 'PRIQUE-04-81'],
             'reply_template': 'apology_credit',
             'sla_breaches': ['SLABRE-04-102', 'SLABRE-04-49', 'SLABRE-04-73', 'SLABRE-04-78'],
             'themes': ['THE-04-49', 'THE-04-56', 'THE-04-68', 'THE-04-78']},
 'case_05': {'duplicate_groups': ['DUPGRO-05-33',
                                  'DUPGRO-05-41',
                                  'DUPGRO-05-64',
                                  'DUPGRO-05-95'],
             'priority_queue': ['PRIQUE-05-33', 'PRIQUE-05-59', 'PRIQUE-05-61', 'PRIQUE-05-81'],
             'reply_template': 'apology_credit',
             'sla_breaches': ['SLABRE-05-102', 'SLABRE-05-49', 'SLABRE-05-73', 'SLABRE-05-78'],
             'themes': ['THE-05-49', 'THE-05-56', 'THE-05-68', 'THE-05-78']}}
    required_fields = ['priority_queue', 'duplicate_groups', 'themes', 'sla_breaches', 'reply_template']
    numeric_fields = []
    list_fields = ['priority_queue', 'duplicate_groups', 'themes', 'sla_breaches']
    dict_fields = []
    bool_fields = []
    text_fields = ['reply_template']
    family_marker = "support_product_grader"
    scores = {}

    def load_report(path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    def normalize_list(value):
        if not isinstance(value, list):
            return []
        normalized = []
        for item in value:
            if isinstance(item, list):
                normalized.append(tuple(str(part) for part in item))
            else:
                normalized.append(str(item))
        return sorted(normalized, key=str)

    def normalize_dict(value):
        if not isinstance(value, dict):
            return {}
        normalized = {}
        for key, item in value.items():
            normalized[str(key)] = round(item, 4) if isinstance(item, float) else item
        return normalized

    def compare(field, actual, wanted):
        if field in numeric_fields:
            return isinstance(actual, (int, float)) and math.isclose(
                float(actual), float(wanted), rel_tol=1e-4, abs_tol=1e-4
            )
        if field in list_fields:
            return normalize_list(actual) == normalize_list(wanted)
        if field in dict_fields:
            return normalize_dict(actual) == normalize_dict(wanted)
        if field in bool_fields:
            return isinstance(actual, bool) and actual is bool(wanted)
        if field in text_fields:
            return str(actual).strip().lower() == str(wanted).strip().lower()
        return actual == wanted

    for case_id, wanted in expected.items():
        prefix = case_id.replace("case_", "sub_")
        report_path = output_dir / f"{case_id}_report.json"
        exists = report_path.is_file()
        scores[f"{prefix}_{family_marker}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for field in required_fields:
                scores[f"{prefix}_field_{field}"] = 0.0
            continue
        data = load_report(report_path)
        if data is None:
            scores[f"{prefix}_{family_marker}_valid_json"] = 0.0
            for field in required_fields:
                scores[f"{prefix}_field_{field}"] = 0.0
            continue
        scores[f"{prefix}_{family_marker}_valid_json"] = 1.0
        scores[f"{prefix}_{family_marker}_required_fields"] = (
            1.0 if all(field in data for field in required_fields) else 0.0
        )
        for field, wanted_value in wanted.items():
            scores[f"{prefix}_field_{field}"] = (
                1.0 if compare(field, data.get(field), wanted_value) else 0.0
            )
    return scores
```
