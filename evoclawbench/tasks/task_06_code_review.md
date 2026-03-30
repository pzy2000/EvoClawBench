---
id: task_06_code_review
name: Security Code Review
category: code_analysis
grading_type: hybrid
grading_weights:
  automated: 0.6
  llm_judge: 0.4
timeout_seconds: 600
sub_problems: 5
skill_category: security_review
workspace_files:
  - assets/code_review/login_handler.py
  - assets/code_review/user_profile.js
  - assets/code_review/file_manager.py
  - assets/code_review/api_handler.go
  - assets/code_review/admin_panel.py
---

# Security Code Review

Perform security-focused code reviews on application source files and produce structured vulnerability reports.

---

## Prompt

You have 5 source code files in `assets/code_review/` that contain intentional security vulnerabilities. Review each file, identify ALL security issues, and produce a structured JSON report for each in `outputs/`.

**Files to review:**
1. `assets/code_review/login_handler.py` → `outputs/login_handler_review.json`
2. `assets/code_review/user_profile.js` → `outputs/user_profile_review.json`
3. `assets/code_review/file_manager.py` → `outputs/file_manager_review.json`
4. `assets/code_review/api_handler.go` → `outputs/api_handler_review.json`
5. `assets/code_review/admin_panel.py` → `outputs/admin_panel_review.json`

**Required output format for each report:**
```json
{
  "file": "login_handler.py",
  "language": "python",
  "vulnerabilities": [
    {
      "line": 18,
      "type": "SQL Injection",
      "severity": "critical",
      "description": "User input directly concatenated into SQL query string.",
      "fix_suggestion": "Use parameterized queries with cursor.execute('SELECT ... WHERE username = ?', (username,))."
    }
  ],
  "risk_score": 9.5,
  "summary": "Critical security issues including SQL injection and plaintext password storage."
}
```

**Severity levels:** critical, high, medium, low

**Common vulnerability types to look for:**
- SQL Injection
- Cross-Site Scripting (XSS)
- Command Injection
- Path Traversal
- Insecure Direct Object Reference (IDOR)
- Hardcoded Secrets
- Mass Assignment
- Server-Side Request Forgery (SSRF)
- Broken Access Control
- Information Disclosure
- Missing Input Validation
- Insecure Deserialization
- Missing CSRF Protection
- Unrestricted File Upload
- Session Fixation

---

## Expected Behavior

1. Agent reviews the first code file and manually identifies vulnerabilities
2. Agent recognizes the repeating review pattern across files
3. Agent creates a reusable skill for structured security review
4. Agent applies the skill to all remaining code files
5. All outputs follow consistent JSON format with complete vulnerability details

---

## Sub-Problems

### Sub-Problem 1: Login Handler (Python Flask)
- Input: `assets/code_review/login_handler.py` (~50 lines)
- Key vulnerabilities: SQL injection in login/register/reset queries, plaintext password storage, no rate limiting, hardcoded secret key, predictable reset password
- Expected output: `outputs/login_handler_review.json`

### Sub-Problem 2: User Profile (Node.js Express)
- Input: `assets/code_review/user_profile.js` (~55 lines)
- Key vulnerabilities: XSS in rendered HTML output, SQL injection, path traversal in avatar file serving, IDOR in profile access/update/delete, missing CSRF protection, no file type validation
- Expected output: `outputs/user_profile_review.json`

### Sub-Problem 3: File Manager (Python Flask)
- Input: `assets/code_review/file_manager.py` (~50 lines)
- Key vulnerabilities: Path traversal in download/list/delete, command injection in preview (shell=True) and convert (os.system), unrestricted file upload, directory listing exposure
- Expected output: `outputs/file_manager_review.json`

### Sub-Problem 4: API Handler (Go)
- Input: `assets/code_review/api_handler.go` (~80 lines)
- Key vulnerabilities: SQL injection in search/update/webhook handlers, hardcoded API key and DB password, information disclosure in error messages, mass assignment in update handler, no input validation
- Expected output: `outputs/api_handler_review.json`

### Sub-Problem 5: Admin Panel (Python Django)
- Input: `assets/code_review/admin_panel.py` (~55 lines)
- Key vulnerabilities: Mass assignment via setattr, broken access control (no permission checks), SSRF in URL preview, information disclosure (password hash in response, traceback in error), no CSRF verification
- Expected output: `outputs/admin_panel_review.json`

---

## Grading Criteria

- [ ] All 5 output files exist in outputs/
- [ ] All output files are valid JSON
- [ ] Each report has a "vulnerabilities" array with at least 3 entries
- [ ] Each vulnerability has required fields: line, type, severity, description, fix_suggestion
- [ ] Severity values are valid (critical, high, medium, low)
- [ ] Each report has risk_score (numeric) and summary (string)
- [ ] Key vulnerability types identified per file

---

## LLM Judge Rubric

You are evaluating a security code review task. The agent reviewed 5 source files and produced JSON reports in `outputs/`. The output files and source code are provided above.

Score the following criteria from 0.0 to 1.0. Use 0.6–0.7 for an acceptable review with minor gaps. Reserve 1.0 for comprehensive, accurate coverage.

- **recall**: Were the key vulnerabilities actually present in the source code identified? Compare against the known vulnerability types listed in the Sub-Problems section (SQL injection, XSS, path traversal, command injection, IDOR, hardcoded secrets, mass assignment, SSRF, broken access control, etc.). A score of 0.0 means major vulnerabilities were completely missed; 1.0 means all critical/high vulns were found.
- **accuracy**: Are the identified vulnerabilities real issues in the code? Do the line numbers and vulnerability types make sense given the source code? A score of 0.0 means the report mostly contains hallucinated issues; 1.0 means all identified vulnerabilities are genuine and well-located.
- **fix_quality**: Are the fix suggestions technically correct, specific, and actionable for the identified issues? Generic advice like "use input validation" scores lower than concrete fixes with code examples.
- **overall_quality**: Holistic quality of the security review across all 5 files — consistency, thoroughness, and professionalism.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    REQUIRED_FIELDS = {"line", "type", "severity", "description", "fix_suggestion"}
    VALID_SEVERITIES = {"critical", "high", "medium", "low"}
    MIN_VULNS = 3

    files = [
        ("login_handler", "login_handler_review.json"),
        ("user_profile", "user_profile_review.json"),
        ("file_manager", "file_manager_review.json"),
        ("api_handler", "api_handler_review.json"),
        ("admin_panel", "admin_panel_review.json"),
    ]

    for idx, (label, out_name) in enumerate(files, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / out_name

        # Check file exists
        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_has_vulns"] = 0.0
            scores[f"{prefix}_vuln_fields"] = 0.0
            scores[f"{prefix}_severities"] = 0.0
            scores[f"{prefix}_meta_fields"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        # Check valid JSON
        try:
            with open(out_path) as f:
                report = json.load(f)
        except (json.JSONDecodeError, Exception):
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_has_vulns"] = 0.0
            scores[f"{prefix}_vuln_fields"] = 0.0
            scores[f"{prefix}_severities"] = 0.0
            scores[f"{prefix}_meta_fields"] = 0.0
            continue

        scores[f"{prefix}_valid_json"] = 1.0

        # Check vulnerabilities array exists and has minimum count
        vulns = report.get("vulnerabilities", [])
        if not isinstance(vulns, list) or len(vulns) < MIN_VULNS:
            scores[f"{prefix}_has_vulns"] = 0.0
        else:
            scores[f"{prefix}_has_vulns"] = 1.0

        # Check each vulnerability has required fields
        if len(vulns) == 0:
            scores[f"{prefix}_vuln_fields"] = 0.0
            scores[f"{prefix}_severities"] = 0.0
        else:
            fields_ok = 0
            severity_ok = 0
            for vuln in vulns:
                if isinstance(vuln, dict):
                    if REQUIRED_FIELDS.issubset(vuln.keys()):
                        fields_ok += 1
                    sev = vuln.get("severity", "").lower()
                    if sev in VALID_SEVERITIES:
                        severity_ok += 1

            scores[f"{prefix}_vuln_fields"] = round(fields_ok / len(vulns), 2)
            scores[f"{prefix}_severities"] = round(severity_ok / len(vulns), 2)

        # Check meta fields (risk_score and summary)
        has_risk = isinstance(report.get("risk_score"), (int, float))
        has_summary = isinstance(report.get("summary"), str) and len(report.get("summary", "")) > 0
        scores[f"{prefix}_meta_fields"] = 1.0 if (has_risk and has_summary) else 0.0

    return scores
```
