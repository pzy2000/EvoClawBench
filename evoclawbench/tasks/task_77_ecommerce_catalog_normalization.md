---
id: task_77_ecommerce_catalog_normalization
name: Ecommerce Catalog Normalization
category: commerce_food
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: commerce_food
task_family: Commerce/Food
grader_family: commerce_food
workspace_files:
  - assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_01.csv
  - assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_02.csv
  - assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_03.csv
  - assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_04.csv
  - assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_05.csv
---

# Ecommerce Catalog Normalization

Process five hard-mode fixture-backed commerce/food cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode ecommerce catalog normalization fixture files under `assets/generated_tasks/task_77_ecommerce_catalog_normalization/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `normalized_skus`, `refund_ids`, `inspection_score`, `policy_violations`, `recommended_action`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `normalized_skus` (list)
- `L2` -> `refund_ids` (list)
- `N1` -> `inspection_score` (numeric)
- `L3` -> `policy_violations` (list)
- `T1` -> `recommended_action` (text)

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
- Input: `assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_01.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action for this commerce/food case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_02.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action for this commerce/food case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_03.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action for this commerce/food case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_04.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action for this commerce/food case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_77_ecommerce_catalog_normalization/case_05.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive normalized_skus, refund_ids, inspection_score, policy_violations, recommended_action for this commerce/food case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `normalized_skus` with the correctly derived value.
- [ ] Each report includes `refund_ids` with the correctly derived value.
- [ ] Each report includes `inspection_score` with the correctly derived value.
- [ ] Each report includes `policy_violations` with the correctly derived value.
- [ ] Each report includes `recommended_action` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'inspection_score': 30.17,
             'normalized_skus': ['NORSKU-01-103',
                                 'NORSKU-01-38',
                                 'NORSKU-01-62',
                                 'NORSKU-01-81'],
             'policy_violations': ['POLVIO-01-103',
                                   'POLVIO-01-38',
                                   'POLVIO-01-51',
                                   'POLVIO-01-60'],
             'recommended_action': 'recact_secondary',
             'refund_ids': ['REFIDS-01-31', 'REFIDS-01-72', 'REFIDS-01-90', 'REFIDS-01-93']},
 'case_02': {'inspection_score': 7.46,
             'normalized_skus': ['NORSKU-02-103',
                                 'NORSKU-02-38',
                                 'NORSKU-02-62',
                                 'NORSKU-02-81'],
             'policy_violations': ['POLVIO-02-103',
                                   'POLVIO-02-38',
                                   'POLVIO-02-51',
                                   'POLVIO-02-60'],
             'recommended_action': 'recact_secondary',
             'refund_ids': ['REFIDS-02-31', 'REFIDS-02-72', 'REFIDS-02-90', 'REFIDS-02-93']},
 'case_03': {'inspection_score': 104.52,
             'normalized_skus': ['NORSKU-03-103',
                                 'NORSKU-03-38',
                                 'NORSKU-03-62',
                                 'NORSKU-03-81'],
             'policy_violations': ['POLVIO-03-103',
                                   'POLVIO-03-38',
                                   'POLVIO-03-51',
                                   'POLVIO-03-60'],
             'recommended_action': 'recact_secondary',
             'refund_ids': ['REFIDS-03-31', 'REFIDS-03-72', 'REFIDS-03-90', 'REFIDS-03-93']},
 'case_04': {'inspection_score': 73.98,
             'normalized_skus': ['NORSKU-04-103',
                                 'NORSKU-04-38',
                                 'NORSKU-04-62',
                                 'NORSKU-04-81'],
             'policy_violations': ['POLVIO-04-103',
                                   'POLVIO-04-38',
                                   'POLVIO-04-51',
                                   'POLVIO-04-60'],
             'recommended_action': 'recact_primary',
             'refund_ids': ['REFIDS-04-31', 'REFIDS-04-72', 'REFIDS-04-90', 'REFIDS-04-93']},
 'case_05': {'inspection_score': 54.75,
             'normalized_skus': ['NORSKU-05-103',
                                 'NORSKU-05-38',
                                 'NORSKU-05-62',
                                 'NORSKU-05-81'],
             'policy_violations': ['POLVIO-05-103',
                                   'POLVIO-05-38',
                                   'POLVIO-05-51',
                                   'POLVIO-05-60'],
             'recommended_action': 'recact_primary',
             'refund_ids': ['REFIDS-05-31', 'REFIDS-05-72', 'REFIDS-05-90', 'REFIDS-05-93']}}
    required_fields = ['normalized_skus', 'refund_ids', 'inspection_score', 'policy_violations', 'recommended_action']
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
