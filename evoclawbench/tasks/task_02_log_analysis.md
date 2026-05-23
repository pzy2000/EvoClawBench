---
id: task_02_log_analysis
name: Log Analysis
category: data_analysis
grading_type: hybrid
grading_weights:
  automated: 0.85
  llm_judge: 0.15
timeout_seconds: 600
sub_problems: 5
skill_category: log_parsing
workspace_files:
  - assets/log_analysis/auth_service.log
  - assets/log_analysis/payment_service.log
  - assets/log_analysis/api_gateway.log
  - assets/log_analysis/notification_service.log
  - assets/log_analysis/scheduler_service.log
---

# Log Analysis

Parse and analyze log files from 5 different microservices, each using a different log format, and produce structured JSON reports.

---

## Prompt

You have 5 log files in `assets/log_analysis/` from different microservices. Each service uses a different log format. Analyze each log file and produce a structured JSON report per file in the `outputs/` directory.

**Input files:**

1. `auth_service.log` — Syslog format: `Mar 15 10:23:45 auth-srv auth[1234]: LEVEL: message`
2. `payment_service.log` — JSON lines (one JSON object per line with timestamp, level, service, message, request_id)
3. `api_gateway.log` — Apache/CLF format: `IP - user [date] "METHOD /path HTTP/1.1" status_code bytes`
4. `notification_service.log` — Custom bracket format: `[timestamp] [LEVEL] [service] [request_id] message`
5. `scheduler_service.log` — Structured key=value format: `level=error ts=... caller=... msg="..." key=value`

**Output:** For each input file `<service>.log`, produce `outputs/<service>_report.json` with this structure:

```json
{
  "service_name": "string",
  "total_entries": integer,
  "error_count": integer,
  "warn_count": integer,
  "info_count": integer,
  "errors": [
    {
      "timestamp": "string",
      "message": "string",
      "context": "string (any extra info like request_id, IP, etc.)"
    }
  ],
  "time_range": {
    "start": "string (first log entry timestamp)",
    "end": "string (last log entry timestamp)"
  },
  "summary": "string (one-line description of service health)",
  "confidence": "high|medium|low",
  "evidence": ["short exact log snippets supporting the summary"]
}
```

Also produce `outputs/incident_correlation.json` with this structure:

```json
{
  "incidents": [
    {
      "incident_id": "stable snake_case id",
      "request_ids": ["req-..."],
      "affected_services": ["service names"],
      "severity": "critical|high|medium|low",
      "root_cause": "concise explanation",
      "first_seen": "normalized timestamp",
      "last_seen": "normalized timestamp",
      "retry_count": 0,
      "evidence": ["short exact snippets from multiple files"],
      "recommended_action": "specific operator action"
    }
  ],
  "benign_noise_filtered": ["synthetic/canary events that should not be treated as incidents"]
}
```

**Notes:**
- For `api_gateway.log`, treat HTTP status codes 5xx as ERROR, 4xx as WARN, and 2xx as INFO.
- Stack trace continuation lines belong to the preceding ERROR event and should be preserved as evidence, not counted as independent log entries.
- Canary/synthetic expected failures still count in per-service WARN totals, but they must not become incidents.
- The `errors` list should only include ERROR-level entries.
- Cross-service incidents must correlate repeated request IDs across services and retries.
- The `summary` should mention key findings (e.g., "5 errors detected, mostly authentication failures").

---

## Expected Behavior

1. The agent parses the first log file (syslog format) and produces a structured report.
2. It moves to the second file (JSON lines) and writes a different parser.
3. After 2-3 files, the agent recognizes the common pattern: parse log -> classify levels -> extract errors -> compute stats -> build report.
4. The agent creates a reusable skill or framework that handles generic log analysis with pluggable format parsers.
5. Remaining files are processed using the skill, with only the parser changing per format.

---

## Sub-Problems

### Sub-Problem 1: Syslog format (auth_service.log)
- Input: Syslog-style log with `LEVEL:` markers
- Special handling: Date lacks year (assume 2024); level is embedded after the PID bracket
- Expected output: `outputs/auth_service_report.json`

### Sub-Problem 2: JSON lines (payment_service.log)
- Input: One JSON object per line with structured fields
- Special handling: Level and timestamp are explicit fields; easiest to parse
- Expected output: `outputs/payment_service_report.json`

### Sub-Problem 3: Apache/CLF format (api_gateway.log)
- Input: Apache Combined Log Format
- Special handling: No explicit level field; must infer from HTTP status codes (5xx=ERROR, 4xx=WARN, 2xx=INFO)
- Expected output: `outputs/api_gateway_report.json`

### Sub-Problem 4: Custom bracket format (notification_service.log)
- Input: Bracket-delimited fields
- Special handling: Request ID is in brackets; level is second bracket group
- Expected output: `outputs/notification_service_report.json`

### Sub-Problem 5: Key=value structured format (scheduler_service.log)
- Input: Logfmt-style key=value pairs
- Special handling: Values may be quoted; msg field contains the main message
- Expected output: `outputs/scheduler_service_report.json`

---

## Grading Criteria

- [ ] Each of the 5 output report files exists
- [ ] Each report contains valid JSON
- [ ] Each report has all required top-level fields
- [ ] Error counts are reasonable (non-zero where errors exist)
- [ ] The `errors` list contains only ERROR-level entries
- [ ] `time_range` has both start and end fields

---

## LLM Judge Rubric

You are evaluating a log analysis task. The agent parsed 5 log files and produced JSON reports in `outputs/`. The output files are provided above.

This rubric focuses **only** on the `summary` field in each report — all other fields (counts, errors list, time_range) are checked by automated scoring.
It also considers the incident narrative in `incident_correlation.json` when it explains cross-service causality.

Score the following criterion from 0.0 to 1.0:

- **summary_quality**: For each of the 5 service reports, does the `summary` field accurately and meaningfully describe service health from the actual log evidence? A high score requires naming the service, exact error count, dominant failure mode, and whether canary/synthetic noise was filtered. Generic summaries, unsupported claims, or summaries that miss the `req-901` cross-service failure should score low.
- **incident_reasoning**: Does `incident_correlation.json` explain the correlated `req-901` refund/nonce failure across services with concise evidence and a plausible operator action? Penalize treating canary expected failures as production incidents.

Return a single score for `summary_quality` averaged across all 5 reports.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    expected = {
        "auth_service": {"total": 23, "error": 7, "warn": 5, "info": 11, "must": ["req-901", "NonceMismatchException"]},
        "payment_service": {"total": 23, "error": 7, "warn": 5, "info": 11, "must": ["req-901", "ord-901"]},
        "api_gateway": {"total": 23, "error": 6, "warn": 4, "info": 13, "must": ["req-901", "502"]},
        "notification_service": {"total": 23, "error": 7, "warn": 5, "info": 11, "must": ["req-901", "ord-901"]},
        "scheduler_service": {"total": 23, "error": 6, "warn": 5, "info": 12, "must": ["req-901", "cron-901"]},
    }

    def norm_text(value):
        return json.dumps(value, sort_keys=True).lower()

    for i, (service, exp) in enumerate(expected.items(), start=1):
        prefix = f"sub_{i}"
        filename = f"{service}_report.json"
        filepath = workspace / "outputs" / filename

        if not filepath.is_file():
            for key in ["exact_counts", "error_inventory", "evidence_trace", "diagnostic_summary"]:
                scores[f"{prefix}_{key}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception):
            for key in ["exact_counts", "error_inventory", "evidence_trace", "diagnostic_summary"]:
                scores[f"{prefix}_{key}"] = 0.0
            continue

        if not isinstance(data, dict):
            for key in ["exact_counts", "error_inventory", "evidence_trace", "diagnostic_summary"]:
                scores[f"{prefix}_{key}"] = 0.0
            continue

        exact_counts = (
            data.get("total_entries") == exp["total"]
            and data.get("error_count") == exp["error"]
            and data.get("warn_count") == exp["warn"]
            and data.get("info_count") == exp["info"]
        )
        scores[f"{prefix}_exact_counts"] = 1.0 if exact_counts else 0.0

        errors = data.get("errors", None)
        text = norm_text(data)
        errors_ok = (
            isinstance(errors, list)
            and len(errors) == exp["error"]
            and all(
                isinstance(e, dict)
                and "timestamp" in e
                and "message" in e
                and "context" in e
                and "severity" in e
                and "request_id" in e
                for e in errors
            )
            and all(token.lower() in text for token in exp["must"])
        )
        scores[f"{prefix}_error_inventory"] = 1.0 if errors_ok else 0.0

        evidence = data.get("evidence")
        evidence_ok = (
            isinstance(evidence, list)
            and len(evidence) >= 3
            and any("req-901" in str(item).lower() for item in evidence)
            and all(token.lower() in norm_text(evidence) for token in exp["must"])
        )
        scores[f"{prefix}_evidence_trace"] = 1.0 if evidence_ok else 0.0

        summary = str(data.get("summary", "")).lower()
        summary_ok = (
            service.replace("_", " ") in summary
            and str(exp["error"]) in summary
            and "req-901" in summary
            and ("canary" in text or "synthetic" in text)
        )
        scores[f"{prefix}_diagnostic_summary"] = 1.0 if summary_ok else 0.0

    corr_path = workspace / "outputs" / "incident_correlation.json"
    if not corr_path.exists():
        scores["incident_req901"] = 0.0
        scores["incident_services"] = 0.0
        scores["incident_root_cause"] = 0.0
        scores["incident_timeline"] = 0.0
        scores["incident_noise_filter"] = 0.0
    else:
        try:
            corr = json.loads(corr_path.read_text())
        except Exception:
            corr = {}
        corr_text = norm_text(corr)
        incidents = corr.get("incidents", []) if isinstance(corr, dict) else []
        req901 = [item for item in incidents if "req-901" in norm_text(item)]
        scores["incident_req901"] = 1.0 if req901 else 0.0
        required_services = {"auth", "payment", "api", "notification", "scheduler"}
        scores["incident_services"] = 1.0 if all(s in corr_text for s in required_services) else 0.0
        has_root = "nonce" in corr_text and "ord-901" in corr_text and "retry" in corr_text
        scores["incident_root_cause"] = 1.0 if has_root else 0.0
        timeline_ok = (
            "2024-03-15t10:43:08z" in corr_text
            and "2024-03-15t10:43:28z" in corr_text
            and '"retry_count": 1' in corr_text
        )
        scores["incident_timeline"] = 1.0 if timeline_ok else 0.0
        noise = corr.get("benign_noise_filtered", []) if isinstance(corr, dict) else []
        noise_text = norm_text(noise)
        noise_ok = "canary" in noise_text and "synthetic" in noise_text and "negative-test" in noise_text
        scores["incident_noise_filter"] = 1.0 if noise_ok else 0.0

    return scores
```
