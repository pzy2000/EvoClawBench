---
id: task_44_admissions_packet_screening
name: Admissions Packet Screening
category: hr_education
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: hr_education
task_family: HR/Education
grader_family: hr_education
workspace_files:
  - assets/generated_tasks/task_44_admissions_packet_screening/case_01.json
  - assets/generated_tasks/task_44_admissions_packet_screening/case_02.json
  - assets/generated_tasks/task_44_admissions_packet_screening/case_03.json
  - assets/generated_tasks/task_44_admissions_packet_screening/case_04.json
  - assets/generated_tasks/task_44_admissions_packet_screening/case_05.json
---

# Admissions Packet Screening

Process five fixture-backed hr/education cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic admissions packet screening fixture files under `assets/generated_tasks/task_44_admissions_packet_screening/`.
For each input file, audit completion, calibrate scores, assign tracks, and flag interventions and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids`.
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
- Input: `assets/generated_tasks/task_44_admissions_packet_screening/case_01.json`
- Special handling: derive `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids` for this hr/education case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_44_admissions_packet_screening/case_02.json`
- Special handling: derive `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids` for this hr/education case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_44_admissions_packet_screening/case_03.json`
- Special handling: derive `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids` for this hr/education case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_44_admissions_packet_screening/case_04.json`
- Special handling: derive `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids` for this hr/education case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_44_admissions_packet_screening/case_05.json`
- Special handling: derive `completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids` for this hr/education case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `completion_rate` with the correct value.
- [ ] Each report includes `missing_items` with the correct value.
- [ ] Each report includes `calibrated_scores` with the correct value.
- [ ] Each report includes `assigned_track` with the correct value.
- [ ] Each report includes `intervention_ids` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'assigned_track': 'accelerated',
             'calibrated_scores': {'APS-01-01': 5, 'APS-01-02': 3},
             'completion_rate': 0.72,
             'intervention_ids': ['APS-01-04'],
             'missing_items': ['background_check']},
 'case_02': {'assigned_track': 'standard',
             'calibrated_scores': {'APS-02-01': 4, 'APS-02-02': 3},
             'completion_rate': 0.76,
             'intervention_ids': ['APS-02-04'],
             'missing_items': ['rubric_alignment', 'manager_signoff']},
 'case_03': {'assigned_track': 'accelerated',
             'calibrated_scores': {'APS-03-01': 5, 'APS-03-02': 3},
             'completion_rate': 0.8,
             'intervention_ids': ['APS-03-04'],
             'missing_items': ['background_check']},
 'case_04': {'assigned_track': 'standard',
             'calibrated_scores': {'APS-04-01': 4, 'APS-04-02': 3},
             'completion_rate': 0.84,
             'intervention_ids': ['APS-04-04'],
             'missing_items': ['rubric_alignment', 'manager_signoff']},
 'case_05': {'assigned_track': 'accelerated',
             'calibrated_scores': {'APS-05-01': 5, 'APS-05-02': 3},
             'completion_rate': 0.88,
             'intervention_ids': ['APS-05-04'],
             'missing_items': ['background_check']}}
    required_fields = ['completion_rate',
 'missing_items',
 'calibrated_scores',
 'assigned_track',
 'intervention_ids']
    numeric_fields = ['completion_rate']
    list_fields = ['missing_items', 'intervention_ids']
    dict_fields = ['calibrated_scores']
    bool_fields = []
    text_fields = ['assigned_track']
    family_marker = "hr_education_grader"
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
