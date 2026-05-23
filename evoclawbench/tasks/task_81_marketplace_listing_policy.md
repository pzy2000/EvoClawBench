---
id: task_81_marketplace_listing_policy
name: Marketplace Listing Policy
category: commerce_food
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: commerce_food
task_family: Commerce/Food
grader_family: commerce_food
workspace_files:
  - assets/generated_tasks/task_81_marketplace_listing_policy/case_01.csv
  - assets/generated_tasks/task_81_marketplace_listing_policy/case_02.csv
  - assets/generated_tasks/task_81_marketplace_listing_policy/case_03.csv
  - assets/generated_tasks/task_81_marketplace_listing_policy/case_04.csv
  - assets/generated_tasks/task_81_marketplace_listing_policy/case_05.csv
---

# Marketplace Listing Policy

Process five fixture-backed commerce/food cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic marketplace listing policy fixture files under `assets/generated_tasks/task_81_marketplace_listing_policy/`.
For each input file, normalize commerce or food-service records and identify refunds, policy, or inspection issues and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action`.
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
- Input: `assets/generated_tasks/task_81_marketplace_listing_policy/case_01.csv`
- Special handling: derive `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action` for this commerce/food case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_81_marketplace_listing_policy/case_02.csv`
- Special handling: derive `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action` for this commerce/food case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_81_marketplace_listing_policy/case_03.csv`
- Special handling: derive `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action` for this commerce/food case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_81_marketplace_listing_policy/case_04.csv`
- Special handling: derive `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action` for this commerce/food case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_81_marketplace_listing_policy/case_05.csv`
- Special handling: derive `normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action` for this commerce/food case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `normalized_skus` with the correct value.
- [ ] Each report includes `refund_ids` with the correct value.
- [ ] Each report includes `inspection_score` with the correct value.
- [ ] Each report includes `policy_violations` with the correct value.
- [ ] Each report includes `recommended_action` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'inspection_score': 82,
             'normalized_skus': ['SKU-01-01', 'SKU-01-02', 'SKU-01-03'],
             'policy_violations': ['missing_allergen_label'],
             'recommended_action': 'manual_review',
             'refund_ids': ['MLP-01-02', 'MLP-01-03']},
 'case_02': {'inspection_score': 84,
             'normalized_skus': ['SKU-02-01', 'SKU-02-02', 'SKU-02-03'],
             'policy_violations': ['prohibited_claim', 'late_delivery'],
             'recommended_action': 'auto_approve_with_note',
             'refund_ids': ['MLP-02-02', 'MLP-02-03']},
 'case_03': {'inspection_score': 86,
             'normalized_skus': ['SKU-03-01', 'SKU-03-02', 'SKU-03-03'],
             'policy_violations': ['missing_allergen_label'],
             'recommended_action': 'manual_review',
             'refund_ids': ['MLP-03-02', 'MLP-03-03']},
 'case_04': {'inspection_score': 88,
             'normalized_skus': ['SKU-04-01', 'SKU-04-02', 'SKU-04-03'],
             'policy_violations': ['prohibited_claim', 'late_delivery'],
             'recommended_action': 'auto_approve_with_note',
             'refund_ids': ['MLP-04-02', 'MLP-04-03']},
 'case_05': {'inspection_score': 90,
             'normalized_skus': ['SKU-05-01', 'SKU-05-02', 'SKU-05-03'],
             'policy_violations': ['missing_allergen_label'],
             'recommended_action': 'manual_review',
             'refund_ids': ['MLP-05-02', 'MLP-05-03']}}
    required_fields = ['normalized_skus',
 'refund_ids',
 'inspection_score',
 'policy_violations',
 'recommended_action']
    numeric_fields = ['inspection_score']
    list_fields = ['normalized_skus', 'refund_ids', 'policy_violations']
    dict_fields = []
    bool_fields = []
    text_fields = ['recommended_action']
    family_marker = "commerce_food_grader"
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
