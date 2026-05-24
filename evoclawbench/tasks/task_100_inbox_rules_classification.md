---
id: task_100_inbox_rules_classification
name: Inbox Rules Classification
category: office_operations
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: travel_office
task_family: Travel/Office
grader_family: travel_office
workspace_files:
  - assets/generated_tasks/task_100_inbox_rules_classification/case_01.json
  - assets/generated_tasks/task_100_inbox_rules_classification/case_02.json
  - assets/generated_tasks/task_100_inbox_rules_classification/case_03.json
  - assets/generated_tasks/task_100_inbox_rules_classification/case_04.json
  - assets/generated_tasks/task_100_inbox_rules_classification/case_05.json
---

# Inbox Rules Classification

Process five hard-mode fixture-backed travel/office cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode inbox rules classification fixture files under `assets/generated_tasks/task_100_inbox_rules_classification/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `conflicts`, `exceptions`, `action_items`, `rule_labels`, `resolved`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `conflicts` (list)
- `L2` -> `exceptions` (list)
- `L3` -> `action_items` (list)
- `L4` -> `rule_labels` (list)
- `B1` -> `resolved` (bool)

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
- Input: `assets/generated_tasks/task_100_inbox_rules_classification/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive conflicts, exceptions, action_items, rule_labels, resolved for this travel/office case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_100_inbox_rules_classification/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive conflicts, exceptions, action_items, rule_labels, resolved for this travel/office case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_100_inbox_rules_classification/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive conflicts, exceptions, action_items, rule_labels, resolved for this travel/office case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_100_inbox_rules_classification/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive conflicts, exceptions, action_items, rule_labels, resolved for this travel/office case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_100_inbox_rules_classification/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive conflicts, exceptions, action_items, rule_labels, resolved for this travel/office case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `conflicts` with the correctly derived value.
- [ ] Each report includes `exceptions` with the correctly derived value.
- [ ] Each report includes `action_items` with the correctly derived value.
- [ ] Each report includes `rule_labels` with the correctly derived value.
- [ ] Each report includes `resolved` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'action_items': ['ACTITE-01-30', 'ACTITE-01-46', 'ACTITE-01-49', 'ACTITE-01-56'],
             'conflicts': ['CON-01-26', 'CON-01-52', 'CON-01-60', 'CON-01-90'],
             'exceptions': ['EXC-01-14', 'EXC-01-39', 'EXC-01-47', 'EXC-01-53'],
             'resolved': True,
             'rule_labels': ['RULLAB-01-32', 'RULLAB-01-46', 'RULLAB-01-55', 'RULLAB-01-96']},
 'case_02': {'action_items': ['ACTITE-02-30', 'ACTITE-02-46', 'ACTITE-02-49', 'ACTITE-02-56'],
             'conflicts': ['CON-02-26', 'CON-02-52', 'CON-02-60', 'CON-02-90'],
             'exceptions': ['EXC-02-14', 'EXC-02-39', 'EXC-02-47', 'EXC-02-53'],
             'resolved': False,
             'rule_labels': ['RULLAB-02-32', 'RULLAB-02-46', 'RULLAB-02-55', 'RULLAB-02-96']},
 'case_03': {'action_items': ['ACTITE-03-30', 'ACTITE-03-46', 'ACTITE-03-49', 'ACTITE-03-56'],
             'conflicts': ['CON-03-26', 'CON-03-52', 'CON-03-60', 'CON-03-90'],
             'exceptions': ['EXC-03-14', 'EXC-03-39', 'EXC-03-47', 'EXC-03-53'],
             'resolved': True,
             'rule_labels': ['RULLAB-03-32', 'RULLAB-03-46', 'RULLAB-03-55', 'RULLAB-03-96']},
 'case_04': {'action_items': ['ACTITE-04-30', 'ACTITE-04-46', 'ACTITE-04-49', 'ACTITE-04-56'],
             'conflicts': ['CON-04-26', 'CON-04-52', 'CON-04-60', 'CON-04-90'],
             'exceptions': ['EXC-04-14', 'EXC-04-39', 'EXC-04-47', 'EXC-04-53'],
             'resolved': True,
             'rule_labels': ['RULLAB-04-32', 'RULLAB-04-46', 'RULLAB-04-55', 'RULLAB-04-96']},
 'case_05': {'action_items': ['ACTITE-05-30', 'ACTITE-05-46', 'ACTITE-05-49', 'ACTITE-05-56'],
             'conflicts': ['CON-05-26', 'CON-05-52', 'CON-05-60', 'CON-05-90'],
             'exceptions': ['EXC-05-14', 'EXC-05-39', 'EXC-05-47', 'EXC-05-53'],
             'resolved': False,
             'rule_labels': ['RULLAB-05-32', 'RULLAB-05-46', 'RULLAB-05-55', 'RULLAB-05-96']}}
    required_fields = ['conflicts', 'exceptions', 'action_items', 'rule_labels', 'resolved']
    numeric_fields = []
    list_fields = ['conflicts', 'exceptions', 'action_items', 'rule_labels']
    dict_fields = []
    bool_fields = ['resolved']
    text_fields = []
    family_marker = "travel_office_grader"
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
