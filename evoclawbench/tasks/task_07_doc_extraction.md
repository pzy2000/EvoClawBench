---
id: task_07_doc_extraction
name: Document Data Extraction
category: data_extraction
grading_type: hybrid
grading_weights:
  automated: 0.5
  llm_judge: 0.5
timeout_seconds: 600
sub_problems: 5
skill_category: document_extraction
workspace_files:
  - assets/doc_extraction/invoice_001.txt
  - assets/doc_extraction/resume_001.txt
  - assets/doc_extraction/contract_001.txt
  - assets/doc_extraction/meeting_notes_001.txt
  - assets/doc_extraction/expense_report_001.txt
---

# Document Data Extraction

Extract structured JSON data from unstructured text documents of various types.

---

## Prompt

You have 5 text documents in `assets/doc_extraction/` representing different document types. Read each document and extract its key information into structured JSON files in `outputs/`.

**Files to process:**
1. `assets/doc_extraction/invoice_001.txt` → `outputs/invoice_001.json`
2. `assets/doc_extraction/resume_001.txt` → `outputs/resume_001.json`
3. `assets/doc_extraction/contract_001.txt` → `outputs/contract_001.json`
4. `assets/doc_extraction/meeting_notes_001.txt` → `outputs/meeting_notes_001.json`
5. `assets/doc_extraction/expense_report_001.txt` → `outputs/expense_report_001.json`

**Required schemas per document type:**

**Invoice:**
```json
{
  "vendor": {"name": "", "address": "", "phone": "", "email": "", "tax_id": ""},
  "client": {"name": "", "address": "", "contact_person": ""},
  "invoice_number": "",
  "invoice_date": "",
  "due_date": "",
  "payment_terms": "",
  "purchase_order": "",
  "line_items": [{"description": "", "quantity": 0, "unit_price": 0.0, "total": 0.0}],
  "subtotal": 0.0,
  "tax_rate": "",
  "tax_amount": 0.0,
  "grand_total": 0.0,
  "bank_details": {"bank": "", "account_name": "", "routing_number": "", "account_number": ""}
}
```

**Resume:**
```json
{
  "name": "",
  "title": "",
  "contact": {"email": "", "phone": "", "location": "", "linkedin": "", "github": ""},
  "summary": "",
  "work_experience": [{"title": "", "company": "", "start_date": "", "end_date": "", "highlights": []}],
  "education": [{"degree": "", "institution": "", "year": "", "details": ""}],
  "skills": {"languages": [], "frameworks": [], "cloud": [], "data": [], "tools": []},
  "certifications": []
}
```

**Contract:**
```json
{
  "title": "",
  "effective_date": "",
  "parties": [{"name": "", "address": "", "contact_person": "", "role": ""}],
  "scope_of_work": [],
  "total_value": 0.0,
  "payment_schedule": [{"milestone": "", "percentage": "", "amount": 0.0, "due_date": ""}],
  "duration": {"start_date": "", "end_date": "", "support_period": ""},
  "termination_notice_days": 0,
  "governing_law": "",
  "dispute_resolution": ""
}
```

**Meeting Notes:**
```json
{
  "project": "",
  "meeting_type": "",
  "date": "",
  "time": "",
  "location": "",
  "attendees": {"present": [], "absent": []},
  "agenda": [],
  "discussion_points": [{"topic": "", "summary": ""}],
  "action_items": [{"assignee": "", "task": "", "deadline": ""}],
  "decisions": [],
  "next_meeting": {"date": "", "time": "", "location": ""}
}
```

**Expense Report:**
```json
{
  "employee": {"name": "", "employee_id": "", "department": "", "manager": ""},
  "period": {"start_date": "", "end_date": ""},
  "purpose": "",
  "line_items": [{"date": "", "category": "", "description": "", "amount": 0.0}],
  "category_totals": {},
  "total": 0.0,
  "approval_status": "",
  "receipts_count": 0
}
```

---

## Expected Behavior

1. Agent reads the first document and manually extracts data into the required schema
2. Agent recognizes the repeating extraction pattern across documents
3. Agent creates a reusable skill for document data extraction
4. Agent applies the skill to all remaining documents
5. All outputs follow their respective schemas with accurate extracted values

---

## Sub-Problems

### Sub-Problem 1: Invoice Extraction
- Input: `assets/doc_extraction/invoice_001.txt` (business invoice with line items)
- Special handling: Numeric values must be parsed as numbers (not strings), line items as array of objects
- Expected output: `outputs/invoice_001.json`

### Sub-Problem 2: Resume Extraction
- Input: `assets/doc_extraction/resume_001.txt` (professional resume)
- Special handling: Work experience needs structured dates and bullet points, skills categorized
- Expected output: `outputs/resume_001.json`

### Sub-Problem 3: Contract Extraction
- Input: `assets/doc_extraction/contract_001.txt` (service agreement)
- Special handling: Payment schedule with percentages and amounts, multiple parties with roles
- Expected output: `outputs/contract_001.json`

### Sub-Problem 4: Meeting Notes Extraction
- Input: `assets/doc_extraction/meeting_notes_001.txt` (meeting minutes)
- Special handling: Action items with assignees and deadlines, attendee presence tracking
- Expected output: `outputs/meeting_notes_001.json`

### Sub-Problem 5: Expense Report Extraction
- Input: `assets/doc_extraction/expense_report_001.txt` (expense report with line items)
- Special handling: Date parsing, category totals, numeric amounts
- Expected output: `outputs/expense_report_001.json`

---

## Grading Criteria

- [ ] All 5 output files exist in outputs/
- [ ] All output files are valid JSON
- [ ] Invoice has line_items array and grand_total
- [ ] Resume has work_experience and education arrays
- [ ] Contract has parties array and payment_schedule
- [ ] Meeting notes have action_items with assignee and deadline
- [ ] Expense report has line_items and total amount
- [ ] Extracted values are accurate (match source documents)

---

## LLM Judge Rubric

You are evaluating a document data extraction task. The agent read 5 source documents and extracted structured JSON files in `outputs/`. The source documents and output files are provided above.

Score the following criteria from 0.0 to 1.0. Use 0.6–0.7 for acceptable extraction with minor errors. Reserve 1.0 for complete, accurate extraction.

- **value_accuracy**: Do the extracted values actually match the content of the source documents? Check key fields: invoice totals/dates/vendor, resume candidate name/experience/education, contract parties/dates/amounts, meeting action items/attendees, expense totals/categories. A score of 0.0 means most values are wrong or invented; 1.0 means all extracted values precisely match the source.
- **semantic_quality**: Are categorized or grouped fields correctly organized? This includes: resume `skills` categorized into languages/frameworks/cloud/tools, contract `scope_of_work` as meaningful bullet points, meeting `discussion_points` with correct topic/summary grouping, `action_items` with correct assignee/task/deadline structure. A score of 0.0 means groupings are meaningless or collapsed; 1.0 means all structured fields are well-organized and semantically accurate.
- **completeness**: Are all significant fields populated with actual data extracted from the document (not empty strings, null, 0, or placeholder text)? Consider fields like `bank_details` in invoice, `certifications` in resume, `payment_schedule` in contract, `decisions` in meeting notes, `category_totals` in expense report. A score of 0.0 means many fields are blank/default; 1.0 means all fields have meaningful extracted values.
- **overall_quality**: Holistic quality of extraction across all 5 document types — accuracy, completeness, and correct schema adherence.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    files_checks = [
        (
            "invoice_001.json",
            {
                "required_keys": ["line_items", "grand_total", "invoice_number", "vendor", "client"],
                "array_keys": ["line_items"],
                "min_array_len": {"line_items": 3},
                "numeric_keys": ["grand_total", "subtotal"],
            },
        ),
        (
            "resume_001.json",
            {
                "required_keys": ["name", "work_experience", "education", "skills"],
                "array_keys": ["work_experience", "education"],
                "min_array_len": {"work_experience": 2, "education": 1},
                "string_keys": ["name"],
            },
        ),
        (
            "contract_001.json",
            {
                "required_keys": ["parties", "effective_date", "total_value", "governing_law"],
                "array_keys": ["parties"],
                "min_array_len": {"parties": 2},
                "numeric_keys": ["total_value"],
            },
        ),
        (
            "meeting_notes_001.json",
            {
                "required_keys": ["date", "attendees", "action_items", "next_meeting"],
                "array_keys": ["action_items"],
                "min_array_len": {"action_items": 3},
            },
        ),
        (
            "expense_report_001.json",
            {
                "required_keys": ["employee", "line_items", "total"],
                "array_keys": ["line_items"],
                "min_array_len": {"line_items": 5},
                "numeric_keys": ["total"],
            },
        ),
    ]

    for idx, (filename, checks) in enumerate(files_checks, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / filename

        # Check file exists
        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_required_keys"] = 0.0
            scores[f"{prefix}_arrays"] = 0.0
            scores[f"{prefix}_values"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        # Check valid JSON
        try:
            with open(out_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception):
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_required_keys"] = 0.0
            scores[f"{prefix}_arrays"] = 0.0
            scores[f"{prefix}_values"] = 0.0
            continue

        scores[f"{prefix}_valid_json"] = 1.0

        # Check required keys
        required = checks.get("required_keys", [])
        found = sum(1 for k in required if k in data)
        scores[f"{prefix}_required_keys"] = round(found / len(required), 2) if required else 1.0

        # Check arrays exist and have minimum length
        array_keys = checks.get("array_keys", [])
        min_lens = checks.get("min_array_len", {})
        if array_keys:
            array_ok = 0
            for ak in array_keys:
                val = data.get(ak, [])
                if isinstance(val, list) and len(val) >= min_lens.get(ak, 1):
                    array_ok += 1
            scores[f"{prefix}_arrays"] = round(array_ok / len(array_keys), 2)
        else:
            scores[f"{prefix}_arrays"] = 1.0

        # Check that numeric keys are actually numbers and string keys are strings
        value_checks = 0
        value_total = 0
        for nk in checks.get("numeric_keys", []):
            value_total += 1
            val = data.get(nk)
            if isinstance(val, (int, float)):
                value_checks += 1
        for sk in checks.get("string_keys", []):
            value_total += 1
            val = data.get(sk)
            if isinstance(val, str) and len(val) > 0:
                value_checks += 1

        if value_total > 0:
            scores[f"{prefix}_values"] = round(value_checks / value_total, 2)
        else:
            scores[f"{prefix}_values"] = 1.0

    return scores
```
