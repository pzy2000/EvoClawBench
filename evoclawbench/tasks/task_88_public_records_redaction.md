---
id: task_88_public_records_redaction
name: Public Records Redaction
category: public_audit
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: public_audit
task_family: Public Sector/Audit
grader_family: public_audit
workspace_files:
  - assets/generated_tasks/task_88_public_records_redaction/case_01.json
  - assets/generated_tasks/task_88_public_records_redaction/case_02.json
  - assets/generated_tasks/task_88_public_records_redaction/case_03.json
  - assets/generated_tasks/task_88_public_records_redaction/case_04.json
  - assets/generated_tasks/task_88_public_records_redaction/case_05.json
---

# Public Records Redaction

Process five hard-mode fixture-backed public sector/audit cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode public records redaction fixture files under `assets/generated_tasks/task_88_public_records_redaction/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `routing_queue`, `redactions_required`, `missing_evidence`, `risk_summary`, `compliant`.
Use the channel map below to translate evidence channels into output fields:

- `D1` -> `routing_queue` (dict)
- `L1` -> `redactions_required` (list)
- `L2` -> `missing_evidence` (list)
- `D2` -> `risk_summary` (dict)
- `B1` -> `compliant` (bool)

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
- Input: `assets/generated_tasks/task_88_public_records_redaction/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive routing_queue, redactions_required, missing_evidence, risk_summary, compliant for this public sector/audit case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_88_public_records_redaction/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive routing_queue, redactions_required, missing_evidence, risk_summary, compliant for this public sector/audit case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_88_public_records_redaction/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive routing_queue, redactions_required, missing_evidence, risk_summary, compliant for this public sector/audit case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_88_public_records_redaction/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive routing_queue, redactions_required, missing_evidence, risk_summary, compliant for this public sector/audit case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_88_public_records_redaction/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive routing_queue, redactions_required, missing_evidence, risk_summary, compliant for this public sector/audit case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `routing_queue` with the correctly derived value.
- [ ] Each report includes `redactions_required` with the correctly derived value.
- [ ] Each report includes `missing_evidence` with the correctly derived value.
- [ ] Each report includes `risk_summary` with the correctly derived value.
- [ ] Each report includes `compliant` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'compliant': True,
             'missing_evidence': ['MISEVI-01-28',
                                  'MISEVI-01-65',
                                  'MISEVI-01-76',
                                  'MISEVI-01-91'],
             'redactions_required': ['approve_with_note', 'escalate', 'hold', 'manual_review'],
             'risk_summary': {'compliance': 10, 'financial': 6, 'operational': 10},
             'routing_queue': {'admin': 2, 'clinical': 5, 'pharmacy': 8}},
 'case_02': {'compliant': False,
             'missing_evidence': ['MISEVI-02-28',
                                  'MISEVI-02-65',
                                  'MISEVI-02-76',
                                  'MISEVI-02-91'],
             'redactions_required': ['approve_with_note', 'hold', 'manual_review', 'reject'],
             'risk_summary': {'compliance': 7, 'financial': 5, 'operational': 3},
             'routing_queue': {'admin': 3, 'clinical': 4, 'pharmacy': 5}},
 'case_03': {'compliant': True,
             'missing_evidence': ['MISEVI-03-28',
                                  'MISEVI-03-65',
                                  'MISEVI-03-76',
                                  'MISEVI-03-91'],
             'redactions_required': ['approve_with_note', 'hold', 'reject'],
             'risk_summary': {'compliance': 9, 'financial': 9, 'operational': 6},
             'routing_queue': {'admin': 5, 'clinical': 8, 'pharmacy': 3}},
 'case_04': {'compliant': True,
             'missing_evidence': ['MISEVI-04-28',
                                  'MISEVI-04-65',
                                  'MISEVI-04-76',
                                  'MISEVI-04-91'],
             'redactions_required': ['approve_with_note',
                                     'escalate',
                                     'manual_review',
                                     'reject'],
             'risk_summary': {'compliance': 8, 'financial': 5, 'operational': 6},
             'routing_queue': {'clinical': 8, 'pharmacy': 9}},
 'case_05': {'compliant': False,
             'missing_evidence': ['MISEVI-05-28',
                                  'MISEVI-05-65',
                                  'MISEVI-05-76',
                                  'MISEVI-05-91'],
             'redactions_required': ['approve_with_note', 'escalate', 'reject'],
             'risk_summary': {'compliance': 8, 'financial': 6, 'operational': 4},
             'routing_queue': {'admin': -1, 'clinical': 7, 'pharmacy': 10}}}
    required_fields = ['routing_queue', 'redactions_required', 'missing_evidence', 'risk_summary', 'compliant']
    numeric_fields = []
    list_fields = ['redactions_required', 'missing_evidence']
    dict_fields = ['routing_queue', 'risk_summary']
    bool_fields = ['compliant']
    text_fields = []
    family_marker = "public_audit_grader"
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
