---
id: task_35_insurance_prior_auth_review
name: Insurance Prior Auth Review
category: healthcare_admin
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: healthcare
task_family: Healthcare
grader_family: healthcare
workspace_files:
  - assets/generated_tasks/task_35_insurance_prior_auth_review/case_01.json
  - assets/generated_tasks/task_35_insurance_prior_auth_review/case_02.json
  - assets/generated_tasks/task_35_insurance_prior_auth_review/case_03.json
  - assets/generated_tasks/task_35_insurance_prior_auth_review/case_04.json
  - assets/generated_tasks/task_35_insurance_prior_auth_review/case_05.json
---

# Insurance Prior Auth Review

Process five hard-mode fixture-backed healthcare cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode insurance prior auth review fixture files under `assets/generated_tasks/task_35_insurance_prior_auth_review/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `eligible_ids`, `routing_queue`, `followup_ids`, `stockout_ids`, `urgent_count`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `eligible_ids` (list)
- `D1` -> `routing_queue` (dict)
- `L2` -> `followup_ids` (list)
- `L3` -> `stockout_ids` (list)
- `N1` -> `urgent_count` (numeric)

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
- Input: `assets/generated_tasks/task_35_insurance_prior_auth_review/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count for this healthcare case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_35_insurance_prior_auth_review/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count for this healthcare case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_35_insurance_prior_auth_review/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count for this healthcare case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_35_insurance_prior_auth_review/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count for this healthcare case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_35_insurance_prior_auth_review/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive eligible_ids, routing_queue, followup_ids, stockout_ids, urgent_count for this healthcare case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `eligible_ids` with the correctly derived value.
- [ ] Each report includes `routing_queue` with the correctly derived value.
- [ ] Each report includes `followup_ids` with the correctly derived value.
- [ ] Each report includes `stockout_ids` with the correctly derived value.
- [ ] Each report includes `urgent_count` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'eligible_ids': ['ELIIDS-01-11', 'ELIIDS-01-12', 'ELIIDS-01-13', 'ELIIDS-01-59'],
             'followup_ids': ['FOLIDS-01-28', 'FOLIDS-01-51', 'FOLIDS-01-66', 'FOLIDS-01-85'],
             'routing_queue': {'admin': 9, 'clinical': 3, 'pharmacy': 6},
             'stockout_ids': ['STOIDS-01-31', 'STOIDS-01-88', 'STOIDS-01-92', 'STOIDS-01-98'],
             'urgent_count': 37},
 'case_02': {'eligible_ids': ['ELIIDS-02-11', 'ELIIDS-02-12', 'ELIIDS-02-13', 'ELIIDS-02-59'],
             'followup_ids': ['FOLIDS-02-28', 'FOLIDS-02-51', 'FOLIDS-02-66', 'FOLIDS-02-85'],
             'routing_queue': {'admin': 8, 'clinical': 5, 'pharmacy': 4},
             'stockout_ids': ['STOIDS-02-31', 'STOIDS-02-88', 'STOIDS-02-92', 'STOIDS-02-98'],
             'urgent_count': 1},
 'case_03': {'eligible_ids': ['ELIIDS-03-11', 'ELIIDS-03-12', 'ELIIDS-03-13', 'ELIIDS-03-59'],
             'followup_ids': ['FOLIDS-03-28', 'FOLIDS-03-51', 'FOLIDS-03-66', 'FOLIDS-03-85'],
             'routing_queue': {'admin': 2, 'clinical': 4, 'pharmacy': 7},
             'stockout_ids': ['STOIDS-03-31', 'STOIDS-03-88', 'STOIDS-03-92', 'STOIDS-03-98'],
             'urgent_count': 30},
 'case_04': {'eligible_ids': ['ELIIDS-04-11', 'ELIIDS-04-12', 'ELIIDS-04-13', 'ELIIDS-04-59'],
             'followup_ids': ['FOLIDS-04-28', 'FOLIDS-04-51', 'FOLIDS-04-66', 'FOLIDS-04-85'],
             'routing_queue': {'admin': 5, 'clinical': 6, 'pharmacy': 8},
             'stockout_ids': ['STOIDS-04-31', 'STOIDS-04-88', 'STOIDS-04-92', 'STOIDS-04-98'],
             'urgent_count': 13},
 'case_05': {'eligible_ids': ['ELIIDS-05-11', 'ELIIDS-05-12', 'ELIIDS-05-13', 'ELIIDS-05-59'],
             'followup_ids': ['FOLIDS-05-28', 'FOLIDS-05-51', 'FOLIDS-05-66', 'FOLIDS-05-85'],
             'routing_queue': {'admin': 2, 'clinical': 5, 'pharmacy': 3},
             'stockout_ids': ['STOIDS-05-31', 'STOIDS-05-88', 'STOIDS-05-92', 'STOIDS-05-98'],
             'urgent_count': 8}}
    required_fields = ['eligible_ids', 'routing_queue', 'followup_ids', 'stockout_ids', 'urgent_count']
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
