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
  "summary": "string (one-line description of service health)"
}
```

**Notes:**
- For `api_gateway.log`, treat HTTP status codes 5xx as ERROR, 4xx as WARN, and 2xx as INFO.
- Each log file has approximately 20 entries.
- The `errors` list should only include ERROR-level entries.
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

Score the following criterion from 0.0 to 1.0:

- **summary_quality**: For each of the 5 service reports, does the `summary` field accurately and meaningfully describe the service's health status based on the log data? A good summary names the service, mentions the error count or key error types, and gives a concise health assessment (e.g. "5 authentication failures detected, service degraded"). A score of 0.0 means the summary is missing, generic ("logs analyzed"), or factually incorrect; 1.0 means all 5 summaries are specific, accurate, and informative.

Return a single score for `summary_quality` averaged across all 5 reports.

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    services = [
        "auth_service",
        "payment_service",
        "api_gateway",
        "notification_service",
        "scheduler_service",
    ]

    required_fields = {
        "service_name", "total_entries", "error_count", "warn_count",
        "info_count", "errors", "time_range", "summary"
    }

    for i, service in enumerate(services, start=1):
        prefix = f"sub_{i}"
        filename = f"{service}_report.json"
        filepath = workspace / "outputs" / filename

        # Check existence
        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_fields"] = 0.0
            scores[f"{prefix}_errors_list"] = 0.0
            scores[f"{prefix}_time_range"] = 0.0
            scores[f"{prefix}_counts"] = 0.0
            continue

        # Check valid JSON
        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except (json.JSONDecodeError, Exception):
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_fields"] = 0.0
            scores[f"{prefix}_errors_list"] = 0.0
            scores[f"{prefix}_time_range"] = 0.0
            scores[f"{prefix}_counts"] = 0.0
            continue

        if not isinstance(data, dict):
            scores[f"{prefix}_fields"] = 0.0
            scores[f"{prefix}_errors_list"] = 0.0
            scores[f"{prefix}_time_range"] = 0.0
            scores[f"{prefix}_counts"] = 0.0
            continue

        # Check required fields
        has_fields = required_fields.issubset(data.keys())
        scores[f"{prefix}_fields"] = 1.0 if has_fields else 0.0

        # Check errors is a list
        errors = data.get("errors", None)
        errors_ok = (
            isinstance(errors, list)
            and all(
                isinstance(e, dict) and "timestamp" in e and "message" in e
                for e in errors
            )
        )
        scores[f"{prefix}_errors_list"] = 1.0 if errors_ok else 0.0

        # Check time_range
        tr = data.get("time_range", {})
        tr_ok = isinstance(tr, dict) and "start" in tr and "end" in tr
        scores[f"{prefix}_time_range"] = 1.0 if tr_ok else 0.0

        # Check counts are integers and error_count > 0
        counts_ok = (
            isinstance(data.get("total_entries"), int)
            and isinstance(data.get("error_count"), int)
            and isinstance(data.get("warn_count"), int)
            and isinstance(data.get("info_count"), int)
            and data.get("total_entries", 0) > 0
            and data.get("error_count", 0) > 0
        )
        scores[f"{prefix}_counts"] = 1.0 if counts_ok else 0.0

    return scores
```
