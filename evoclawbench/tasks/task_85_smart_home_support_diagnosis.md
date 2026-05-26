---
id: task_85_smart_home_support_diagnosis
name: Smart Home Support Diagnosis
category: facilities_iot
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: facilities_iot
task_family: Facilities/IoT
grader_family: facilities_iot
workspace_files:
  - assets/generated_tasks/task_85_smart_home_support_diagnosis/case_01.json
  - assets/generated_tasks/task_85_smart_home_support_diagnosis/case_02.json
  - assets/generated_tasks/task_85_smart_home_support_diagnosis/case_03.json
  - assets/generated_tasks/task_85_smart_home_support_diagnosis/case_04.json
  - assets/generated_tasks/task_85_smart_home_support_diagnosis/case_05.json
---

# Smart Home Support Diagnosis

Process five hard-mode fixture-backed facilities/iot cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode smart home support diagnosis fixture files under `assets/generated_tasks/task_85_smart_home_support_diagnosis/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `priority_assets`, `maintenance_due`, `anomaly_ids`, `diagnostic_codes`, `dispatch_required`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `priority_assets` (list)
- `L2` -> `maintenance_due` (list)
- `L3` -> `anomaly_ids` (list)
- `L4` -> `diagnostic_codes` (list)
- `B1` -> `dispatch_required` (bool)

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
- Input: `assets/generated_tasks/task_85_smart_home_support_diagnosis/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required for this facilities/iot case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_85_smart_home_support_diagnosis/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required for this facilities/iot case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_85_smart_home_support_diagnosis/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required for this facilities/iot case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_85_smart_home_support_diagnosis/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required for this facilities/iot case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_85_smart_home_support_diagnosis/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required for this facilities/iot case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `priority_assets` with the correctly derived value.
- [ ] Each report includes `maintenance_due` with the correctly derived value.
- [ ] Each report includes `anomaly_ids` with the correctly derived value.
- [ ] Each report includes `diagnostic_codes` with the correctly derived value.
- [ ] Each report includes `dispatch_required` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'anomaly_ids': ['ANOIDS-01-26', 'ANOIDS-01-41', 'ANOIDS-01-57', 'ANOIDS-01-78'],
             'diagnostic_codes': ['DIACOD-01-11',
                                  'DIACOD-01-21',
                                  'DIACOD-01-61',
                                  'DIACOD-01-90'],
             'dispatch_required': True,
             'maintenance_due': ['MAIDUE-01-28',
                                 'MAIDUE-01-41',
                                 'MAIDUE-01-74',
                                 'MAIDUE-01-86'],
             'priority_assets': ['PRIASS-01-13',
                                 'PRIASS-01-22',
                                 'PRIASS-01-52',
                                 'PRIASS-01-70']},
 'case_02': {'anomaly_ids': ['ANOIDS-02-26', 'ANOIDS-02-41', 'ANOIDS-02-57', 'ANOIDS-02-78'],
             'diagnostic_codes': ['DIACOD-02-11',
                                  'DIACOD-02-21',
                                  'DIACOD-02-61',
                                  'DIACOD-02-90'],
             'dispatch_required': False,
             'maintenance_due': ['MAIDUE-02-28',
                                 'MAIDUE-02-41',
                                 'MAIDUE-02-74',
                                 'MAIDUE-02-86'],
             'priority_assets': ['PRIASS-02-13',
                                 'PRIASS-02-22',
                                 'PRIASS-02-52',
                                 'PRIASS-02-70']},
 'case_03': {'anomaly_ids': ['ANOIDS-03-26', 'ANOIDS-03-41', 'ANOIDS-03-57', 'ANOIDS-03-78'],
             'diagnostic_codes': ['DIACOD-03-11',
                                  'DIACOD-03-21',
                                  'DIACOD-03-61',
                                  'DIACOD-03-90'],
             'dispatch_required': True,
             'maintenance_due': ['MAIDUE-03-28',
                                 'MAIDUE-03-41',
                                 'MAIDUE-03-74',
                                 'MAIDUE-03-86'],
             'priority_assets': ['PRIASS-03-13',
                                 'PRIASS-03-22',
                                 'PRIASS-03-52',
                                 'PRIASS-03-70']},
 'case_04': {'anomaly_ids': ['ANOIDS-04-26', 'ANOIDS-04-41', 'ANOIDS-04-57', 'ANOIDS-04-78'],
             'diagnostic_codes': ['DIACOD-04-11',
                                  'DIACOD-04-21',
                                  'DIACOD-04-61',
                                  'DIACOD-04-90'],
             'dispatch_required': False,
             'maintenance_due': ['MAIDUE-04-28',
                                 'MAIDUE-04-41',
                                 'MAIDUE-04-74',
                                 'MAIDUE-04-86'],
             'priority_assets': ['PRIASS-04-13',
                                 'PRIASS-04-22',
                                 'PRIASS-04-52',
                                 'PRIASS-04-70']},
 'case_05': {'anomaly_ids': ['ANOIDS-05-26', 'ANOIDS-05-41', 'ANOIDS-05-57', 'ANOIDS-05-78'],
             'diagnostic_codes': ['DIACOD-05-11',
                                  'DIACOD-05-21',
                                  'DIACOD-05-61',
                                  'DIACOD-05-90'],
             'dispatch_required': False,
             'maintenance_due': ['MAIDUE-05-28',
                                 'MAIDUE-05-41',
                                 'MAIDUE-05-74',
                                 'MAIDUE-05-86'],
             'priority_assets': ['PRIASS-05-13',
                                 'PRIASS-05-22',
                                 'PRIASS-05-52',
                                 'PRIASS-05-70']}}
    required_fields = ['priority_assets', 'maintenance_due', 'anomaly_ids', 'diagnostic_codes', 'dispatch_required']
    numeric_fields = []
    list_fields = ['priority_assets', 'maintenance_due', 'anomaly_ids', 'diagnostic_codes']
    dict_fields = []
    bool_fields = ['dispatch_required']
    text_fields = []
    family_marker = "facilities_iot_grader"
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
