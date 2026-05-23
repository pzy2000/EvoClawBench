---
id: task_83_fleet_maintenance_schedule
name: Fleet Maintenance Schedule
category: facilities_iot
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: facilities_iot
task_family: Facilities/IoT
grader_family: facilities_iot
workspace_files:
  - assets/generated_tasks/task_83_fleet_maintenance_schedule/case_01.json
  - assets/generated_tasks/task_83_fleet_maintenance_schedule/case_02.json
  - assets/generated_tasks/task_83_fleet_maintenance_schedule/case_03.json
  - assets/generated_tasks/task_83_fleet_maintenance_schedule/case_04.json
  - assets/generated_tasks/task_83_fleet_maintenance_schedule/case_05.json
---

# Fleet Maintenance Schedule

Process five fixture-backed facilities/iot cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic fleet maintenance schedule fixture files under `assets/generated_tasks/task_83_fleet_maintenance_schedule/`.
For each input file, review operational telemetry, schedule maintenance, and diagnose device events and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required`.
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
- Input: `assets/generated_tasks/task_83_fleet_maintenance_schedule/case_01.json`
- Special handling: derive `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required` for this facilities/iot case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_83_fleet_maintenance_schedule/case_02.json`
- Special handling: derive `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required` for this facilities/iot case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_83_fleet_maintenance_schedule/case_03.json`
- Special handling: derive `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required` for this facilities/iot case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_83_fleet_maintenance_schedule/case_04.json`
- Special handling: derive `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required` for this facilities/iot case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_83_fleet_maintenance_schedule/case_05.json`
- Special handling: derive `priority_assets, maintenance_due, anomaly_ids, diagnostic_codes, dispatch_required` for this facilities/iot case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `priority_assets` with the correct value.
- [ ] Each report includes `maintenance_due` with the correct value.
- [ ] Each report includes `anomaly_ids` with the correct value.
- [ ] Each report includes `diagnostic_codes` with the correct value.
- [ ] Each report includes `dispatch_required` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'anomaly_ids': ['FMS-01-03', 'FMS-01-04'],
             'diagnostic_codes': ['TEMP_SPIKE', 'VIBRATION'],
             'dispatch_required': True,
             'maintenance_due': ['UNIT-01-1', 'UNIT-01-2'],
             'priority_assets': ['ASSET-01-A', 'ASSET-01-C']},
 'case_02': {'anomaly_ids': ['FMS-02-03', 'FMS-02-04'],
             'diagnostic_codes': ['BATTERY_LOW'],
             'dispatch_required': False,
             'maintenance_due': ['UNIT-02-1', 'UNIT-02-2'],
             'priority_assets': ['ASSET-02-A', 'ASSET-02-C']},
 'case_03': {'anomaly_ids': ['FMS-03-03', 'FMS-03-04'],
             'diagnostic_codes': ['TEMP_SPIKE', 'VIBRATION'],
             'dispatch_required': True,
             'maintenance_due': ['UNIT-03-1', 'UNIT-03-2'],
             'priority_assets': ['ASSET-03-A', 'ASSET-03-C']},
 'case_04': {'anomaly_ids': ['FMS-04-03', 'FMS-04-04'],
             'diagnostic_codes': ['BATTERY_LOW'],
             'dispatch_required': False,
             'maintenance_due': ['UNIT-04-1', 'UNIT-04-2'],
             'priority_assets': ['ASSET-04-A', 'ASSET-04-C']},
 'case_05': {'anomaly_ids': ['FMS-05-03', 'FMS-05-04'],
             'diagnostic_codes': ['TEMP_SPIKE', 'VIBRATION'],
             'dispatch_required': True,
             'maintenance_due': ['UNIT-05-1', 'UNIT-05-2'],
             'priority_assets': ['ASSET-05-A', 'ASSET-05-C']}}
    required_fields = ['priority_assets',
 'maintenance_due',
 'anomaly_ids',
 'diagnostic_codes',
 'dispatch_required']
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
