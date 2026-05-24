---
id: task_50_bug_report_deduplication
name: Bug Report Deduplication
category: support_product
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: support_product
task_family: Support/Product
grader_family: support_product
workspace_files:
  - assets/generated_tasks/task_50_bug_report_deduplication/case_01.json
  - assets/generated_tasks/task_50_bug_report_deduplication/case_02.json
  - assets/generated_tasks/task_50_bug_report_deduplication/case_03.json
  - assets/generated_tasks/task_50_bug_report_deduplication/case_04.json
  - assets/generated_tasks/task_50_bug_report_deduplication/case_05.json
---

# Bug Report Deduplication

Process five hard-mode fixture-backed support/product cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode bug report deduplication fixture files under `assets/generated_tasks/task_50_bug_report_deduplication/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `priority_queue`, `duplicate_groups`, `themes`, `sla_breaches`, `reply_template`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `priority_queue` (list)
- `L2` -> `duplicate_groups` (list)
- `L3` -> `themes` (list)
- `L4` -> `sla_breaches` (list)
- `T1` -> `reply_template` (text)

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
- Input: `assets/generated_tasks/task_50_bug_report_deduplication/case_01.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_50_bug_report_deduplication/case_02.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_50_bug_report_deduplication/case_03.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_50_bug_report_deduplication/case_04.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_50_bug_report_deduplication/case_05.json`
- Special handling: select the valid evidence packet, discard all decoys, and derive priority_queue, duplicate_groups, themes, sla_breaches, reply_template for this support/product case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `priority_queue` with the correctly derived value.
- [ ] Each report includes `duplicate_groups` with the correctly derived value.
- [ ] Each report includes `themes` with the correctly derived value.
- [ ] Each report includes `sla_breaches` with the correctly derived value.
- [ ] Each report includes `reply_template` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'duplicate_groups': ['DUPGRO-01-105',
                                  'DUPGRO-01-55',
                                  'DUPGRO-01-63',
                                  'DUPGRO-01-78'],
             'priority_queue': ['PRIQUE-01-62', 'PRIQUE-01-65', 'PRIQUE-01-74', 'PRIQUE-01-94'],
             'reply_template': 'policy_clarification',
             'sla_breaches': ['SLABRE-01-106', 'SLABRE-01-27', 'SLABRE-01-44', 'SLABRE-01-53'],
             'themes': ['THE-01-101', 'THE-01-11', 'THE-01-16', 'THE-01-46']},
 'case_02': {'duplicate_groups': ['DUPGRO-02-105',
                                  'DUPGRO-02-55',
                                  'DUPGRO-02-63',
                                  'DUPGRO-02-78'],
             'priority_queue': ['PRIQUE-02-62', 'PRIQUE-02-65', 'PRIQUE-02-74', 'PRIQUE-02-94'],
             'reply_template': 'policy_clarification',
             'sla_breaches': ['SLABRE-02-106', 'SLABRE-02-27', 'SLABRE-02-44', 'SLABRE-02-53'],
             'themes': ['THE-02-101', 'THE-02-11', 'THE-02-16', 'THE-02-46']},
 'case_03': {'duplicate_groups': ['DUPGRO-03-105',
                                  'DUPGRO-03-55',
                                  'DUPGRO-03-63',
                                  'DUPGRO-03-78'],
             'priority_queue': ['PRIQUE-03-62', 'PRIQUE-03-65', 'PRIQUE-03-74', 'PRIQUE-03-94'],
             'reply_template': 'technical_escalation',
             'sla_breaches': ['SLABRE-03-106', 'SLABRE-03-27', 'SLABRE-03-44', 'SLABRE-03-53'],
             'themes': ['THE-03-101', 'THE-03-11', 'THE-03-16', 'THE-03-46']},
 'case_04': {'duplicate_groups': ['DUPGRO-04-105',
                                  'DUPGRO-04-55',
                                  'DUPGRO-04-63',
                                  'DUPGRO-04-78'],
             'priority_queue': ['PRIQUE-04-62', 'PRIQUE-04-65', 'PRIQUE-04-74', 'PRIQUE-04-94'],
             'reply_template': 'technical_escalation',
             'sla_breaches': ['SLABRE-04-106', 'SLABRE-04-27', 'SLABRE-04-44', 'SLABRE-04-53'],
             'themes': ['THE-04-101', 'THE-04-11', 'THE-04-16', 'THE-04-46']},
 'case_05': {'duplicate_groups': ['DUPGRO-05-105',
                                  'DUPGRO-05-55',
                                  'DUPGRO-05-63',
                                  'DUPGRO-05-78'],
             'priority_queue': ['PRIQUE-05-62', 'PRIQUE-05-65', 'PRIQUE-05-74', 'PRIQUE-05-94'],
             'reply_template': 'apology_credit',
             'sla_breaches': ['SLABRE-05-106', 'SLABRE-05-27', 'SLABRE-05-44', 'SLABRE-05-53'],
             'themes': ['THE-05-101', 'THE-05-11', 'THE-05-16', 'THE-05-46']}}
    required_fields = ['priority_queue', 'duplicate_groups', 'themes', 'sla_breaches', 'reply_template']
    numeric_fields = []
    list_fields = ['priority_queue', 'duplicate_groups', 'themes', 'sla_breaches']
    dict_fields = []
    bool_fields = []
    text_fields = ['reply_template']
    family_marker = "support_product_grader"
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
