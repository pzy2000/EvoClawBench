---
id: task_27_contract_clause_extraction
name: Contract Clause Extraction
category: legal_ops
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: legal
task_family: Legal
grader_family: legal
workspace_files:
  - assets/generated_tasks/task_27_contract_clause_extraction/case_01.txt
  - assets/generated_tasks/task_27_contract_clause_extraction/case_02.txt
  - assets/generated_tasks/task_27_contract_clause_extraction/case_03.txt
  - assets/generated_tasks/task_27_contract_clause_extraction/case_04.txt
  - assets/generated_tasks/task_27_contract_clause_extraction/case_05.txt
---

# Contract Clause Extraction

Process five hard-mode fixture-backed legal cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode contract clause extraction fixture files under `assets/generated_tasks/task_27_contract_clause_extraction/`.
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
- Input: `assets/generated_tasks/task_27_contract_clause_extraction/case_01.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_27_contract_clause_extraction/case_02.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_27_contract_clause_extraction/case_03.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_27_contract_clause_extraction/case_04.txt`
- Special handling: select the valid evidence packet, discard all decoys, and derive clause_labels, missing_fields, high_risk_terms, parties, effective_date for this legal case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_27_contract_clause_extraction/case_05.txt`
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
    expected = {'case_01': {'clause_labels': ['CLALAB-01-38', 'CLALAB-01-60', 'CLALAB-01-61', 'CLALAB-01-82'],
             'effective_date': '2026-01-14',
             'high_risk_terms': ['HIGRISTER-01-50',
                                 'HIGRISTER-01-58',
                                 'HIGRISTER-01-84',
                                 'HIGRISTER-01-93'],
             'missing_fields': ['MISFIE-01-22', 'MISFIE-01-23', 'MISFIE-01-74', 'MISFIE-01-87'],
             'parties': ['PAR-01-19', 'PAR-01-20', 'PAR-01-60', 'PAR-01-62']},
 'case_02': {'clause_labels': ['CLALAB-02-38', 'CLALAB-02-60', 'CLALAB-02-61', 'CLALAB-02-82'],
             'effective_date': '2026-09-14',
             'high_risk_terms': ['HIGRISTER-02-50',
                                 'HIGRISTER-02-58',
                                 'HIGRISTER-02-84',
                                 'HIGRISTER-02-93'],
             'missing_fields': ['MISFIE-02-22', 'MISFIE-02-23', 'MISFIE-02-74', 'MISFIE-02-87'],
             'parties': ['PAR-02-19', 'PAR-02-20', 'PAR-02-60', 'PAR-02-62']},
 'case_03': {'clause_labels': ['CLALAB-03-38', 'CLALAB-03-60', 'CLALAB-03-61', 'CLALAB-03-82'],
             'effective_date': '2026-08-14',
             'high_risk_terms': ['HIGRISTER-03-50',
                                 'HIGRISTER-03-58',
                                 'HIGRISTER-03-84',
                                 'HIGRISTER-03-93'],
             'missing_fields': ['MISFIE-03-22', 'MISFIE-03-23', 'MISFIE-03-74', 'MISFIE-03-87'],
             'parties': ['PAR-03-19', 'PAR-03-20', 'PAR-03-60', 'PAR-03-62']},
 'case_04': {'clause_labels': ['CLALAB-04-38', 'CLALAB-04-60', 'CLALAB-04-61', 'CLALAB-04-82'],
             'effective_date': '2026-05-21',
             'high_risk_terms': ['HIGRISTER-04-50',
                                 'HIGRISTER-04-58',
                                 'HIGRISTER-04-84',
                                 'HIGRISTER-04-93'],
             'missing_fields': ['MISFIE-04-22', 'MISFIE-04-23', 'MISFIE-04-74', 'MISFIE-04-87'],
             'parties': ['PAR-04-19', 'PAR-04-20', 'PAR-04-60', 'PAR-04-62']},
 'case_05': {'clause_labels': ['CLALAB-05-38', 'CLALAB-05-60', 'CLALAB-05-61', 'CLALAB-05-82'],
             'effective_date': '2026-09-14',
             'high_risk_terms': ['HIGRISTER-05-50',
                                 'HIGRISTER-05-58',
                                 'HIGRISTER-05-84',
                                 'HIGRISTER-05-93'],
             'missing_fields': ['MISFIE-05-22', 'MISFIE-05-23', 'MISFIE-05-74', 'MISFIE-05-87'],
             'parties': ['PAR-05-19', 'PAR-05-20', 'PAR-05-60', 'PAR-05-62']}}
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
