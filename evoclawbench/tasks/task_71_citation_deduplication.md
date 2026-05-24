---
id: task_71_citation_deduplication
name: Citation Deduplication
category: research_media
grading_type: automated
timeout_seconds: 10
sub_problems: 5
skill_category: research_media
task_family: Research/Media
grader_family: research_media
workspace_files:
  - assets/generated_tasks/task_71_citation_deduplication/case_01.html
  - assets/generated_tasks/task_71_citation_deduplication/case_02.html
  - assets/generated_tasks/task_71_citation_deduplication/case_03.html
  - assets/generated_tasks/task_71_citation_deduplication/case_04.html
  - assets/generated_tasks/task_71_citation_deduplication/case_05.html
---

# Citation Deduplication

Process five hard-mode fixture-backed research/media cases. Each case includes competing evidence packets, stale revisions, and decoy records; only the selected packet should drive the final report.

---

## Prompt

You have 5 hard-mode citation deduplication fixture files under `assets/generated_tasks/task_71_citation_deduplication/`.
For each input file, derive the required report from the evidence protocol and save `outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: `supported_claims`, `unsupported_claims`, `source_count`, `duplicate_citations`, `confidence`.
Use the channel map below to translate evidence channels into output fields:

- `L1` -> `supported_claims` (list)
- `L2` -> `unsupported_claims` (list)
- `N1` -> `source_count` (numeric)
- `L3` -> `duplicate_citations` (list)
- `N2` -> `confidence` (numeric)

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
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_01.html`
- Special handling: select the valid evidence packet, discard all decoys, and derive supported_claims, unsupported_claims, source_count, duplicate_citations, confidence for this research/media case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_02.html`
- Special handling: select the valid evidence packet, discard all decoys, and derive supported_claims, unsupported_claims, source_count, duplicate_citations, confidence for this research/media case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_03.html`
- Special handling: select the valid evidence packet, discard all decoys, and derive supported_claims, unsupported_claims, source_count, duplicate_citations, confidence for this research/media case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_04.html`
- Special handling: select the valid evidence packet, discard all decoys, and derive supported_claims, unsupported_claims, source_count, duplicate_citations, confidence for this research/media case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_05.html`
- Special handling: select the valid evidence packet, discard all decoys, and derive supported_claims, unsupported_claims, source_count, duplicate_citations, confidence for this research/media case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains every required field.
- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.
- [ ] Each report includes `supported_claims` with the correctly derived value.
- [ ] Each report includes `unsupported_claims` with the correctly derived value.
- [ ] Each report includes `source_count` with the correctly derived value.
- [ ] Each report includes `duplicate_citations` with the correctly derived value.
- [ ] Each report includes `confidence` with the correctly derived value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'confidence': 22.82,
             'duplicate_citations': ['DUPCIT-01-13',
                                     'DUPCIT-01-33',
                                     'DUPCIT-01-39',
                                     'DUPCIT-01-99'],
             'source_count': 2,
             'supported_claims': ['SUPCLA-01-27', 'SUPCLA-01-62', 'SUPCLA-01-71'],
             'unsupported_claims': ['UNSCLA-01-34',
                                    'UNSCLA-01-64',
                                    'UNSCLA-01-67',
                                    'UNSCLA-01-79']},
 'case_02': {'confidence': 22.96,
             'duplicate_citations': ['DUPCIT-02-13',
                                     'DUPCIT-02-33',
                                     'DUPCIT-02-39',
                                     'DUPCIT-02-99'],
             'source_count': 20,
             'supported_claims': ['SUPCLA-02-27', 'SUPCLA-02-62', 'SUPCLA-02-71'],
             'unsupported_claims': ['UNSCLA-02-34',
                                    'UNSCLA-02-64',
                                    'UNSCLA-02-67',
                                    'UNSCLA-02-79']},
 'case_03': {'confidence': 8.13,
             'duplicate_citations': ['DUPCIT-03-13',
                                     'DUPCIT-03-33',
                                     'DUPCIT-03-39',
                                     'DUPCIT-03-99'],
             'source_count': 4,
             'supported_claims': ['SUPCLA-03-27', 'SUPCLA-03-62', 'SUPCLA-03-71'],
             'unsupported_claims': ['UNSCLA-03-34',
                                    'UNSCLA-03-64',
                                    'UNSCLA-03-67',
                                    'UNSCLA-03-79']},
 'case_04': {'confidence': 66.54,
             'duplicate_citations': ['DUPCIT-04-13',
                                     'DUPCIT-04-33',
                                     'DUPCIT-04-39',
                                     'DUPCIT-04-99'],
             'source_count': 21,
             'supported_claims': ['SUPCLA-04-27', 'SUPCLA-04-62', 'SUPCLA-04-71'],
             'unsupported_claims': ['UNSCLA-04-34',
                                    'UNSCLA-04-64',
                                    'UNSCLA-04-67',
                                    'UNSCLA-04-79']},
 'case_05': {'confidence': 7.8,
             'duplicate_citations': ['DUPCIT-05-13',
                                     'DUPCIT-05-33',
                                     'DUPCIT-05-39',
                                     'DUPCIT-05-99'],
             'source_count': 28,
             'supported_claims': ['SUPCLA-05-27', 'SUPCLA-05-62', 'SUPCLA-05-71'],
             'unsupported_claims': ['UNSCLA-05-34',
                                    'UNSCLA-05-64',
                                    'UNSCLA-05-67',
                                    'UNSCLA-05-79']}}
    required_fields = ['supported_claims', 'unsupported_claims', 'source_count', 'duplicate_citations', 'confidence']
    numeric_fields = ['source_count', 'confidence']
    list_fields = ['supported_claims', 'unsupported_claims', 'duplicate_citations']
    dict_fields = []
    bool_fields = []
    text_fields = []
    family_marker = "research_media_grader"
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
