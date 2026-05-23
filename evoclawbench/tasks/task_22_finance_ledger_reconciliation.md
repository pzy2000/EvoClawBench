---
id: task_22_finance_ledger_reconciliation
name: Finance Ledger Reconciliation
category: finance_ops
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: finance
task_family: Finance
grader_family: finance
workspace_files:
  - assets/generated_tasks/task_22_finance_ledger_reconciliation/case_01.csv
  - assets/generated_tasks/task_22_finance_ledger_reconciliation/case_02.csv
  - assets/generated_tasks/task_22_finance_ledger_reconciliation/case_03.csv
  - assets/generated_tasks/task_22_finance_ledger_reconciliation/case_04.csv
  - assets/generated_tasks/task_22_finance_ledger_reconciliation/case_05.csv
---

# Finance Ledger Reconciliation

Process five fixture-backed finance cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic finance ledger reconciliation fixture files under `assets/generated_tasks/task_22_finance_ledger_reconciliation/`.
For each input file, reconcile totals, identify exceptions, and verify currency and tax treatment and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `ledger_total, exception_ids, currencies, tax_total, balanced`.
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
- Input: `assets/generated_tasks/task_22_finance_ledger_reconciliation/case_01.csv`
- Special handling: derive `ledger_total, exception_ids, currencies, tax_total, balanced` for this finance case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_22_finance_ledger_reconciliation/case_02.csv`
- Special handling: derive `ledger_total, exception_ids, currencies, tax_total, balanced` for this finance case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_22_finance_ledger_reconciliation/case_03.csv`
- Special handling: derive `ledger_total, exception_ids, currencies, tax_total, balanced` for this finance case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_22_finance_ledger_reconciliation/case_04.csv`
- Special handling: derive `ledger_total, exception_ids, currencies, tax_total, balanced` for this finance case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_22_finance_ledger_reconciliation/case_05.csv`
- Special handling: derive `ledger_total, exception_ids, currencies, tax_total, balanced` for this finance case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `ledger_total` with the correct value.
- [ ] Each report includes `exception_ids` with the correct value.
- [ ] Each report includes `currencies` with the correct value.
- [ ] Each report includes `tax_total` with the correct value.
- [ ] Each report includes `balanced` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'balanced': True,
             'currencies': ['USD'],
             'exception_ids': ['FLR-01-03', 'FLR-01-04'],
             'ledger_total': 1337.5,
             'tax_total': 93.25},
 'case_02': {'balanced': True,
             'currencies': ['EUR', 'USD'],
             'exception_ids': ['FLR-02-03', 'FLR-02-04'],
             'ledger_total': 1475.0,
             'tax_total': 102.5},
 'case_03': {'balanced': False,
             'currencies': ['USD'],
             'exception_ids': ['FLR-03-03', 'FLR-03-04'],
             'ledger_total': 1612.5,
             'tax_total': 111.75},
 'case_04': {'balanced': True,
             'currencies': ['EUR', 'USD'],
             'exception_ids': ['FLR-04-03', 'FLR-04-04'],
             'ledger_total': 1750.0,
             'tax_total': 121.0},
 'case_05': {'balanced': True,
             'currencies': ['USD'],
             'exception_ids': ['FLR-05-03', 'FLR-05-04'],
             'ledger_total': 1887.5,
             'tax_total': 130.25}}
    required_fields = ['ledger_total', 'exception_ids', 'currencies', 'tax_total', 'balanced']
    numeric_fields = ['ledger_total', 'tax_total']
    list_fields = ['exception_ids', 'currencies']
    dict_fields = []
    bool_fields = ['balanced']
    text_fields = []
    family_marker = "finance_grader"
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
