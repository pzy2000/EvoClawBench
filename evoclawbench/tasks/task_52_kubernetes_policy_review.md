---
id: task_52_kubernetes_policy_review
name: Kubernetes Policy Review
category: devops
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: devops_sre
task_family: DevOps/SRE
grader_family: devops_sre
workspace_files:
  - assets/generated_tasks/task_52_kubernetes_policy_review/case_01.yaml
  - assets/generated_tasks/task_52_kubernetes_policy_review/case_02.yaml
  - assets/generated_tasks/task_52_kubernetes_policy_review/case_03.yaml
  - assets/generated_tasks/task_52_kubernetes_policy_review/case_04.yaml
  - assets/generated_tasks/task_52_kubernetes_policy_review/case_05.yaml
---

# Kubernetes Policy Review

Process five hard-mode fixture-backed devops/sre cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode kubernetes policy review fixture files under `assets/generated_tasks/task_52_kubernetes_policy_review/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `policy_violations`, `required_changes`, `slo_status`, `backup_passed`, `risk_score`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `policy_violations` (list)
- `L2` -> `required_changes` (list)
- `T1` -> `slo_status` (text)
- `B1` -> `backup_passed` (bool)
- `N1` -> `risk_score` (numeric)

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
- Input: `assets/generated_tasks/task_52_kubernetes_policy_review/case_01.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive policy_violations, required_changes, slo_status, backup_passed, risk_score for this devops/sre case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_52_kubernetes_policy_review/case_02.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive policy_violations, required_changes, slo_status, backup_passed, risk_score for this devops/sre case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_52_kubernetes_policy_review/case_03.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive policy_violations, required_changes, slo_status, backup_passed, risk_score for this devops/sre case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_52_kubernetes_policy_review/case_04.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive policy_violations, required_changes, slo_status, backup_passed, risk_score for this devops/sre case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_52_kubernetes_policy_review/case_05.yaml`
- Special handling: select the valid evidence packet, discard all decoys, and derive policy_violations, required_changes, slo_status, backup_passed, risk_score for this devops/sre case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `policy_violations` with the correctly derived value.
- [ ] Each report includes `required_changes` with the correctly derived value.
- [ ] Each report includes `slo_status` with the correctly derived value.
- [ ] Each report includes `backup_passed` with the correctly derived value.
- [ ] Each report includes `risk_score` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'backup_passed': True,
             'policy_violations': ['POLVIO-01-103', 'POLVIO-01-66', 'POLVIO-01-97'],
             'required_changes': ['REQCHA-01-105',
                                  'REQCHA-01-36',
                                  'REQCHA-01-37',
                                  'REQCHA-01-55'],
             'risk_score': 39.33,
             'slo_status': 'amber'},
 'case_02': {'backup_passed': False,
             'policy_violations': ['POLVIO-02-103', 'POLVIO-02-66', 'POLVIO-02-97'],
             'required_changes': ['REQCHA-02-105',
                                  'REQCHA-02-36',
                                  'REQCHA-02-37',
                                  'REQCHA-02-55'],
             'risk_score': 46.89,
             'slo_status': 'amber'},
 'case_03': {'backup_passed': True,
             'policy_violations': ['POLVIO-03-103', 'POLVIO-03-66', 'POLVIO-03-97'],
             'required_changes': ['REQCHA-03-105',
                                  'REQCHA-03-36',
                                  'REQCHA-03-37',
                                  'REQCHA-03-55'],
             'risk_score': 30.18,
             'slo_status': 'green'},
 'case_04': {'backup_passed': False,
             'policy_violations': ['POLVIO-04-103', 'POLVIO-04-66', 'POLVIO-04-97'],
             'required_changes': ['REQCHA-04-105',
                                  'REQCHA-04-36',
                                  'REQCHA-04-37',
                                  'REQCHA-04-55'],
             'risk_score': 1.19,
             'slo_status': 'amber'},
 'case_05': {'backup_passed': False,
             'policy_violations': ['POLVIO-05-103', 'POLVIO-05-66', 'POLVIO-05-97'],
             'required_changes': ['REQCHA-05-105',
                                  'REQCHA-05-36',
                                  'REQCHA-05-37',
                                  'REQCHA-05-55'],
             'risk_score': 7.25,
             'slo_status': 'red'}}
    required_fields = ['policy_violations', 'required_changes', 'slo_status', 'backup_passed', 'risk_score']
    numeric_fields = ['risk_score']
    list_fields = ['policy_violations', 'required_changes']
    dict_fields = []
    bool_fields = ['backup_passed']
    text_fields = ['slo_status']
    family_marker = "devops_sre_grader"
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
