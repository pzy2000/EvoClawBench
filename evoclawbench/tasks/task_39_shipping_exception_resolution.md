---
id: task_39_shipping_exception_resolution
name: Shipping Exception Resolution
category: procurement_logistics
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: procurement_logistics
task_family: Procurement/Logistics
grader_family: procurement_logistics
workspace_files:
  - assets/generated_tasks/task_39_shipping_exception_resolution/case_01.yaml
  - assets/generated_tasks/task_39_shipping_exception_resolution/case_02.yaml
  - assets/generated_tasks/task_39_shipping_exception_resolution/case_03.yaml
  - assets/generated_tasks/task_39_shipping_exception_resolution/case_04.yaml
  - assets/generated_tasks/task_39_shipping_exception_resolution/case_05.yaml
---

# Shipping Exception Resolution

Process five hard-mode fixture-backed procurement/logistics cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode shipping exception resolution fixture files under `assets/generated_tasks/task_39_shipping_exception_resolution/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `selected_vendor`, `match_exceptions`, `late_shipments`, `risk_suppliers`, `savings_estimate`.
Use the channel map below to translate evidence channels into output fields:

- `T1` -> `selected_vendor` (text)
- `L1` -> `match_exceptions` (list)
- `L2` -> `late_shipments` (list)
- `L3` -> `risk_suppliers` (list)
- `N1` -> `savings_estimate` (numeric)

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
- Input: `assets/generated_tasks/task_39_shipping_exception_resolution/case_01.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate for this procurement/logistics case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_39_shipping_exception_resolution/case_02.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate for this procurement/logistics case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_39_shipping_exception_resolution/case_03.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate for this procurement/logistics case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_39_shipping_exception_resolution/case_04.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate for this procurement/logistics case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_39_shipping_exception_resolution/case_05.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate for this procurement/logistics case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `selected_vendor` with the correctly derived value.
- [ ] Each report includes `match_exceptions` with the correctly derived value.
- [ ] Each report includes `late_shipments` with the correctly derived value.
- [ ] Each report includes `risk_suppliers` with the correctly derived value.
- [ ] Each report includes `savings_estimate` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'late_shipments': ['LATSHI-01-30', 'LATSHI-01-36', 'LATSHI-01-65', 'LATSHI-01-72'],
             'match_exceptions': ['MATEXC-01-106',
                                  'MATEXC-01-32',
                                  'MATEXC-01-61',
                                  'MATEXC-01-64'],
             'risk_suppliers': ['RISSUP-01-27', 'RISSUP-01-36', 'RISSUP-01-51', 'RISSUP-01-95'],
             'savings_estimate': 13.28,
             'selected_vendor': 'Vendor-Nimbus'},
 'case_02': {'late_shipments': ['LATSHI-02-30', 'LATSHI-02-36', 'LATSHI-02-65', 'LATSHI-02-72'],
             'match_exceptions': ['MATEXC-02-106',
                                  'MATEXC-02-32',
                                  'MATEXC-02-61',
                                  'MATEXC-02-64'],
             'risk_suppliers': ['RISSUP-02-27', 'RISSUP-02-36', 'RISSUP-02-51', 'RISSUP-02-95'],
             'savings_estimate': 19.93,
             'selected_vendor': 'Vendor-Kestrel'},
 'case_03': {'late_shipments': ['LATSHI-03-30', 'LATSHI-03-36', 'LATSHI-03-65', 'LATSHI-03-72'],
             'match_exceptions': ['MATEXC-03-106',
                                  'MATEXC-03-32',
                                  'MATEXC-03-61',
                                  'MATEXC-03-64'],
             'risk_suppliers': ['RISSUP-03-27', 'RISSUP-03-36', 'RISSUP-03-51', 'RISSUP-03-95'],
             'savings_estimate': 33.55,
             'selected_vendor': 'Vendor-Nimbus'},
 'case_04': {'late_shipments': ['LATSHI-04-30', 'LATSHI-04-36', 'LATSHI-04-65', 'LATSHI-04-72'],
             'match_exceptions': ['MATEXC-04-106',
                                  'MATEXC-04-32',
                                  'MATEXC-04-61',
                                  'MATEXC-04-64'],
             'risk_suppliers': ['RISSUP-04-27', 'RISSUP-04-36', 'RISSUP-04-51', 'RISSUP-04-95'],
             'savings_estimate': 16.99,
             'selected_vendor': 'Vendor-Nimbus'},
 'case_05': {'late_shipments': ['LATSHI-05-30', 'LATSHI-05-36', 'LATSHI-05-65', 'LATSHI-05-72'],
             'match_exceptions': ['MATEXC-05-106',
                                  'MATEXC-05-32',
                                  'MATEXC-05-61',
                                  'MATEXC-05-64'],
             'risk_suppliers': ['RISSUP-05-27', 'RISSUP-05-36', 'RISSUP-05-51', 'RISSUP-05-95'],
             'savings_estimate': 46.87,
             'selected_vendor': 'Vendor-Orion'}}
    required_fields = ['selected_vendor', 'match_exceptions', 'late_shipments', 'risk_suppliers', 'savings_estimate']
    numeric_fields = ['savings_estimate']
    list_fields = ['match_exceptions', 'late_shipments', 'risk_suppliers']
    dict_fields = []
    bool_fields = []
    text_fields = ['selected_vendor']
    family_marker = "procurement_logistics_grader"
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
