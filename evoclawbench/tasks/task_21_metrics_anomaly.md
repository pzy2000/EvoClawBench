---
id: task_21_metrics_anomaly
name: System Metrics Anomaly Detection
category: data_analysis
grading_type: hybrid
grading_weights:
  automated: 0.85
  llm_judge: 0.15
timeout_seconds: 600
sub_problems: 5
skill_category: metrics_analysis
workspace_files:
  - assets/system_metrics/server_cpu.csv
  - assets/system_metrics/server_mem.csv
  - assets/system_metrics/db_query_perf.csv
  - assets/system_metrics/network_traffic.csv
  - assets/system_metrics/disk_io.csv
---

# System Metrics Anomaly Detection

Analyze 5 system metrics CSV files collected over a 24-hour window (5-minute intervals), compute statistical summaries, detect anomalies, and produce structured health reports.

---

## Prompt

You have 5 system metrics CSV files in `assets/system_metrics/`. Each file contains 24 hours of data at 5-minute intervals for different infrastructure components. Analyze each file, compute statistics, detect anomalies (values significantly above normal baseline), and produce a JSON health report.

**Input files:**

1. `server_cpu.csv` — CPU usage per host (3 hosts × 288 intervals)
2. `server_mem.csv` — Memory usage per host (3 hosts × 288 intervals)
3. `db_query_perf.csv` — Database query latency and QPS per query type
4. `network_traffic.csv` — Network bandwidth per interface
5. `disk_io.csv` — Disk I/O utilization and throughput per device

**Output for each metric:** `outputs/<metric_name>_report.json`

```json
{
  "metric_name": "server_cpu",
  "period": {
    "start": "2024-03-20T00:00:00",
    "end": "2024-03-20T23:55:00"
  },
  "total_data_points": 288,
  "dimensions": ["web-01", "web-02", "web-03"],
  "statistics": {
    "web-01": {
      "mean": 32.5,
      "p50": 30.1,
      "p95": 65.2,
      "p99": 88.4,
      "max": 97.3,
      "min": 5.1
    }
  },
  "anomalies": [
    {
      "dimension": "web-01",
      "timestamp": "2024-03-20T14:00:00",
      "metric_value": 95.4,
      "anomaly_type": "spike",
      "description": "CPU usage spiked to 95.4% at 14:00, well above the 24-hour mean of 32.5%"
    }
  ],
  "health_score": 7.5,
  "health_status": "warning",
  "summary": "2 anomalies detected across 3 hosts. web-01 experienced a CPU spike at 14:00 (95.4%), web-02 showed sustained high usage at 02:00-02:20."
}
```

**Anomaly detection method:**
- Define a baseline as the mean and standard deviation of the metric for each dimension
- Flag data points where `value > mean + 3 * std` (3-sigma rule)
- For metrics with sustained anomalies, group consecutive anomalous points into a single anomaly event
- Report the peak value and time window for each anomaly event

**Health score (0-10):**
- Start at 10
- Deduct 2 points per critical anomaly (value > mean + 4σ)
- Deduct 1 point per warning anomaly (mean + 3σ < value ≤ mean + 4σ)
- Minimum score is 0

**Health status:** `healthy` (≥8), `warning` (5–7.9), `critical` (<5)

**Dimension key:**
- `server_cpu.csv`: dimension = `host` column
- `server_mem.csv`: dimension = `host` column, primary metric = `mem_usage_pct`
- `db_query_perf.csv`: dimension = `db_host + "_" + query_type`, primary metric = `avg_latency_ms`
- `network_traffic.csv`: dimension = `interface` column, primary metric = `rx_mbps`
- `disk_io.csv`: dimension = `device` column, primary metric = `util_pct`

---

## Expected Behavior

1. Agent reads `server_cpu.csv`, computes per-host statistics, applies 3-sigma anomaly detection, and generates the report.
2. After 2 files, agent recognizes the pattern: load CSV → group by dimension → compute stats → detect outliers → score → report.
3. Agent builds a reusable metrics analysis skill that handles different CSV schemas via a configurable `dimension_col` and `metric_col`.
4. Remaining files are processed using the skill with schema-specific configuration.
5. All 5 reports accurately reflect the planted anomalies in the data.

---

## Sub-Problems

### Sub-Problem 1: CPU Usage (server_cpu.csv)
- Primary metric: `cpu_usage_pct`; dimensions: 3 hosts (web-01, web-02, web-03)
- Planted anomalies: web-01 spike at ~14:00 (92-99%), web-02 high at ~02:00 (88-95%)
- Expected output: `outputs/server_cpu_report.json`

### Sub-Problem 2: Memory Usage (server_mem.csv)
- Primary metric: `mem_usage_pct`; dimensions: 3 hosts
- Planted anomalies: web-03 memory spike at ~18:00 (~87.5%), web-01 gradual growth trend
- Expected output: `outputs/server_mem_report.json`

### Sub-Problem 3: Database Query Performance (db_query_perf.csv)
- Primary metric: `avg_latency_ms`; dimensions: db_host × query_type combinations
- Planted anomaly: pg-primary SELECT latency spike at ~10:30 (450-550ms vs normal ~5ms)
- Expected output: `outputs/db_query_perf_report.json`

### Sub-Problem 4: Network Traffic (network_traffic.csv)
- Primary metric: `rx_mbps`; dimensions: 2 interfaces (eth0, eth1)
- Planted anomaly: eth0 traffic surge at ~20:00 (850-980 Mbps vs normal ~150 Mbps)
- Expected output: `outputs/network_traffic_report.json`

### Sub-Problem 5: Disk I/O (disk_io.csv)
- Primary metric: `util_pct`; dimensions: 2 devices (/dev/sda, /dev/sdb)
- Planted anomaly: /dev/sda util spike at ~03:00 (85-98% vs normal ~15%)
- Expected output: `outputs/disk_io_report.json`

---

## Grading Criteria

- [ ] All 5 output report files exist
- [ ] Each report contains valid JSON
- [ ] Each report has all required top-level fields
- [ ] Each report's `statistics` contains at least one dimension with mean, p95, p99, max
- [ ] `anomalies` array is non-empty for all 5 reports (planted anomalies are detectable)
- [ ] `health_score` is a number between 0 and 10
- [ ] `server_cpu_report.json` anomalies mention web-01 or web-02
- [ ] `db_query_perf_report.json` anomalies mention pg-primary

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    metrics = [
        ("server_cpu",       "web-01|web-02"),
        ("server_mem",       "web-03|web-01"),
        ("db_query_perf",    "pg-primary"),
        ("network_traffic",  "eth0"),
        ("disk_io",          "sda"),
    ]

    required_fields = {"metric_name", "period", "total_data_points", "statistics",
                       "anomalies", "health_score", "health_status", "summary"}
    stat_required = {"mean", "p95", "p99", "max"}

    for i, (metric, must_mention) in enumerate(metrics, start=1):
        prefix = f"sub_{i}"
        filepath = workspace / "outputs" / f"{metric}_report.json"

        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for k in ["valid_json", "fields", "statistics", "anomalies", "health_score", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for k in ["valid_json", "fields", "statistics", "anomalies", "health_score", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        if not isinstance(data, dict):
            for k in ["fields", "statistics", "anomalies", "health_score", "special"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        scores[f"{prefix}_fields"] = 1.0 if required_fields.issubset(data.keys()) else 0.0

        # Statistics structure
        stats = data.get("statistics", {})
        has_stats = (
            isinstance(stats, dict)
            and len(stats) > 0
            and any(
                isinstance(v, dict) and stat_required.issubset(v.keys())
                for v in stats.values()
            )
        )
        scores[f"{prefix}_statistics"] = 1.0 if has_stats else 0.0

        # Anomalies non-empty
        anomalies = data.get("anomalies", [])
        scores[f"{prefix}_anomalies"] = 1.0 if (isinstance(anomalies, list) and len(anomalies) > 0) else 0.0

        # Health score valid
        hs = data.get("health_score")
        scores[f"{prefix}_health_score"] = 1.0 if (
            isinstance(hs, (int, float)) and 0 <= hs <= 10
        ) else 0.0

        # Special mention check
        report_str = json.dumps(data).lower()
        scores[f"{prefix}_special"] = 1.0 if re.search(must_mention, report_str) else 0.0

    return scores
```

---

## LLM Judge Rubric

You are evaluating system metrics anomaly detection reports. The agent analyzed 5 CSV files containing 24-hour infrastructure metrics with planted anomalies and generated JSON reports in `outputs/`.

Score the following criterion from 0.0 to 1.0:

**anomaly_accuracy**: For each of the 5 reports, does the `anomalies` list correctly identify the planted anomaly events? The planted anomalies are: (1) server_cpu: web-01 CPU spike ~14:00 and web-02 spike ~02:00; (2) server_mem: web-03 memory spike ~18:00; (3) db_query_perf: pg-primary SELECT latency spike ~10:30; (4) network_traffic: eth0 surge ~20:00; (5) disk_io: /dev/sda util spike ~03:00. A score of 1.0 means all planted anomalies are detected with correct dimension name and approximate timestamp. A score of 0.0 means no planted anomalies are detected. Average across all 5 reports.
