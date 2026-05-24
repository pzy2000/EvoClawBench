---
id: task_31_vendor_contract_risk
name: Vendor Contract Risk
category: legal_ops
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: legal
task_family: Legal
grader_family: legal
workspace_files:
  - assets/generated_tasks/task_31_vendor_contract_risk/case_01.txt
  - assets/generated_tasks/task_31_vendor_contract_risk/case_02.txt
  - assets/generated_tasks/task_31_vendor_contract_risk/case_03.txt
  - assets/generated_tasks/task_31_vendor_contract_risk/case_04.txt
  - assets/generated_tasks/task_31_vendor_contract_risk/case_05.txt
---

# Vendor Contract Risk

Process five hard-mode fixture-backed legal cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode vendor contract risk fixture files under `assets/generated_tasks/task_31_vendor_contract_risk/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `clause_labels`, `missing_fields`, `high_risk_terms`, `parties`, `effective_date`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `clause_labels` (list)
- `L2` -> `missing_fields` (list)
- `L3` -> `high_risk_terms` (list)
- `L4` -> `parties` (list)
- `T1` -> `effective_date` (text)

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
- Input: `assets/generated_tasks/task_31_vendor_contract_risk/case_01.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_31_vendor_contract_risk/case_02.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_31_vendor_contract_risk/case_03.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_31_vendor_contract_risk/case_04.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_31_vendor_contract_risk/case_05.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `clause_labels` with the correctly derived value.
- [ ] Each report includes `missing_fields` with the correctly derived value.
- [ ] Each report includes `high_risk_terms` with the correctly derived value.
- [ ] Each report includes `parties` with the correctly derived value.
- [ ] Each report includes `effective_date` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'clause_labels': ['CLALAB-01-103', 'CLALAB-01-67', 'CLALAB-01-70', 'CLALAB-01-89'],
             'effective_date': '2026-06-14',
             'high_risk_terms': ['HIGRISTER-01-27',
                                 'HIGRISTER-01-71',
                                 'HIGRISTER-01-86',
                                 'HIGRISTER-01-98'],
             'missing_fields': ['MISFIE-01-11', 'MISFIE-01-54', 'MISFIE-01-70'],
             'parties': ['PAR-01-11', 'PAR-01-17', 'PAR-01-76', 'PAR-01-80']},
 'case_02': {'clause_labels': ['CLALAB-02-103', 'CLALAB-02-67', 'CLALAB-02-70', 'CLALAB-02-89'],
             'effective_date': '2026-01-14',
             'high_risk_terms': ['HIGRISTER-02-27',
                                 'HIGRISTER-02-71',
                                 'HIGRISTER-02-86',
                                 'HIGRISTER-02-98'],
             'missing_fields': ['MISFIE-02-11', 'MISFIE-02-54', 'MISFIE-02-70'],
             'parties': ['PAR-02-11', 'PAR-02-17', 'PAR-02-76', 'PAR-02-80']},
 'case_03': {'clause_labels': ['CLALAB-03-103', 'CLALAB-03-67', 'CLALAB-03-70', 'CLALAB-03-89'],
             'effective_date': '2026-03-21',
             'high_risk_terms': ['HIGRISTER-03-27',
                                 'HIGRISTER-03-71',
                                 'HIGRISTER-03-86',
                                 'HIGRISTER-03-98'],
             'missing_fields': ['MISFIE-03-11', 'MISFIE-03-54', 'MISFIE-03-70'],
             'parties': ['PAR-03-11', 'PAR-03-17', 'PAR-03-76', 'PAR-03-80']},
 'case_04': {'clause_labels': ['CLALAB-04-103', 'CLALAB-04-67', 'CLALAB-04-70', 'CLALAB-04-89'],
             'effective_date': '2026-08-07',
             'high_risk_terms': ['HIGRISTER-04-27',
                                 'HIGRISTER-04-71',
                                 'HIGRISTER-04-86',
                                 'HIGRISTER-04-98'],
             'missing_fields': ['MISFIE-04-11', 'MISFIE-04-54', 'MISFIE-04-70'],
             'parties': ['PAR-04-11', 'PAR-04-17', 'PAR-04-76', 'PAR-04-80']},
 'case_05': {'clause_labels': ['CLALAB-05-103', 'CLALAB-05-67', 'CLALAB-05-70', 'CLALAB-05-89'],
             'effective_date': '2026-07-14',
             'high_risk_terms': ['HIGRISTER-05-27',
                                 'HIGRISTER-05-71',
                                 'HIGRISTER-05-86',
                                 'HIGRISTER-05-98'],
             'missing_fields': ['MISFIE-05-11', 'MISFIE-05-54', 'MISFIE-05-70'],
             'parties': ['PAR-05-11', 'PAR-05-17', 'PAR-05-76', 'PAR-05-80']}}
    required_fields = ['clause_labels', 'missing_fields', 'high_risk_terms', 'parties', 'effective_date']
    numeric_fields = []
    list_fields = ['clause_labels', 'missing_fields', 'high_risk_terms', 'parties']
    dict_fields = []
    bool_fields = []
    text_fields = ['effective_date']
    family_marker = "legal_grader"
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
