---
id: task_62_sql_schema_migration_review
name: SQL Schema Migration Review
category: data_analysis
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: data_analytics
task_family: Data/Analytics
grader_family: data_analytics
workspace_files:
  - assets/generated_tasks/task_62_sql_schema_migration_review/case_01.csv
  - assets/generated_tasks/task_62_sql_schema_migration_review/case_02.csv
  - assets/generated_tasks/task_62_sql_schema_migration_review/case_03.csv
  - assets/generated_tasks/task_62_sql_schema_migration_review/case_04.csv
  - assets/generated_tasks/task_62_sql_schema_migration_review/case_05.csv
---

# SQL Schema Migration Review

Process five fixture-backed data/analytics cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic sql schema migration review fixture files under `assets/generated_tasks/task_62_sql_schema_migration_review/`.
For each input file, normalize data, calculate metric changes, and author quality findings and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `row_count, quality_failures, metric_delta, rule_ids, experiment_winner`.
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
- Input: `assets/generated_tasks/task_62_sql_schema_migration_review/case_01.csv`
- Special handling: derive `row_count, quality_failures, metric_delta, rule_ids, experiment_winner` for this data/analytics case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_62_sql_schema_migration_review/case_02.csv`
- Special handling: derive `row_count, quality_failures, metric_delta, rule_ids, experiment_winner` for this data/analytics case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_62_sql_schema_migration_review/case_03.csv`
- Special handling: derive `row_count, quality_failures, metric_delta, rule_ids, experiment_winner` for this data/analytics case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_62_sql_schema_migration_review/case_04.csv`
- Special handling: derive `row_count, quality_failures, metric_delta, rule_ids, experiment_winner` for this data/analytics case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_62_sql_schema_migration_review/case_05.csv`
- Special handling: derive `row_count, quality_failures, metric_delta, rule_ids, experiment_winner` for this data/analytics case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `row_count` with the correct value.
- [ ] Each report includes `quality_failures` with the correct value.
- [ ] Each report includes `metric_delta` with the correct value.
- [ ] Each report includes `rule_ids` with the correct value.
- [ ] Each report includes `experiment_winner` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'experiment_winner': 'variant_b',
             'metric_delta': -4.7,
             'quality_failures': ['null_required_field', 'duplicate_key'],
             'row_count': 117,
             'rule_ids': ['DQ-01-A', 'DQ-01-B']},
 'case_02': {'experiment_winner': 'control',
             'metric_delta': -2.35,
             'quality_failures': ['range_violation'],
             'row_count': 134,
             'rule_ids': ['DQ-02-A', 'DQ-02-B']},
 'case_03': {'experiment_winner': 'variant_b',
             'metric_delta': 0.0,
             'quality_failures': ['null_required_field', 'duplicate_key'],
             'row_count': 151,
             'rule_ids': ['DQ-03-A', 'DQ-03-B']},
 'case_04': {'experiment_winner': 'control',
             'metric_delta': 2.35,
             'quality_failures': ['range_violation'],
             'row_count': 168,
             'rule_ids': ['DQ-04-A', 'DQ-04-B']},
 'case_05': {'experiment_winner': 'variant_b',
             'metric_delta': 4.7,
             'quality_failures': ['null_required_field', 'duplicate_key'],
             'row_count': 185,
             'rule_ids': ['DQ-05-A', 'DQ-05-B']}}
    required_fields = ['row_count',
 'quality_failures',
 'metric_delta',
 'rule_ids',
 'experiment_winner']
    numeric_fields = ['row_count', 'metric_delta']
    list_fields = ['quality_failures', 'rule_ids']
    dict_fields = []
    bool_fields = []
    text_fields = ['experiment_winner']
    family_marker = "data_analytics_grader"
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
