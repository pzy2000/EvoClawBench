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
      "id": "stable finding id",
      "line": 18,
      "type": "SQL Injection",
      "severity": "critical",
      "cwe": "CWE-89",
      "owasp": "A03:2021-Injection",
      "confidence": "high|medium|low",
      "description": "User input directly concatenated into SQL query string.",
      "evidence": "short exact code snippet",
      "fix_suggestion": "Use parameterized queries with cursor.execute('SELECT ... WHERE username = ?', (username,)).",
      "exploit_chain": "how this issue could be abused with adjacent code, or null"
    }
  ],
  "false_positive_notes": ["safe helper or decoy patterns that were intentionally not reported"],
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
- Chained authorization bypasses
- Debug or audit exports that leak secrets

Some files include safe helper functions or escaped/parameterized decoys. Do not report those safe helpers as vulnerabilities; list them in `false_positive_notes` when relevant.

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
- **false_positive_discipline**: Does the report avoid flagging safe decoy helpers such as parameterized lookups, escaped preview rendering, secure filename helpers, aggregate-only audit summaries, or typed integer lookups?
- **overall_quality**: Holistic quality of the security review across all 5 files — consistency, thoroughness, CWE/OWASP labeling, exploit-chain reasoning, and professionalism.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    expected = {
        "login_handler_review.json": {
            "types": ["sql injection", "plaintext password", "hardcoded secret", "predictable password", "broken access control", "no rate limiting"],
            "cwes": ["cwe-89", "cwe-798", "cwe-521", "cwe-862"],
            "decoys": ["lookup_user_safe", "constant_time_compare"],
            "anchors": ["find_by_sql", "hardcoded-secret-key-12345", "temp123", "is_admin", "impersonate_user", "password"],
            "chain_terms": ["session", "impersonate", "reset"],
        },
        "user_profile_review.json": {
            "types": ["xss", "sql injection", "path traversal", "idor", "csrf", "unrestricted file upload", "audit log disclosure"],
            "cwes": ["cwe-79", "cwe-89", "cwe-22", "cwe-639", "cwe-352", "cwe-434"],
            "decoys": ["rendersafepreview", "escapehtml"],
            "anchors": ["innerHTML", "SELECT * FROM users WHERE id =", "readFileSync", "req.params.userId", "avatar.mv", "exportAuditLogs"],
            "chain_terms": ["profile", "avatar", "audit"],
        },
        "file_manager_review.json": {
            "types": ["path traversal", "command injection", "unrestricted file upload", "directory listing", "broken access control", "public share bypass"],
            "cwes": ["cwe-22", "cwe-78", "cwe-434", "cwe-548", "cwe-862"],
            "decoys": ["safe_join_preview", "secure_filename"],
            "anchors": ["send_file", "shell=True", "os.system", "uploaded_file.save", "os.listdir", "share_token"],
            "chain_terms": ["upload", "preview", "delete"],
        },
        "api_handler_review.json": {
            "types": ["sql injection", "hardcoded secret", "information disclosure", "mass assignment", "debug endpoint", "webhook trust bypass"],
            "cwes": ["cwe-89", "cwe-798", "cwe-209", "cwe-915", "cwe-489"],
            "decoys": ["safelookuphandler", "strconv.Atoi"],
            "anchors": ["fmt.Sprintf", "HARDCODED_API_KEY", "DB_PASSWORD", "json.NewEncoder", "DebugHandler", "WebhookHandler"],
            "chain_terms": ["debug", "token", "webhook"],
        },
        "admin_panel_review.json": {
            "types": ["mass assignment", "broken access control", "ssrf", "information disclosure", "csrf", "audit export", "session token leak"],
            "cwes": ["cwe-915", "cwe-862", "cwe-918", "cwe-200", "cwe-352"],
            "decoys": ["safe_audit_summary"],
            "anchors": ["setattr", "user_detail", "requests.get", "traceback.format_exc", "csrf_exempt", "session_key"],
            "chain_terms": ["admin", "ssrf", "audit"],
        },
    }

    def text_of(value):
        return json.dumps(value, sort_keys=True).lower()

    def normalize(value):
        return re.sub(r"[^a-z0-9_./:-]+", " ", str(value).lower())

    def gated_fraction(found, total):
        if total == 0:
            return 0.0
        return 1.0 if found == total else round(0.3 * found / total, 2)

    for idx, (out_name, exp) in enumerate(expected.items(), start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / out_name

        if not out_path.exists():
            for key in ["complete_recall", "evidence_anchors", "taxonomy_exact", "false_positive_control", "chain_reasoning"]:
                scores[f"{prefix}_{key}"] = 0.0
            continue

        try:
            with open(out_path) as f:
                report = json.load(f)
        except (json.JSONDecodeError, Exception):
            for key in ["complete_recall", "evidence_anchors", "taxonomy_exact", "false_positive_control", "chain_reasoning"]:
                scores[f"{prefix}_{key}"] = 0.0
            continue

        vulns = report.get("vulnerabilities", [])
        if not isinstance(vulns, list) or not vulns:
            scores[f"{prefix}_complete_recall"] = 0.0
            scores[f"{prefix}_evidence_anchors"] = 0.0
            scores[f"{prefix}_taxonomy_exact"] = 0.0
            scores[f"{prefix}_chain_reasoning"] = 0.0
        else:
            combined = normalize(vulns)
            found = sum(1 for item in exp["types"] if item in combined)
            scores[f"{prefix}_complete_recall"] = gated_fraction(found, len(exp["types"]))

            evidence_text = normalize([v.get("evidence", "") for v in vulns if isinstance(v, dict)])
            anchor_found = sum(1 for anchor in exp["anchors"] if anchor.lower() in evidence_text)
            scores[f"{prefix}_evidence_anchors"] = gated_fraction(anchor_found, len(exp["anchors"]))

            cwe_text = text_of(vulns)
            cwe_found = sum(1 for cwe in exp["cwes"] if cwe in cwe_text)
            has_owasp = all(
                isinstance(v, dict)
                and str(v.get("owasp", "")).lower().startswith("a0")
                and str(v.get("confidence", "")).lower() == "high"
                for v in vulns
            )
            scores[f"{prefix}_taxonomy_exact"] = 1.0 if cwe_found == len(exp["cwes"]) and has_owasp else 0.0

            chain_text = normalize([v.get("exploit_chain", "") for v in vulns if isinstance(v, dict)])
            chain_found = sum(1 for term in exp["chain_terms"] if term in chain_text)
            enough_chains = sum(
                1 for vuln in vulns
                if isinstance(vuln, dict) and len(str(vuln.get("exploit_chain", ""))) >= 40
            )
            scores[f"{prefix}_chain_reasoning"] = (
                1.0 if chain_found == len(exp["chain_terms"]) and enough_chains >= len(exp["types"]) else 0.0
            )

        vuln_text = text_of(report.get("vulnerabilities", []))
        decoy_hits = sum(1 for decoy in exp["decoys"] if decoy.lower() in vuln_text)
        notes_text = text_of(report.get("false_positive_notes", []))
        decoys_ack = all(decoy.lower() in notes_text for decoy in exp["decoys"])
        scores[f"{prefix}_false_positive_control"] = 1.0 if decoy_hits == 0 and decoys_ack else 0.0

    return scores
```
