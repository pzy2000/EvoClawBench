---
id: task_75_changelog_impact_matrix
name: Changelog Impact Matrix
category: localization_release
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: localization_release
task_family: Localization/Release
grader_family: localization_release
workspace_files:
  - assets/generated_tasks/task_75_changelog_impact_matrix/case_01.json
  - assets/generated_tasks/task_75_changelog_impact_matrix/case_02.json
  - assets/generated_tasks/task_75_changelog_impact_matrix/case_03.json
  - assets/generated_tasks/task_75_changelog_impact_matrix/case_04.json
  - assets/generated_tasks/task_75_changelog_impact_matrix/case_05.json
---

# Changelog Impact Matrix

Process five fixture-backed localization/release cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic changelog impact matrix fixture files under `assets/generated_tasks/task_75_changelog_impact_matrix/`.
For each input file, check localization and release artifacts for placeholders, terminology, and launch readiness and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready`.
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
- Input: `assets/generated_tasks/task_75_changelog_impact_matrix/case_01.json`
- Special handling: derive `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready` for this localization/release case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_75_changelog_impact_matrix/case_02.json`
- Special handling: derive `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready` for this localization/release case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_75_changelog_impact_matrix/case_03.json`
- Special handling: derive `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready` for this localization/release case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_75_changelog_impact_matrix/case_04.json`
- Special handling: derive `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready` for this localization/release case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_75_changelog_impact_matrix/case_05.json`
- Special handling: derive `placeholder_errors, glossary_violations, release_sections, flag_actions, publish_ready` for this localization/release case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `placeholder_errors` with the correct value.
- [ ] Each report includes `glossary_violations` with the correct value.
- [ ] Each report includes `release_sections` with the correct value.
- [ ] Each report includes `flag_actions` with the correct value.
- [ ] Each report includes `publish_ready` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'flag_actions': ['remove_stale_flag'],
             'glossary_violations': ['workspace', 'checkout'],
             'placeholder_errors': ['LOC-01-02'],
             'publish_ready': True,
             'release_sections': ['features', 'fixes', 'known_issues']},
 'case_02': {'flag_actions': ['keep_guardrail', 'schedule_cleanup'],
             'glossary_violations': ['workspace'],
             'placeholder_errors': ['LOC-02-01', 'LOC-02-03'],
             'publish_ready': True,
             'release_sections': ['features', 'fixes']},
 'case_03': {'flag_actions': ['remove_stale_flag'],
             'glossary_violations': ['workspace', 'checkout'],
             'placeholder_errors': ['LOC-03-02'],
             'publish_ready': False,
             'release_sections': ['features', 'fixes', 'known_issues']},
 'case_04': {'flag_actions': ['keep_guardrail', 'schedule_cleanup'],
             'glossary_violations': ['workspace'],
             'placeholder_errors': ['LOC-04-01', 'LOC-04-03'],
             'publish_ready': True,
             'release_sections': ['features', 'fixes']},
 'case_05': {'flag_actions': ['remove_stale_flag'],
             'glossary_violations': ['workspace', 'checkout'],
             'placeholder_errors': ['LOC-05-02'],
             'publish_ready': True,
             'release_sections': ['features', 'fixes', 'known_issues']}}
    required_fields = ['placeholder_errors',
 'glossary_violations',
 'release_sections',
 'flag_actions',
 'publish_ready']
    numeric_fields = []
    list_fields = ['placeholder_errors',
 'glossary_violations',
 'release_sections',
 'flag_actions']
    dict_fields = []
    bool_fields = ['publish_ready']
    text_fields = []
    family_marker = "localization_release_grader"
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
