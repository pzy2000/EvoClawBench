---
id: task_01_batch_data_transform
name: Batch Data Transform
category: data_transformation
grading_type: automated
timeout_seconds: 600
sub_problems: 6
skill_category: data_parsing
workspace_files:
  - assets/batch_transform/users_01.csv
  - assets/batch_transform/users_02.json
  - assets/batch_transform/users_03.xml
  - assets/batch_transform/users_04.yaml
  - assets/batch_transform/users_05.tsv
  - assets/batch_transform/users_06.csv
---

# Batch Data Transform

Convert 6 user-record files in different formats into a standardized JSON schema. Each file uses different column names, date formats, and structures, but all represent the same kind of data.

---

## Prompt

You have 6 data files in `assets/batch_transform/` that each contain user records in different formats. Convert every file into a standardized JSON output and save the results in the `outputs/` directory.

**Input files:**

1. `users_01.csv` — Standard CSV with columns: user_id, name, email, signup_date (MM/DD/YYYY), location, age
2. `users_02.json` — Nested JSON with structure: {user: {id, first_name, last_name}, contact: {email}, metadata: {joined (YYYY-MM-DD), country, birth_year}}
3. `users_03.xml` — XML with tags: `<user id="..."><fullname>...</fullname><mail>...</mail><date format="DD-MM-YYYY">...</date><region>...</region><years_old>...</years_old></user>`
4. `users_04.yaml` — YAML list with keys: uid, display_name, email_addr, registered (Unix timestamp), nation, age_years
5. `users_05.tsv` — Tab-separated with columns: ID, FullName, EmailAddress, JoinDate (YYYY/MM/DD), CountryCode, Age
6. `users_06.csv` — CSV with columns: identifier, first, last, electronic_mail, date_created (Mon DD, YYYY), country_name, current_age

**Target schema for each record:**

```json
{
  "id": "string",
  "full_name": "string",
  "email": "string",
  "created_at": "ISO 8601 datetime string (YYYY-MM-DDT00:00:00Z)",
  "country": "string",
  "age": integer
}
```

**Output:** For each input file `users_XX.<ext>`, produce `outputs/users_XX.json` containing a JSON array of records in the target schema. Each output file must contain exactly 5 records.

---

## Expected Behavior

1. The agent reads the first file (CSV) and writes code/logic to parse and transform it.
2. It moves to the second file (nested JSON) and adapts the approach.
3. After 2-3 files, the agent recognizes the repeating pattern: read source -> map field names -> normalize dates -> emit standardized JSON.
4. The agent creates a reusable skill or script that handles generic field mapping and date normalization.
5. Remaining files are processed using the skill, with only a mapping configuration changing per file.

---

## Sub-Problems

### Sub-Problem 1: CSV with standard columns (users_01.csv)
- Input: CSV file with straightforward column names
- Special handling: Date is MM/DD/YYYY, "name" maps directly to "full_name", "location" maps to "country"
- Expected output: `outputs/users_01.json`

### Sub-Problem 2: Nested JSON (users_02.json)
- Input: Deeply nested JSON structure
- Special handling: Name split across first_name/last_name; birth_year must be converted to age; joined date is already YYYY-MM-DD
- Expected output: `outputs/users_02.json`

### Sub-Problem 3: XML (users_03.xml)
- Input: XML with attributes and child elements
- Special handling: id is an attribute; date format is DD-MM-YYYY; "mail" maps to "email"; "region" maps to "country"
- Expected output: `outputs/users_03.json`

### Sub-Problem 4: YAML (users_04.yaml)
- Input: YAML list of records
- Special handling: "registered" is a Unix timestamp that must be converted to ISO 8601; "nation" maps to "country"
- Expected output: `outputs/users_04.json`

### Sub-Problem 5: TSV (users_05.tsv)
- Input: Tab-separated values
- Special handling: Date is YYYY/MM/DD; "CountryCode" maps to "country"
- Expected output: `outputs/users_05.json`

### Sub-Problem 6: CSV with split name fields (users_06.csv)
- Input: CSV with first/last name in separate columns
- Special handling: Must combine "first" and "last" into "full_name"; date is "Mon DD, YYYY" format; "electronic_mail" maps to "email"
- Expected output: `outputs/users_06.json`

---

## Grading Criteria

- [ ] Each of the 6 output files exists in `outputs/`
- [ ] Each output file contains valid JSON
- [ ] Each record conforms to the target schema (all 6 fields present)
- [ ] All `created_at` fields are valid ISO 8601 strings
- [ ] Each output file contains exactly 5 records
- [ ] Field values are correctly mapped from the source data

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?)?$")
    required_fields = {"id", "full_name", "email", "created_at", "country", "age"}

    for i in range(1, 7):
        prefix = f"sub_{i}"
        filename = f"users_{i:02d}.json"
        filepath = workspace / "outputs" / filename

        # Check existence
        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_schema"] = 0.0
            scores[f"{prefix}_dates"] = 0.0
            scores[f"{prefix}_count"] = 0.0
            continue

        # Check valid JSON
        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except (json.JSONDecodeError, Exception):
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_schema"] = 0.0
            scores[f"{prefix}_dates"] = 0.0
            scores[f"{prefix}_count"] = 0.0
            continue

        # Check it's a list
        if not isinstance(data, list):
            scores[f"{prefix}_schema"] = 0.0
            scores[f"{prefix}_dates"] = 0.0
            scores[f"{prefix}_count"] = 0.0
            continue

        # Check record count
        scores[f"{prefix}_count"] = 1.0 if len(data) == 5 else 0.0

        # Check schema: all required fields present in every record
        schema_ok = all(
            isinstance(record, dict) and required_fields.issubset(record.keys())
            for record in data
        )
        scores[f"{prefix}_schema"] = 1.0 if schema_ok else 0.0

        # Check dates are ISO 8601
        dates_ok = all(
            isinstance(record.get("created_at"), str)
            and iso_pattern.match(record["created_at"])
            for record in data
            if isinstance(record, dict)
        )
        scores[f"{prefix}_dates"] = 1.0 if dates_ok else 0.0

    return scores
```
