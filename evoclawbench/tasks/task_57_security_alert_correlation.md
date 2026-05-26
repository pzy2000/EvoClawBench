---
id: task_57_security_alert_correlation
name: Security Alert Correlation
category: security_privacy
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: security_privacy
task_family: Security/Privacy
grader_family: security_privacy
workspace_files:
  - assets/generated_tasks/task_57_security_alert_correlation/case_01.json
  - assets/generated_tasks/task_57_security_alert_correlation/case_02.json
  - assets/generated_tasks/task_57_security_alert_correlation/case_03.json
  - assets/generated_tasks/task_57_security_alert_correlation/case_04.json
  - assets/generated_tasks/task_57_security_alert_correlation/case_05.json
---

# Security Alert Correlation

Process five hard-mode fixture-backed security/privacy cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode security alert correlation fixture files under `assets/generated_tasks/task_57_security_alert_correlation/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `incident_ids`, `redacted_fields`, `raw_pii_present`, `approved_exceptions`, `severity_counts`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `incident_ids` (list)
- `L2` -> `redacted_fields` (list)
- `B1` -> `raw_pii_present` (bool)
- `L3` -> `approved_exceptions` (list)
- `D1` -> `severity_counts` (dict)

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
- Input: `assets/generated_tasks/task_57_security_alert_correlation/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive incident_ids, redacted_fields, raw_pii_present, approved_exceptions, severity_counts for this security/privacy case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_57_security_alert_correlation/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive incident_ids, redacted_fields, raw_pii_present, approved_exceptions, severity_counts for this security/privacy case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_57_security_alert_correlation/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive incident_ids, redacted_fields, raw_pii_present, approved_exceptions, severity_counts for this security/privacy case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_57_security_alert_correlation/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive incident_ids, redacted_fields, raw_pii_present, approved_exceptions, severity_counts for this security/privacy case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_57_security_alert_correlation/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive incident_ids, redacted_fields, raw_pii_present, approved_exceptions, severity_counts for this security/privacy case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `incident_ids` with the correctly derived value.
- [ ] Each report includes `redacted_fields` with the correctly derived value.
- [ ] Each report includes `raw_pii_present` with the correctly derived value.
- [ ] Each report includes `approved_exceptions` with the correctly derived value.
- [ ] Each report includes `severity_counts` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'approved_exceptions': ['APPEXC-01-24',
                                     'APPEXC-01-62',
                                     'APPEXC-01-68',
                                     'APPEXC-01-80'],
             'incident_ids': ['INCIDS-01-15', 'INCIDS-01-38', 'INCIDS-01-74', 'INCIDS-01-84'],
             'raw_pii_present': True,
             'redacted_fields': ['REDFIE-01-31',
                                 'REDFIE-01-46',
                                 'REDFIE-01-62',
                                 'REDFIE-01-66'],
             'severity_counts': {'critical': 6, 'high': 10, 'low': 8, 'medium': 8}},
 'case_02': {'approved_exceptions': ['APPEXC-02-24',
                                     'APPEXC-02-62',
                                     'APPEXC-02-68',
                                     'APPEXC-02-80'],
             'incident_ids': ['INCIDS-02-15', 'INCIDS-02-38', 'INCIDS-02-74', 'INCIDS-02-84'],
             'raw_pii_present': False,
             'redacted_fields': ['REDFIE-02-31',
                                 'REDFIE-02-46',
                                 'REDFIE-02-62',
                                 'REDFIE-02-66'],
             'severity_counts': {'critical': 4, 'high': 12, 'low': 5}},
 'case_03': {'approved_exceptions': ['APPEXC-03-24',
                                     'APPEXC-03-62',
                                     'APPEXC-03-68',
                                     'APPEXC-03-80'],
             'incident_ids': ['INCIDS-03-15', 'INCIDS-03-38', 'INCIDS-03-74', 'INCIDS-03-84'],
             'raw_pii_present': True,
             'redacted_fields': ['REDFIE-03-31',
                                 'REDFIE-03-46',
                                 'REDFIE-03-62',
                                 'REDFIE-03-66'],
             'severity_counts': {'high': 1, 'low': 4, 'medium': 5}},
 'case_04': {'approved_exceptions': ['APPEXC-04-24',
                                     'APPEXC-04-62',
                                     'APPEXC-04-68',
                                     'APPEXC-04-80'],
             'incident_ids': ['INCIDS-04-15', 'INCIDS-04-38', 'INCIDS-04-74', 'INCIDS-04-84'],
             'raw_pii_present': False,
             'redacted_fields': ['REDFIE-04-31',
                                 'REDFIE-04-46',
                                 'REDFIE-04-62',
                                 'REDFIE-04-66'],
             'severity_counts': {'critical': 2, 'high': 10, 'low': 12, 'medium': 2}},
 'case_05': {'approved_exceptions': ['APPEXC-05-24',
                                     'APPEXC-05-62',
                                     'APPEXC-05-68',
                                     'APPEXC-05-80'],
             'incident_ids': ['INCIDS-05-15', 'INCIDS-05-38', 'INCIDS-05-74', 'INCIDS-05-84'],
             'raw_pii_present': False,
             'redacted_fields': ['REDFIE-05-31',
                                 'REDFIE-05-46',
                                 'REDFIE-05-62',
                                 'REDFIE-05-66'],
             'severity_counts': {'critical': 3, 'high': 9, 'low': 3, 'medium': 2}}}
    required_fields = ['incident_ids', 'redacted_fields', 'raw_pii_present', 'approved_exceptions', 'severity_counts']
    numeric_fields = []
    list_fields = ['incident_ids', 'redacted_fields', 'approved_exceptions']
    dict_fields = ['severity_counts']
    bool_fields = ['raw_pii_present']
    text_fields = []
    family_marker = "security_privacy_grader"
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
