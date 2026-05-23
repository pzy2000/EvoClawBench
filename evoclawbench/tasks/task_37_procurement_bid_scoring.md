---
id: task_37_procurement_bid_scoring
name: Procurement Bid Scoring
category: procurement_logistics
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: procurement_logistics
task_family: Procurement/Logistics
grader_family: procurement_logistics
workspace_files:
  - assets/generated_tasks/task_37_procurement_bid_scoring/case_01.yaml
  - assets/generated_tasks/task_37_procurement_bid_scoring/case_02.yaml
  - assets/generated_tasks/task_37_procurement_bid_scoring/case_03.yaml
  - assets/generated_tasks/task_37_procurement_bid_scoring/case_04.yaml
  - assets/generated_tasks/task_37_procurement_bid_scoring/case_05.yaml
---

# Procurement Bid Scoring

Process five fixture-backed procurement/logistics cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic procurement bid scoring fixture files under `assets/generated_tasks/task_37_procurement_bid_scoring/`.
For each input file, score vendors or logistics records, identify exceptions, and summarize risk and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate`.
Use exact identifiers from the source files, preserve list values as JSON arrays, and write one report per input case.
Do not modify the input fixtures; only write files under `outputs/`.

---

## Expected Behavior

1. Inspect the first one or two cases to identify the repeated domain workflow.
2. Create a reusable procedure for the family-specific fields instead of solving each case from scratch.
3. Apply the procedure to all five source files, adapting to the record details in each case.
4. Emit the five JSON reports under `outputs/` with stable schemas and exact IDs.
5. Keep any explanatory text inside concise summary-like field values when the schema asks for text.

---

## Sub-Problems

### Sub-Problem 1: North Region Batch
- Input: `assets/generated_tasks/task_37_procurement_bid_scoring/case_01.yaml`
- Special handling: derive `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate` for this procurement/logistics case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_37_procurement_bid_scoring/case_02.yaml`
- Special handling: derive `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate` for this procurement/logistics case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_37_procurement_bid_scoring/case_03.yaml`
- Special handling: derive `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate` for this procurement/logistics case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_37_procurement_bid_scoring/case_04.yaml`
- Special handling: derive `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate` for this procurement/logistics case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_37_procurement_bid_scoring/case_05.yaml`
- Special handling: derive `selected_vendor, match_exceptions, late_shipments, risk_suppliers, savings_estimate` for this procurement/logistics case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `selected_vendor` with the correct value.
- [ ] Each report includes `match_exceptions` with the correct value.
- [ ] Each report includes `late_shipments` with the correct value.
- [ ] Each report includes `risk_suppliers` with the correct value.
- [ ] Each report includes `savings_estimate` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'late_shipments': ['SHIP-01-03'],
             'match_exceptions': ['PBS-01-02', 'PBS-01-03'],
             'risk_suppliers': ['Supplier-1', 'Supplier-6'],
             'savings_estimate': 5125.75,
             'selected_vendor': 'Vendor-A'},
 'case_02': {'late_shipments': ['SHIP-02-01'],
             'match_exceptions': ['PBS-02-02', 'PBS-02-03'],
             'risk_suppliers': ['Supplier-2', 'Supplier-7'],
             'savings_estimate': 5751.5,
             'selected_vendor': 'Vendor-B'},
 'case_03': {'late_shipments': ['SHIP-03-03'],
             'match_exceptions': ['PBS-03-02', 'PBS-03-03'],
             'risk_suppliers': ['Supplier-3', 'Supplier-8'],
             'savings_estimate': 6377.25,
             'selected_vendor': 'Vendor-C'},
 'case_04': {'late_shipments': ['SHIP-04-01'],
             'match_exceptions': ['PBS-04-02', 'PBS-04-03'],
             'risk_suppliers': ['Supplier-4', 'Supplier-9'],
             'savings_estimate': 7003.0,
             'selected_vendor': 'Vendor-D'},
 'case_05': {'late_shipments': ['SHIP-05-03'],
             'match_exceptions': ['PBS-05-02', 'PBS-05-03'],
             'risk_suppliers': ['Supplier-5', 'Supplier-10'],
             'savings_estimate': 7628.75,
             'selected_vendor': 'Vendor-E'}}
    required_fields = ['selected_vendor',
 'match_exceptions',
 'late_shipments',
 'risk_suppliers',
 'savings_estimate']
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
            return isinstance(actual, (int, float)) and math.isclose(float(actual), float(wanted), rel_tol=1e-4, abs_tol=1e-4)
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
        scores[f"{prefix}_{family_marker}_required_fields"] = 1.0 if all(field in data for field in required_fields) else 0.0
        for field, wanted_value in wanted.items():
            scores[f"{prefix}_field_{field}"] = 1.0 if compare(field, data.get(field), wanted_value) else 0.0
    return scores
```
