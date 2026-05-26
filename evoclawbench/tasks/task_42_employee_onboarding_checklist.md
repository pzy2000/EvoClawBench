---
id: task_42_employee_onboarding_checklist
name: Employee Onboarding Checklist
category: hr_education
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: hr_education
task_family: HR/Education
grader_family: hr_education
workspace_files:
  - assets/generated_tasks/task_42_employee_onboarding_checklist/case_01.json
  - assets/generated_tasks/task_42_employee_onboarding_checklist/case_02.json
  - assets/generated_tasks/task_42_employee_onboarding_checklist/case_03.json
  - assets/generated_tasks/task_42_employee_onboarding_checklist/case_04.json
  - assets/generated_tasks/task_42_employee_onboarding_checklist/case_05.json
---

# Employee Onboarding Checklist

Process five hard-mode fixture-backed hr/education cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode employee onboarding checklist fixture files under `assets/generated_tasks/task_42_employee_onboarding_checklist/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `completion_rate`, `missing_items`, `calibrated_scores`, `assigned_track`, `intervention_ids`.
Use the channel map below to translate evidence channels into output fields:

- `N1` -> `completion_rate` (numeric)
- `L1` -> `missing_items` (list)
- `D1` -> `calibrated_scores` (dict)
- `T1` -> `assigned_track` (text)
- `L2` -> `intervention_ids` (list)

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
- Input: `assets/generated_tasks/task_42_employee_onboarding_checklist/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids for this hr/education case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_42_employee_onboarding_checklist/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids for this hr/education case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_42_employee_onboarding_checklist/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids for this hr/education case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_42_employee_onboarding_checklist/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids for this hr/education case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_42_employee_onboarding_checklist/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive completion_rate, missing_items, calibrated_scores, assigned_track, intervention_ids for this hr/education case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `completion_rate` with the correctly derived value.
- [ ] Each report includes `missing_items` with the correctly derived value.
- [ ] Each report includes `calibrated_scores` with the correctly derived value.
- [ ] Each report includes `assigned_track` with the correctly derived value.
- [ ] Each report includes `intervention_ids` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'assigned_track': 'standard',
             'calibrated_scores': {'process': 6, 'technical': 5},
             'completion_rate': 30.88,
             'intervention_ids': ['INTIDS-01-103',
                                  'INTIDS-01-25',
                                  'INTIDS-01-45',
                                  'INTIDS-01-93'],
             'missing_items': ['MISITE-01-29', 'MISITE-01-49', 'MISITE-01-78']},
 'case_02': {'assigned_track': 'accelerated',
             'calibrated_scores': {'evidence': 8, 'process': 7, 'technical': 7},
             'completion_rate': 0.82,
             'intervention_ids': ['INTIDS-02-103',
                                  'INTIDS-02-25',
                                  'INTIDS-02-45',
                                  'INTIDS-02-93'],
             'missing_items': ['MISITE-02-29', 'MISITE-02-49', 'MISITE-02-78']},
 'case_03': {'assigned_track': 'accelerated',
             'calibrated_scores': {'evidence': 8, 'process': 1, 'technical': 7},
             'completion_rate': 100.02,
             'intervention_ids': ['INTIDS-03-103',
                                  'INTIDS-03-25',
                                  'INTIDS-03-45',
                                  'INTIDS-03-93'],
             'missing_items': ['MISITE-03-29', 'MISITE-03-49', 'MISITE-03-78']},
 'case_04': {'assigned_track': 'accelerated',
             'calibrated_scores': {'evidence': 4, 'process': 7, 'technical': 9},
             'completion_rate': 7.25,
             'intervention_ids': ['INTIDS-04-103',
                                  'INTIDS-04-25',
                                  'INTIDS-04-45',
                                  'INTIDS-04-93'],
             'missing_items': ['MISITE-04-29', 'MISITE-04-49', 'MISITE-04-78']},
 'case_05': {'assigned_track': 'intervention',
             'calibrated_scores': {'evidence': 2, 'process': 6, 'technical': 1},
             'completion_rate': 59.29,
             'intervention_ids': ['INTIDS-05-103',
                                  'INTIDS-05-25',
                                  'INTIDS-05-45',
                                  'INTIDS-05-93'],
             'missing_items': ['MISITE-05-29', 'MISITE-05-49', 'MISITE-05-78']}}
    required_fields = ['completion_rate', 'missing_items', 'calibrated_scores', 'assigned_track', 'intervention_ids']
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
