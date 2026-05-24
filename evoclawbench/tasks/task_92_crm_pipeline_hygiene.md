---
id: task_92_crm_pipeline_hygiene
name: CRM Pipeline Hygiene
category: crm_executive
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: crm_exec
task_family: CRM/Executive
grader_family: crm_exec
workspace_files:
  - assets/generated_tasks/task_92_crm_pipeline_hygiene/case_01.csv
  - assets/generated_tasks/task_92_crm_pipeline_hygiene/case_02.csv
  - assets/generated_tasks/task_92_crm_pipeline_hygiene/case_03.csv
  - assets/generated_tasks/task_92_crm_pipeline_hygiene/case_04.csv
  - assets/generated_tasks/task_92_crm_pipeline_hygiene/case_05.csv
---

# CRM Pipeline Hygiene

Process five hard-mode fixture-backed crm/executive cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode crm pipeline hygiene fixture files under `assets/generated_tasks/task_92_crm_pipeline_hygiene/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `stale_opportunities`, `forecast_delta`, `campaign_errors`, `action_items`, `executive_summary`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `stale_opportunities` (list)
- `N1` -> `forecast_delta` (numeric)
- `L2` -> `campaign_errors` (list)
- `L3` -> `action_items` (list)
- `T1` -> `executive_summary` (text)

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
- Input: `assets/generated_tasks/task_92_crm_pipeline_hygiene/case_01.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive stale_opportunities, forecast_delta, campaign_errors, action_items, executive_summary for this crm/executive case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_92_crm_pipeline_hygiene/case_02.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive stale_opportunities, forecast_delta, campaign_errors, action_items, executive_summary for this crm/executive case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_92_crm_pipeline_hygiene/case_03.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive stale_opportunities, forecast_delta, campaign_errors, action_items, executive_summary for this crm/executive case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_92_crm_pipeline_hygiene/case_04.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive stale_opportunities, forecast_delta, campaign_errors, action_items, executive_summary for this crm/executive case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_92_crm_pipeline_hygiene/case_05.csv`
- Special handling: select the valid evidence packet, discard all decoys, and derive stale_opportunities, forecast_delta, campaign_errors, action_items, executive_summary for this crm/executive case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `stale_opportunities` with the correctly derived value.
- [ ] Each report includes `forecast_delta` with the correctly derived value.
- [ ] Each report includes `campaign_errors` with the correctly derived value.
- [ ] Each report includes `action_items` with the correctly derived value.
- [ ] Each report includes `executive_summary` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'action_items': ['ACTITE-01-102', 'ACTITE-01-106', 'ACTITE-01-52', 'ACTITE-01-70'],
             'campaign_errors': ['CAMERR-01-37',
                                 'CAMERR-01-39',
                                 'CAMERR-01-42',
                                 'CAMERR-01-71'],
             'executive_summary': 'exec_escalation',
             'forecast_delta': 14.98,
             'stale_opportunities': ['STAOPP-01-101',
                                     'STAOPP-01-13',
                                     'STAOPP-01-45',
                                     'STAOPP-01-80']},
 'case_02': {'action_items': ['ACTITE-02-102', 'ACTITE-02-106', 'ACTITE-02-52', 'ACTITE-02-70'],
             'campaign_errors': ['CAMERR-02-37',
                                 'CAMERR-02-39',
                                 'CAMERR-02-42',
                                 'CAMERR-02-71'],
             'executive_summary': 'exec_escalation',
             'forecast_delta': 48.44,
             'stale_opportunities': ['STAOPP-02-101',
                                     'STAOPP-02-13',
                                     'STAOPP-02-45',
                                     'STAOPP-02-80']},
 'case_03': {'action_items': ['ACTITE-03-102', 'ACTITE-03-106', 'ACTITE-03-52', 'ACTITE-03-70'],
             'campaign_errors': ['CAMERR-03-37',
                                 'CAMERR-03-39',
                                 'CAMERR-03-42',
                                 'CAMERR-03-71'],
             'executive_summary': 'routine_closeout',
             'forecast_delta': 42.12,
             'stale_opportunities': ['STAOPP-03-101',
                                     'STAOPP-03-13',
                                     'STAOPP-03-45',
                                     'STAOPP-03-80']},
 'case_04': {'action_items': ['ACTITE-04-102', 'ACTITE-04-106', 'ACTITE-04-52', 'ACTITE-04-70'],
             'campaign_errors': ['CAMERR-04-37',
                                 'CAMERR-04-39',
                                 'CAMERR-04-42',
                                 'CAMERR-04-71'],
             'executive_summary': 'exec_escalation',
             'forecast_delta': 39.84,
             'stale_opportunities': ['STAOPP-04-101',
                                     'STAOPP-04-13',
                                     'STAOPP-04-45',
                                     'STAOPP-04-80']},
 'case_05': {'action_items': ['ACTITE-05-102', 'ACTITE-05-106', 'ACTITE-05-52', 'ACTITE-05-70'],
             'campaign_errors': ['CAMERR-05-37',
                                 'CAMERR-05-39',
                                 'CAMERR-05-42',
                                 'CAMERR-05-71'],
             'executive_summary': 'routine_closeout',
             'forecast_delta': 7.25,
             'stale_opportunities': ['STAOPP-05-101',
                                     'STAOPP-05-13',
                                     'STAOPP-05-45',
                                     'STAOPP-05-80']}}
    required_fields = ['stale_opportunities',
 'forecast_delta',
 'campaign_errors',
 'action_items',
 'executive_summary']
    numeric_fields = ['forecast_delta']
    list_fields = ['stale_opportunities', 'campaign_errors', 'action_items']
    dict_fields = []
    bool_fields = []
    text_fields = ['executive_summary']
    family_marker = "crm_exec_grader"
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
