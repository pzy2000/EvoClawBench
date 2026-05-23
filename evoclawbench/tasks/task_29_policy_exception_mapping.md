---
id: task_29_policy_exception_mapping
name: Policy Exception Mapping
category: legal_ops
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: legal
task_family: Legal
grader_family: legal
workspace_files:
  - assets/generated_tasks/task_29_policy_exception_mapping/case_01.txt
  - assets/generated_tasks/task_29_policy_exception_mapping/case_02.txt
  - assets/generated_tasks/task_29_policy_exception_mapping/case_03.txt
  - assets/generated_tasks/task_29_policy_exception_mapping/case_04.txt
  - assets/generated_tasks/task_29_policy_exception_mapping/case_05.txt
---

# Policy Exception Mapping

Process five fixture-backed legal cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic policy exception mapping fixture files under `assets/generated_tasks/task_29_policy_exception_mapping/`.
For each input file, extract clause labels, parties, dates, missing fields, and risky terms and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `clause_labels, missing_fields, high_risk_terms, parties, effective_date`.
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
- Input: `assets/generated_tasks/task_29_policy_exception_mapping/case_01.txt`
- Special handling: derive `clause_labels, missing_fields, high_risk_terms, parties, effective_date` for this legal case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_29_policy_exception_mapping/case_02.txt`
- Special handling: derive `clause_labels, missing_fields, high_risk_terms, parties, effective_date` for this legal case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_29_policy_exception_mapping/case_03.txt`
- Special handling: derive `clause_labels, missing_fields, high_risk_terms, parties, effective_date` for this legal case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_29_policy_exception_mapping/case_04.txt`
- Special handling: derive `clause_labels, missing_fields, high_risk_terms, parties, effective_date` for this legal case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_29_policy_exception_mapping/case_05.txt`
- Special handling: derive `clause_labels, missing_fields, high_risk_terms, parties, effective_date` for this legal case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `clause_labels` with the correct value.
- [ ] Each report includes `missing_fields` with the correct value.
- [ ] Each report includes `high_risk_terms` with the correct value.
- [ ] Each report includes `parties` with the correct value.
- [ ] Each report includes `effective_date` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'clause_labels': ['confidentiality', 'termination', 'liability'],
             'effective_date': '2026-07-11',
             'high_risk_terms': ['auto-renewal'],
             'missing_fields': ['effective_date'],
             'parties': ['Policy Exception Mapping Provider', 'Policy Exception Mapping Client']},
 'case_02': {'clause_labels': ['confidentiality', 'termination'],
             'effective_date': '2026-07-12',
             'high_risk_terms': ['auto-renewal'],
             'missing_fields': ['governing_law'],
             'parties': ['Policy Exception Mapping Provider', 'Policy Exception Mapping Client']},
 'case_03': {'clause_labels': ['confidentiality', 'termination', 'liability'],
             'effective_date': '2026-07-13',
             'high_risk_terms': ['unlimited liability'],
             'missing_fields': ['effective_date'],
             'parties': ['Policy Exception Mapping Provider', 'Policy Exception Mapping Client']},
 'case_04': {'clause_labels': ['confidentiality', 'termination'],
             'effective_date': '2026-07-14',
             'high_risk_terms': ['auto-renewal'],
             'missing_fields': ['governing_law'],
             'parties': ['Policy Exception Mapping Provider', 'Policy Exception Mapping Client']},
 'case_05': {'clause_labels': ['confidentiality', 'termination', 'liability'],
             'effective_date': '2026-07-15',
             'high_risk_terms': ['auto-renewal'],
             'missing_fields': ['effective_date'],
             'parties': ['Policy Exception Mapping Provider', 'Policy Exception Mapping Client']}}
    required_fields = ['clause_labels',
 'missing_fields',
 'high_risk_terms',
 'parties',
 'effective_date']
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
