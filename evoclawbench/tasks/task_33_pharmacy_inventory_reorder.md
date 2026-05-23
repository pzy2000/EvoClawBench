---
id: task_33_pharmacy_inventory_reorder
name: Pharmacy Inventory Reorder
category: healthcare_admin
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: healthcare
task_family: Healthcare
grader_family: healthcare
workspace_files:
  - assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_01.json
  - assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_02.json
  - assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_03.json
  - assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_04.json
  - assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_05.json
---

# Pharmacy Inventory Reorder

Process five fixture-backed healthcare cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic pharmacy inventory reorder fixture files under `assets/generated_tasks/task_33_pharmacy_inventory_reorder/`.
For each input file, route records, identify eligibility, inventory, and urgent follow-up items and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count`.
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
- Input: `assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_01.json`
- Special handling: derive `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count` for this healthcare case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_02.json`
- Special handling: derive `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count` for this healthcare case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_03.json`
- Special handling: derive `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count` for this healthcare case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_04.json`
- Special handling: derive `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count` for this healthcare case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_33_pharmacy_inventory_reorder/case_05.json`
- Special handling: derive `eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count` for this healthcare case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `eligible_ids` with the correct value.
- [ ] Each report includes `routing_queue` with the correct value.
- [ ] Each report includes `followup_ids` with the correct value.
- [ ] Each report includes `stockout_ids` with the correct value.
- [ ] Each report includes `urgent_count` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'eligible_ids': ['PIR-01-01', 'PIR-01-02'],
             'followup_ids': ['PIR-01-03', 'PIR-01-04'],
             'routing_queue': {'admin': 2, 'clinical': 2, 'pharmacy': 1},
             'stockout_ids': [],
             'urgent_count': 2},
 'case_02': {'eligible_ids': ['PIR-02-01', 'PIR-02-02'],
             'followup_ids': ['PIR-02-03', 'PIR-02-04'],
             'routing_queue': {'admin': 2, 'clinical': 1, 'pharmacy': 0},
             'stockout_ids': ['MED-02'],
             'urgent_count': 3},
 'case_03': {'eligible_ids': ['PIR-03-01', 'PIR-03-02'],
             'followup_ids': ['PIR-03-03', 'PIR-03-04'],
             'routing_queue': {'admin': 2, 'clinical': 2, 'pharmacy': 1},
             'stockout_ids': [],
             'urgent_count': 1},
 'case_04': {'eligible_ids': ['PIR-04-01', 'PIR-04-02'],
             'followup_ids': ['PIR-04-03', 'PIR-04-04'],
             'routing_queue': {'admin': 2, 'clinical': 1, 'pharmacy': 0},
             'stockout_ids': ['MED-04'],
             'urgent_count': 2},
 'case_05': {'eligible_ids': ['PIR-05-01', 'PIR-05-02'],
             'followup_ids': ['PIR-05-03', 'PIR-05-04'],
             'routing_queue': {'admin': 2, 'clinical': 2, 'pharmacy': 1},
             'stockout_ids': [],
             'urgent_count': 3}}
    required_fields = ['eligible_ids',
 'routing_queue',
 'followup_ids',
 'stockout_ids',
 'urgent_count']
    numeric_fields = ['urgent_count']
    list_fields = ['eligible_ids', 'followup_ids', 'stockout_ids']
    dict_fields = ['routing_queue']
    bool_fields = []
    text_fields = []
    family_marker = "healthcare_grader"
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
