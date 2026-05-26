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
6. Cross-document extraction audit → `outputs/extraction_audit.json`

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
  "bank_details": {"bank": "", "account_name": "", "routing_number": "", "account_number": ""},
  "revision": "",
  "excluded_line_items": [],
  "evidence_spans": []
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
  "certifications": [],
  "non_certification_notes": [],
  "evidence_spans": []
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
  "dispute_resolution": "",
  "amendments": [],
  "excluded_scope": [],
  "evidence_spans": []
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
  "next_meeting": {"date": "", "time": "", "location": ""},
  "name_disambiguation_notes": [],
  "evidence_spans": []
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
  "receipts_count": 0,
  "receipt_exceptions": [],
  "approved_exceptions": [],
  "evidence_spans": []
}
```

Normalize dates to ISO `YYYY-MM-DD` where a field is a date. When a document contains amendments, corrections, or policy notes, extract the final authoritative value and preserve the superseded value only in an explanatory field such as `amendments`, `excluded_line_items`, or `receipt_exceptions`.

Also create `outputs/extraction_audit.json` with:
```json
{
  "applied_corrections": [{"document": "", "source_note": "", "field": "", "final_value": "", "superseded_value": ""}],
  "rejected_candidates": [{"document": "", "candidate": "", "reason": ""}],
  "normalization_warnings": []
}
```

The audit file should explain why revised invoice totals and bank details were selected, why the final resume certification block supersedes the earlier block, why Amendment A changes the contract scope and value, why the later meeting action-item list replaces the draft list, and why the expense report has 17 attached receipts plus one missing receipt exception.

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
- **evidence_and_revision_handling**: Does the extraction cite source evidence and correctly handle amendments, corrections, duplicate names, policy exceptions, and superseded totals? Penalize invented certifications, using pre-amendment contract totals, keeping excluded invoice lines in final totals, confusing Marcus Johnson with Marcus Johnston, or dropping approved expense exceptions.
- **overall_quality**: Holistic quality of extraction across all 5 document types — accuracy, completeness, correct schema adherence, date normalization, and evidence support.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    def load_json(path):
        try:
            return json.loads(path.read_text())
        except Exception:
            return None

    def text_of(value):
        return json.dumps(value, sort_keys=True).lower()

    def close(actual, expected, tol=0.01):
        return isinstance(actual, (int, float)) and math.isclose(float(actual), expected, abs_tol=tol)

    invoice = load_json(workspace / "outputs" / "invoice_001.json")
    if isinstance(invoice, dict):
        items = text_of(invoice.get("line_items", []))
        bank = text_of(invoice.get("bank_details", {}))
        evidence = text_of(invoice.get("evidence_spans", []))
        scores["invoice_final_record"] = 1.0 if all([
            close(invoice.get("subtotal"), 34293.98),
            close(invoice.get("tax_amount"), 2829.25),
            close(invoice.get("grand_total"), 37123.23),
            str(invoice.get("revision", "")).upper() == "R1",
            "load testing" not in items,
            "111000038" in bank,
            "revision note" in evidence,
        ]) else 0.0
    else:
        scores["invoice_final_record"] = 0.0

    resume = load_json(workspace / "outputs" / "resume_001.json")
    if isinstance(resume, dict):
        certs = text_of(resume.get("certifications", []))
        notes = text_of(resume.get("non_certification_notes", []))
        evidence = text_of(resume.get("evidence_spans", []))
        scores["resume_superseded_certifications"] = 1.0 if all([
            "aws solutions architect professional" in certs and "2023" in certs,
            "certified kubernetes administrator" in certs and "2022" in certs,
            "google cloud professional cloud architect" in certs and "2021" in certs,
            "kubecon" not in certs and "pydata" not in certs,
            "kubecon" in notes and "pydata" in notes,
            "hr correction" in evidence,
        ]) else 0.0
    else:
        scores["resume_superseded_certifications"] = 0.0

    contract = load_json(workspace / "outputs" / "contract_001.json")
    if isinstance(contract, dict):
        scope = text_of(contract.get("scope_of_work", []))
        excluded = text_of(contract.get("excluded_scope", []))
        amendments = text_of(contract.get("amendments", []))
        schedule = text_of(contract.get("payment_schedule", []))
        scores["contract_amended_terms"] = 1.0 if all([
            close(contract.get("total_value"), 421000.00),
            "mobile" not in scope,
            "mobile" in excluded,
            "amendment a" in amendments,
            "33000" in schedule or "33,000" in schedule,
            "12 months" in text_of(contract.get("duration", {})),
        ]) else 0.0
    else:
        scores["contract_amended_terms"] = 0.0

    meeting = load_json(workspace / "outputs" / "meeting_notes_001.json")
    if isinstance(meeting, dict):
        action_items = meeting.get("action_items", [])
        action_text = text_of(action_items)
        scores["meeting_final_action_registry"] = 1.0 if all([
            isinstance(action_items, list) and len(action_items) == 6,
            "2025-02-21" in action_text,
            "2025-02-19" in action_text,
            "marcus johnson" in action_text,
            "marcus johnston" in text_of(meeting.get("name_disambiguation_notes", [])),
            "draft" in text_of(meeting.get("evidence_spans", [])) or "cleanup" in text_of(meeting.get("evidence_spans", [])),
        ]) else 0.0
    else:
        scores["meeting_final_action_registry"] = 0.0

    expense = load_json(workspace / "outputs" / "expense_report_001.json")
    if isinstance(expense, dict):
        totals = text_of(expense.get("category_totals", {}))
        scores["expense_policy_normalization"] = 1.0 if all([
            close(expense.get("total"), 2930.23),
            "transportation" in totals and "743.25" in totals,
            "supplies" in totals and "255.97" in totals,
            "team activity" in totals and "85" in totals,
            "r-2025-0214" in text_of(expense.get("receipt_exceptions", [])),
            "bowling" in text_of(expense.get("approved_exceptions", [])),
            int(expense.get("receipts_count", -1)) == 17,
        ]) else 0.0
    else:
        scores["expense_policy_normalization"] = 0.0

    audit = load_json(workspace / "outputs" / "extraction_audit.json")
    if isinstance(audit, dict):
        audit_text = text_of(audit)
        scores["cross_document_audit"] = 1.0 if all(token in audit_text for token in [
            "r1", "111000038", "hr correction", "amendment a",
            "draft", "17", "r-2025-0214",
        ]) else 0.0
    else:
        scores["cross_document_audit"] = 0.0

    return scores
```
