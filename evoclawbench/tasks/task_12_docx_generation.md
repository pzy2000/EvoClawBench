---
id: task_12_docx_generation
name: Word Document Generation
category: code_generation
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: document_generation
workspace_files:
  - assets/docx_generation/tech_spec.json
  - assets/docx_generation/project_report.json
  - assets/docx_generation/contract_summary.json
  - assets/docx_generation/meeting_agenda.json
  - assets/docx_generation/product_brief.json
---

# Word Document Generation

## Prompt

You are given 5 JSON data files in `assets/docx_generation/`. Each JSON file describes a structured document with sections, tables, and metadata. Your task is to generate a properly formatted Microsoft Word (.docx) file for each.

For each JSON file, generate a Word document at `outputs/<name>.docx` where `<name>` matches the input filename without extension (e.g., `outputs/tech_spec.docx`).

### Document Requirements

Each generated `.docx` must include:
1. **Title** — A large Heading 1 with the document's `title` field
2. **Metadata block** — Document type, date, and author as a paragraph or table
3. **Sections** — Each section in the `sections` array must be rendered:
   - Use `level` field to determine heading style (1→Heading 1, 2→Heading 2, 3→Heading 3)
   - `content` field becomes paragraph text under that heading
4. **Tables** — Each table in the `tables` array must be rendered as an actual Word table:
   - First row uses the `headers` array as column headers
   - Subsequent rows come from the `rows` array
5. **Lists** — If the JSON has a `requirements`, `key_terms`, `attendees`, or `milestones` field that is an array of strings, render it as a bulleted or numbered list

### JSON Structure Reference

```json
{
  "title": "Document Title",
  "document_type": "Type",
  "date": "2024-03-15",
  "author": "Author Name",
  "sections": [
    {"heading": "Section Name", "level": 1, "content": "Section text..."},
    {"heading": "Sub Section", "level": 2, "content": "Sub-section text..."}
  ],
  "tables": [
    {
      "title": "Table Title",
      "headers": ["Col1", "Col2"],
      "rows": [["val1", "val2"]]
    }
  ]
}
```

## Expected Behavior

The agent should:
1. Install and use `python-docx` to generate Word documents
2. Map JSON structure to proper Word document elements (headings, paragraphs, tables)
3. Handle all 5 document types with their varying structures
4. Ideally create a reusable JSON-to-DOCX conversion skill

## Sub-Problems

### Sub-Problem 1: Technical Specification
- Input: `assets/docx_generation/tech_spec.json`
- Output: `outputs/tech_spec.docx`
- Expected: 6 sections, 2 tables, 1 requirements list

### Sub-Problem 2: Project Status Report
- Input: `assets/docx_generation/project_report.json`
- Output: `outputs/project_report.docx`
- Expected: 5 sections, 2 tables, 1 milestones list

### Sub-Problem 3: Contract Summary
- Input: `assets/docx_generation/contract_summary.json`
- Output: `outputs/contract_summary.docx`
- Expected: 6 sections, 2 tables, 1 key_terms list

### Sub-Problem 4: Meeting Agenda
- Input: `assets/docx_generation/meeting_agenda.json`
- Output: `outputs/meeting_agenda.docx`
- Expected: 6 sections, 2 tables, attendees list

### Sub-Problem 5: Product Brief
- Input: `assets/docx_generation/product_brief.json`
- Output: `outputs/product_brief.docx`
- Expected: 7 sections, 2 tables

## Grading Criteria

- [ ] All 5 .docx files exist in outputs/
- [ ] Files are valid Word documents (openable by python-docx)
- [ ] Each document contains the correct title as a Heading 1
- [ ] Each document has at least the expected number of paragraphs
- [ ] At least one table exists in each document
- [ ] Heading hierarchy is present (H1 and H2 at minimum)

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import docx as python_docx

    scores = {}
    workspace = Path(workspace_path)

    FILES = [
        ("tech_spec", "tech_spec.docx", "CloudSync API v3.0", 6, 2),
        ("project_report", "project_report.docx", "Aurora Platform Redesign", 5, 2),
        ("contract_summary", "contract_summary.docx", "Software Development Services", 6, 2),
        ("meeting_agenda", "meeting_agenda.docx", "Q2 2024 Engineering", 6, 2),
        ("product_brief", "product_brief.docx", "NovaPay", 7, 2),
    ]

    for idx, (name, filename, title_keyword, min_sections, min_tables) in enumerate(FILES, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / filename

        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_valid_docx"] = 0.0
            scores[f"{prefix}_has_title"] = 0.0
            scores[f"{prefix}_paragraphs"] = 0.0
            scores[f"{prefix}_tables"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        try:
            doc = python_docx.Document(str(out_path))
            scores[f"{prefix}_valid_docx"] = 1.0
        except Exception as e:
            try:
                Path("/tmp/grade_task12_error.txt").write_text(
                    f"{prefix}: {type(e).__name__}: {e}\npath={out_path}\n"
                )
            except Exception:
                pass
            scores[f"{prefix}_valid_docx"] = 0.0
            scores[f"{prefix}_has_title"] = 0.0
            scores[f"{prefix}_paragraphs"] = 0.0
            scores[f"{prefix}_tables"] = 0.0
            continue

        full_text = " ".join(p.text for p in doc.paragraphs)
        headings = [p for p in doc.paragraphs if p.style.name.startswith("Heading")]
        heading_text = " ".join(h.text for h in headings)
        has_title = title_keyword.lower() in (full_text + heading_text).lower()
        scores[f"{prefix}_has_title"] = 1.0 if has_title else 0.0

        total_paragraphs = len([p for p in doc.paragraphs if p.text.strip()])
        scores[f"{prefix}_paragraphs"] = 1.0 if total_paragraphs >= min_sections * 2 else round(
            total_paragraphs / (min_sections * 2), 2
        )

        table_count = len(doc.tables)
        scores[f"{prefix}_tables"] = 1.0 if table_count >= min_tables else (
            0.5 if table_count >= 1 else 0.0
        )

    return scores
```
