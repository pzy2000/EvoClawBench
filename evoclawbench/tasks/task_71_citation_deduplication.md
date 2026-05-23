---
id: task_71_citation_deduplication
name: Citation Deduplication
category: research_media
grading_type: automated
timeout_seconds: 600
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

Process five fixture-backed research/media cases. The files share a workflow pattern but require domain-specific parsing, normalization, and reporting.

---

## Prompt

You have 5 synthetic citation deduplication fixture files under `assets/generated_tasks/task_71_citation_deduplication/`.
For each input file, synthesize evidence, verify claims, and deduplicate source citations and save `outputs/case_XX_report.json`.

Each report must be valid JSON with these fields: `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence`.
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
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_01.html`
- Special handling: derive `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence` for this research/media case.
- Expected output: `outputs/case_01_report.json`

### Sub-Problem 2: Partner Portal Export
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_02.html`
- Special handling: derive `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence` for this research/media case.
- Expected output: `outputs/case_02_report.json`

### Sub-Problem 3: Back Office Queue
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_03.html`
- Special handling: derive `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence` for this research/media case.
- Expected output: `outputs/case_03_report.json`

### Sub-Problem 4: Legacy System Extract
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_04.html`
- Special handling: derive `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence` for this research/media case.
- Expected output: `outputs/case_04_report.json`

### Sub-Problem 5: Daily Exception Batch
- Input: `assets/generated_tasks/task_71_citation_deduplication/case_05.html`
- Special handling: derive `supported_claims, unsupported_claims, source_count, duplicate_citations, confidence` for this research/media case.
- Expected output: `outputs/case_05_report.json`

---

## Grading Criteria

- [ ] All five `outputs/case_XX_report.json` files exist.
- [ ] Each report is valid JSON and contains the required family-specific fields.
- [ ] Each report includes `supported_claims` with the correct value.
- [ ] Each report includes `unsupported_claims` with the correct value.
- [ ] Each report includes `source_count` with the correct value.
- [ ] Each report includes `duplicate_citations` with the correct value.
- [ ] Each report includes `confidence` with the correct value.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {'case_01': {'confidence': 0.75,
             'duplicate_citations': ['SRC-01-DUP'],
             'source_count': 4,
             'supported_claims': ['CD-01-01', 'CD-01-02'],
             'unsupported_claims': ['CD-01-04']},
 'case_02': {'confidence': 0.78,
             'duplicate_citations': [],
             'source_count': 5,
             'supported_claims': ['CD-02-01', 'CD-02-02'],
             'unsupported_claims': ['CD-02-04']},
 'case_03': {'confidence': 0.81,
             'duplicate_citations': ['SRC-03-DUP'],
             'source_count': 6,
             'supported_claims': ['CD-03-01', 'CD-03-02'],
             'unsupported_claims': ['CD-03-04']},
 'case_04': {'confidence': 0.84,
             'duplicate_citations': [],
             'source_count': 7,
             'supported_claims': ['CD-04-01', 'CD-04-02'],
             'unsupported_claims': ['CD-04-04']},
 'case_05': {'confidence': 0.87,
             'duplicate_citations': ['SRC-05-DUP'],
             'source_count': 8,
             'supported_claims': ['CD-05-01', 'CD-05-02'],
             'unsupported_claims': ['CD-05-04']}}
    required_fields = ['supported_claims',
 'unsupported_claims',
 'source_count',
 'duplicate_citations',
 'confidence']
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
