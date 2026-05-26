---
id: task_11_web_extraction
name: Web Page Structured Data Extraction
category: data_extraction
grading_type: hybrid
grading_weights:
  automated: 0.6
  llm_judge: 0.4
timeout_seconds: 600
sub_problems: 5
skill_category: html_parsing
workspace_files:
  - assets/web_extraction/product_catalog.html
  - assets/web_extraction/job_listings.html
  - assets/web_extraction/news_articles.html
  - assets/web_extraction/event_schedule.html
  - assets/web_extraction/company_directory.html
---

# Web Page Structured Data Extraction

## Prompt

You are given 5 HTML files in `assets/web_extraction/` that simulate web pages. Parse each HTML file and extract structured data into a JSON file in `outputs/`.

### Sub-Problem 1: Product Catalog (`product_catalog.html`)
Extract to `outputs/product_catalog.json` — an array of product objects:
```json
[
  {
    "product_id": "NT-PRX1",
    "name": "NovaTech Pro X1",
    "sku": "NT-PRX1",
    "price": 299.99,
    "category": "Laptop",
    "in_stock": true,
    "rating": 4.5,
    "review_count": 328
  },
  ...
]
```

### Sub-Problem 2: Job Listings (`job_listings.html`)
Extract to `outputs/job_listings.json` — an array of job objects:
```json
[
  {
    "job_id": "JOB-2024-0451",
    "title": "Senior Python Engineer",
    "company": "TechCorp Solutions",
    "location": "San Francisco, CA",
    "salary_min": 150000,
    "salary_max": 180000,
    "job_type": "Full-time",
    "posted_date": "2024-03-01"
  },
  ...
]
```

### Sub-Problem 3: News Articles (`news_articles.html`)
Extract to `outputs/news_articles.json` — an array of article objects:
```json
[
  {
    "article_id": "ART-20240310-001",
    "title": "Breakthrough in Quantum Computing Achieves 1000-Qubit Milestone",
    "author": "Sarah Mitchell",
    "published_date": "2024-03-10",
    "category": "Quantum Computing",
    "read_time_minutes": 5
  },
  ...
]
```

### Sub-Problem 4: Event Schedule (`event_schedule.html`)
Extract to `outputs/event_schedule.json` — an array of event objects:
```json
[
  {
    "event_id": "EVT-001",
    "name": "Keynote: The Future of AI in Enterprise",
    "speaker": "Dr. Amanda Foster",
    "date": "2024-04-15",
    "venue": "Main Auditorium, Hall A",
    "capacity": 2000,
    "registration_fee": 0.0,
    "event_type": "Keynote"
  },
  ...
]
```

### Sub-Problem 5: Company Directory (`company_directory.html`)
Extract to `outputs/company_directory.json` — an array of employee objects:
```json
[
  {
    "employee_id": "EMP-1001",
    "name": "Jennifer Walsh",
    "title": "Chief Technology Officer",
    "department": "Engineering",
    "email": "j.walsh@acmecorp.com",
    "location": "San Francisco, CA"
  },
  ...
]
```

## Expected Behavior

The agent should:
1. Parse each HTML file using Python's `html.parser`, `beautifulsoup4`, or similar tools
2. Extract the structured data accurately from the HTML attributes and text content
3. Write valid JSON to the output files
4. Ideally create a reusable HTML extraction skill to handle all 5 files efficiently

## Sub-Problems

### Sub-Problem 1: Product Catalog
- Input: `assets/web_extraction/product_catalog.html` (5 products)
- Output: `outputs/product_catalog.json`

### Sub-Problem 2: Job Listings
- Input: `assets/web_extraction/job_listings.html` (5 jobs)
- Output: `outputs/job_listings.json`

### Sub-Problem 3: News Articles
- Input: `assets/web_extraction/news_articles.html` (5 articles)
- Output: `outputs/news_articles.json`

### Sub-Problem 4: Event Schedule
- Input: `assets/web_extraction/event_schedule.html` (5 events)
- Output: `outputs/event_schedule.json`

### Sub-Problem 5: Company Directory
- Input: `assets/web_extraction/company_directory.html` (5 employees)
- Output: `outputs/company_directory.json`

## Grading Criteria

- [ ] All 5 output JSON files exist
- [ ] Each file contains a list with at least 5 items
- [ ] Product catalog: prices are numeric, product IDs match source
- [ ] Job listings: salary values are numeric, job IDs match source
- [ ] News articles: dates are in YYYY-MM-DD format
- [ ] Event schedule: capacity values are numeric integers
- [ ] Company directory: emails and employee IDs present

## LLM Judge Rubric

You are evaluating a web data extraction task. The agent was asked to parse 5 HTML files and produce structured JSON outputs.

For each output file, evaluate:
- **accuracy** (0-10): How accurately are the values extracted vs. the source HTML? Check specific values like prices, IDs, names, dates.
- **completeness** (0-10): Are all 5 items extracted from each file? Are all required fields present?
- **format_quality** (0-10): Are values in the correct types (numbers vs strings, date formats)?

Provide a JSON response: `{"scores": {"accuracy": N, "completeness": N, "format_quality": N}, "notes": "..."}`

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    # Sub-1: Product catalog
    prefix = "sub_1"
    out_path = workspace / "outputs" / "product_catalog.json"
    if not out_path.exists():
        scores[f"{prefix}_exists"] = 0.0
        scores[f"{prefix}_count"] = 0.0
        scores[f"{prefix}_ids"] = 0.0
        scores[f"{prefix}_prices"] = 0.0
    else:
        scores[f"{prefix}_exists"] = 1.0
        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_count"] = 1.0 if isinstance(data, list) and len(data) >= 5 else 0.0
            expected_ids = {"NT-PRX1", "AB-3000", "QL-Z7", "SB-MINI", "CV-HD"}
            found_ids = set()
            prices_numeric = True
            for item in (data if isinstance(data, list) else []):
                pid = item.get("product_id") or item.get("sku") or item.get("id", "")
                if str(pid) in expected_ids:
                    found_ids.add(str(pid))
                price = item.get("price") or item.get("price_usd")
                if price is not None and not isinstance(price, (int, float)):
                    prices_numeric = False
            scores[f"{prefix}_ids"] = round(len(found_ids) / len(expected_ids), 2)
            scores[f"{prefix}_prices"] = 1.0 if prices_numeric else 0.0
        except Exception:
            scores[f"{prefix}_count"] = 0.0
            scores[f"{prefix}_ids"] = 0.0
            scores[f"{prefix}_prices"] = 0.0

    # Sub-2: Job listings
    prefix = "sub_2"
    out_path = workspace / "outputs" / "job_listings.json"
    if not out_path.exists():
        scores[f"{prefix}_exists"] = 0.0
        scores[f"{prefix}_count"] = 0.0
        scores[f"{prefix}_ids"] = 0.0
        scores[f"{prefix}_salary_numeric"] = 0.0
    else:
        scores[f"{prefix}_exists"] = 1.0
        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_count"] = 1.0 if isinstance(data, list) and len(data) >= 5 else 0.0
            expected_ids = {"JOB-2024-0451", "JOB-2024-0452", "JOB-2024-0453", "JOB-2024-0454", "JOB-2024-0455"}
            found_ids = set()
            salary_ok = True
            for item in (data if isinstance(data, list) else []):
                jid = item.get("job_id") or item.get("id", "")
                if str(jid) in expected_ids:
                    found_ids.add(str(jid))
                sal_min = item.get("salary_min")
                sal_max = item.get("salary_max")
                if sal_min is not None and not isinstance(sal_min, (int, float)):
                    salary_ok = False
                if sal_max is not None and not isinstance(sal_max, (int, float)):
                    salary_ok = False
            scores[f"{prefix}_ids"] = round(len(found_ids) / len(expected_ids), 2)
            scores[f"{prefix}_salary_numeric"] = 1.0 if salary_ok else 0.0
        except Exception:
            scores[f"{prefix}_count"] = 0.0
            scores[f"{prefix}_ids"] = 0.0
            scores[f"{prefix}_salary_numeric"] = 0.0

    # Sub-3: News articles
    import re
    prefix = "sub_3"
    out_path = workspace / "outputs" / "news_articles.json"
    if not out_path.exists():
        scores[f"{prefix}_exists"] = 0.0
        scores[f"{prefix}_count"] = 0.0
        scores[f"{prefix}_dates"] = 0.0
    else:
        scores[f"{prefix}_exists"] = 1.0
        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_count"] = 1.0 if isinstance(data, list) and len(data) >= 5 else 0.0
            iso_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            dates_ok = True
            for item in (data if isinstance(data, list) else []):
                d = item.get("published_date") or item.get("date") or item.get("pub_date", "")
                if d and not iso_re.match(str(d)):
                    dates_ok = False
            scores[f"{prefix}_dates"] = 1.0 if dates_ok else 0.5
        except Exception:
            scores[f"{prefix}_count"] = 0.0
            scores[f"{prefix}_dates"] = 0.0

    # Sub-4: Event schedule
    prefix = "sub_4"
    out_path = workspace / "outputs" / "event_schedule.json"
    if not out_path.exists():
        scores[f"{prefix}_exists"] = 0.0
        scores[f"{prefix}_count"] = 0.0
        scores[f"{prefix}_capacity_numeric"] = 0.0
    else:
        scores[f"{prefix}_exists"] = 1.0
        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_count"] = 1.0 if isinstance(data, list) and len(data) >= 5 else 0.0
            cap_ok = True
            for item in (data if isinstance(data, list) else []):
                cap = item.get("capacity")
                if cap is not None and not isinstance(cap, (int, float)):
                    cap_ok = False
            scores[f"{prefix}_capacity_numeric"] = 1.0 if cap_ok else 0.0
        except Exception:
            scores[f"{prefix}_count"] = 0.0
            scores[f"{prefix}_capacity_numeric"] = 0.0

    # Sub-5: Company directory
    prefix = "sub_5"
    out_path = workspace / "outputs" / "company_directory.json"
    if not out_path.exists():
        scores[f"{prefix}_exists"] = 0.0
        scores[f"{prefix}_count"] = 0.0
        scores[f"{prefix}_emails"] = 0.0
    else:
        scores[f"{prefix}_exists"] = 1.0
        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_count"] = 1.0 if isinstance(data, list) and len(data) >= 5 else 0.0
            email_re = re.compile(r"[^@]+@[^@]+\.[^@]+")
            emails_ok = True
            email_found = False
            for item in (data if isinstance(data, list) else []):
                email = item.get("email", "")
                if email:
                    email_found = True
                    if not email_re.match(str(email)):
                        emails_ok = False
            scores[f"{prefix}_emails"] = 1.0 if (email_found and emails_ok) else 0.0
        except Exception:
            scores[f"{prefix}_count"] = 0.0
            scores[f"{prefix}_emails"] = 0.0

    return scores
```
