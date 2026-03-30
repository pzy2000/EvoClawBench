---
id: task_18_dep_audit
name: Dependency Security Audit
category: security
grading_type: hybrid
grading_weights:
  automated: 0.60
  llm_judge: 0.40
timeout_seconds: 600
sub_problems: 5
skill_category: security_audit
workspace_files:
  - assets/dep_audit/requirements.txt
  - assets/dep_audit/package.json
  - assets/dep_audit/go.mod
  - assets/dep_audit/Gemfile
  - assets/dep_audit/pom.xml
---

# Dependency Security Audit

Analyze 5 dependency manifest files across different ecosystems, identify packages with known security vulnerabilities, and produce structured audit reports.

---

## Prompt

You have 5 dependency manifest files in `assets/dep_audit/` from different application stacks. Audit each manifest for packages with known security vulnerabilities (CVEs). Produce a structured JSON audit report for each file in `outputs/`.

**Input files:**

1. `requirements.txt` — Python (pip) dependencies
2. `package.json` — Node.js (npm) dependencies
3. `go.mod` — Go module dependencies
4. `Gemfile` — Ruby (Bundler) gems
5. `pom.xml` — Java (Maven) dependencies

**Output for each manifest:** `outputs/<manifest_name>_audit.json`

```json
{
  "manifest_file": "requirements.txt",
  "ecosystem": "python",
  "total_packages": 15,
  "vulnerable_packages": 6,
  "risk_score": 8.5,
  "vulnerabilities": [
    {
      "package": "Flask",
      "installed_version": "2.0.1",
      "cve_ids": ["CVE-2023-30861"],
      "severity": "high",
      "description": "Open redirect vulnerability allowing attackers to redirect users to arbitrary URLs.",
      "fix_version": "2.3.2",
      "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-30861"]
    }
  ],
  "summary": "X critical, Y high, Z medium vulnerabilities found. Immediate action required for: <package list>.",
  "recommendations": [
    "Upgrade Flask from 2.0.1 to >=2.3.2",
    "..."
  ]
}
```

**Severity levels:** critical, high, medium, low

**Notes:**
- Use your knowledge of known CVEs for these specific package versions to identify vulnerabilities. The manifests intentionally contain outdated versions.
- `risk_score` is a 0.0–10.0 overall score reflecting the worst severity and vulnerable package count
- Focus on packages in `dependencies` (not `devDependencies`) for `package.json`
- For `pom.xml`, `log4j 1.2.17` and `struts2-core 2.5.22` are particularly notable
- Include at least 3 vulnerabilities per manifest where they exist

---

## Expected Behavior

1. Agent reads the first manifest (Python requirements.txt), identifies outdated packages, cross-references known CVEs.
2. After processing 2 manifests, agent builds a reusable audit skill: parse manifest → enumerate packages → CVE lookup → severity classification → report generation.
3. Agent applies the skill to remaining manifests with ecosystem-specific parsing (go.mod syntax differs from npm).
4. Each report contains specific CVE IDs, accurate versions, and actionable upgrade recommendations.
5. Reports are consistent in structure across all 5 ecosystems.

---

## Sub-Problems

### Sub-Problem 1: Python (requirements.txt)
- Key vulnerable packages: `requests==2.18.0` (SSRF/redirect), `Pillow==9.0.0` (multiple CVEs), `PyYAML==5.3.1` (arbitrary code exec), `cryptography==3.3.1`, `lxml==4.6.3`
- Expected output: `outputs/requirements_audit.json`

### Sub-Problem 2: Node.js (package.json)
- Key vulnerable packages: `axios==0.21.1` (SSRF), `lodash==4.17.15` (prototype pollution), `node-fetch==2.6.0`, `serialize-javascript==3.1.0`, `tar==6.1.0`, `ws==7.4.2`
- Note: Only scan `dependencies`, not `devDependencies`
- Expected output: `outputs/package_audit.json`

### Sub-Problem 3: Go (go.mod)
- Key vulnerable packages: `dgrijalva/jwt-go v3.2.0` (CVE-2020-26160, discontinued), `golang.org/x/net` (old version), `golang.org/x/crypto` (old version)
- Special handling: parse `require (...)` block, extract module path and version
- Expected output: `outputs/go_audit.json`

### Sub-Problem 4: Ruby (Gemfile)
- Key vulnerable packages: `rails==6.0.3`, `nokogiri==1.10.9` (libxml2 CVEs), `rack==2.1.2`, `omniauth==1.9.1` (auth bypass)
- Expected output: `outputs/gemfile_audit.json`

### Sub-Problem 5: Java (pom.xml)
- Key vulnerable packages: `log4j 1.2.17` (CVE-2019-17571, deserialization), `struts2-core 2.5.22` (RCE), `jackson-databind 2.11.0`, `commons-compress 1.19`
- Special handling: parse Maven XML `<dependency>` nodes, extract groupId/artifactId/version
- Expected output: `outputs/pom_audit.json`

---

## Grading Criteria

- [ ] All 5 output files exist
- [ ] Each report contains valid JSON
- [ ] Each report has all required top-level fields
- [ ] `vulnerable_packages` > 0 for all manifests
- [ ] `vulnerabilities` array is non-empty for all manifests
- [ ] Each vulnerability entry contains `package`, `severity`, and `fix_version`
- [ ] `pom_audit.json` mentions `log4j` or `struts` in vulnerabilities
- [ ] `go_audit.json` mentions `jwt` in vulnerabilities

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    manifests = [
        ("requirements_audit", None, None),
        ("package_audit",      None, None),
        ("go_audit",           "jwt", None),
        ("gemfile_audit",      None, None),
        ("pom_audit",          "log4j|struts", None),
    ]

    required_fields = {"manifest_file", "ecosystem", "total_packages",
                       "vulnerable_packages", "risk_score", "vulnerabilities",
                       "summary", "recommendations"}
    vuln_required = {"package", "severity", "fix_version"}

    for i, (name, must_mention, _) in enumerate(manifests, start=1):
        prefix = f"sub_{i}"
        filepath = workspace / "outputs" / f"{name}.json"

        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for k in ["valid_json", "fields", "has_vulns", "vuln_structure", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for k in ["valid_json", "fields", "has_vulns", "vuln_structure", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        if not isinstance(data, dict):
            for k in ["fields", "has_vulns", "vuln_structure", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        scores[f"{prefix}_fields"] = 1.0 if required_fields.issubset(data.keys()) else 0.0

        vulns = data.get("vulnerabilities", [])
        scores[f"{prefix}_has_vulns"] = 1.0 if (
            isinstance(vulns, list) and len(vulns) > 0
            and data.get("vulnerable_packages", 0) > 0
        ) else 0.0

        vuln_ok = (
            isinstance(vulns, list)
            and all(
                isinstance(v, dict) and vuln_required.issubset(v.keys())
                for v in vulns
            )
        ) if vulns else False
        scores[f"{prefix}_vuln_structure"] = 1.0 if vuln_ok else 0.0

        if must_mention:
            report_text = json.dumps(data).lower()
            scores[f"{prefix}_special"] = 1.0 if re.search(must_mention, report_text) else 0.0
        else:
            scores[f"{prefix}_special"] = 1.0

    return scores
```

---

## LLM Judge Rubric

You are evaluating dependency security audit reports generated from 5 manifest files. The agent used its knowledge of known CVEs to identify vulnerable packages.

Score the following two criteria from 0.0 to 1.0:

**1. cve_accuracy (CVE Knowledge Accuracy, weight 60%)**
For each report, do the identified vulnerabilities reflect real, known CVEs for those specific package versions? Check: (1) Are the CVE IDs plausible/real? (2) Are the severity ratings appropriate? (3) Are the `fix_version` values realistic upgrade targets? A score of 1.0 means all 5 reports contain factually accurate vulnerability data. A score of 0.0 means vulnerabilities are fabricated or grossly incorrect. Average across all 5 reports.

**2. recommendation_quality (Recommendation Quality, weight 40%)**
For each report, are the `recommendations` list items actionable and specific? Good recommendations name the package, current version, and target upgrade version. A score of 1.0 means all reports provide clear, specific upgrade guidance. Return the average across all 5 reports.
