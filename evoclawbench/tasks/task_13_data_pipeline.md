---
id: task_13_data_pipeline
name: Multi-Dataset Statistical Analysis Pipeline
category: data_analysis
grading_type: hybrid
grading_weights:
  automated: 0.65
  llm_judge: 0.35
timeout_seconds: 900
sub_problems: 5
skill_category: data_analysis
workspace_files:
  - assets/data_pipeline/group1_sales.csv
  - assets/data_pipeline/group1_customers.csv
  - assets/data_pipeline/group1_returns.csv
  - assets/data_pipeline/group2_employees.csv
  - assets/data_pipeline/group2_departments.csv
  - assets/data_pipeline/group2_performance.csv
  - assets/data_pipeline/group3_transactions.csv
  - assets/data_pipeline/group3_accounts.csv
  - assets/data_pipeline/group3_fraud_flags.csv
  - assets/data_pipeline/group4_web_traffic.csv
  - assets/data_pipeline/group4_conversions.csv
  - assets/data_pipeline/group4_campaigns.csv
  - assets/data_pipeline/group5_sensors.csv
  - assets/data_pipeline/group5_maintenance_log.csv
  - assets/data_pipeline/group5_alerts.csv
---

# Multi-Dataset Statistical Analysis Pipeline

## Prompt

You are given 5 groups of related CSV files in `assets/data_pipeline/`. Each group contains 3 related datasets that need to be joined, analyzed, and summarized.

For each group, produce a JSON analysis report at `outputs/analysis_group<N>.json`.

### Group 1: E-Commerce Sales Analysis
Files: `group1_sales.csv`, `group1_customers.csv`, `group1_returns.csv`

Analyze and output:
```json
{
  "group": 1,
  "total_orders": 20,
  "total_revenue": <sum of quantity * unit_price for all orders>,
  "return_rate": <returns / total_orders as decimal, e.g. 0.25>,
  "top_product_by_revenue": "<product_id>",
  "revenue_by_region": {"North": <num>, "South": <num>, "East": <num>, "West": <num>},
  "customer_tier_breakdown": {"Gold": <count>, "Silver": <count>, "Bronze": <count>},
  "anomalies": []
}
```

### Group 2: HR Analytics
Files: `group2_employees.csv`, `group2_departments.csv`, `group2_performance.csv`

Analyze and output:
```json
{
  "group": 2,
  "total_employees": <count>,
  "avg_salary": <mean salary across all employees>,
  "salary_std_dev": <standard deviation>,
  "promotion_rate": <recommended_for_promotion / total reviewed>,
  "top_rated_employees": ["<name>", ...],
  "department_avg_salary": {"Engineering": <num>, ...},
  "low_performers": ["<name>", ...]
}
```

### Group 3: Financial Transaction Risk Analysis
Files: `group3_transactions.csv`, `group3_accounts.csv`, `group3_fraud_flags.csv`

Analyze and output:
```json
{
  "group": 3,
  "total_transactions": 20,
  "flagged_transaction_count": <count>,
  "flag_rate": <flagged / total>,
  "confirmed_fraud_count": <count of outcome=confirmed_fraud>,
  "total_debit_amount": <sum of amount for debit transactions>,
  "avg_transaction_amount": <mean>,
  "high_risk_accounts": ["<account_id>", ...]
}
```

### Group 4: Marketing & Web Analytics
Files: `group4_web_traffic.csv`, `group4_conversions.csv`, `group4_campaigns.csv`

Analyze and output:
```json
{
  "group": 4,
  "total_sessions": 20,
  "bounce_rate": <bounced_sessions / total_sessions>,
  "avg_session_duration_sec": <mean>,
  "conversion_count": 5,
  "conversion_rate": <conversions / total_sessions>,
  "top_traffic_source": "<referrer with most sessions>",
  "campaign_total_spend": <sum of spend_usd across all campaigns>
}
```

### Group 5: Infrastructure Monitoring Analysis
Files: `group5_sensors.csv`, `group5_maintenance_log.csv`, `group5_alerts.csv`

Analyze and output:
```json
{
  "group": 5,
  "total_readings": 20,
  "critical_alert_count": <count of severity=critical>,
  "warning_alert_count": <count of severity=warning>,
  "devices_with_incidents": ["<device_id>", ...],
  "avg_temperature": <mean of temperature metric values>,
  "max_cpu_usage": <max of cpu_usage values>,
  "maintenance_events": <count of maintenance log entries>
}
```

## Expected Behavior

The agent should:
1. Load and parse each CSV file using pandas or built-in csv module
2. Perform joins across related files (e.g., sales + customers for tier breakdown)
3. Calculate the required statistics accurately
4. Handle edge cases (missing values, type conversions)
5. Ideally create a reusable data analysis skill

## Sub-Problems

### Sub-Problem 1: E-Commerce Sales Analysis
- Inputs: `group1_sales.csv`, `group1_customers.csv`, `group1_returns.csv`
- Output: `outputs/analysis_group1.json`

### Sub-Problem 2: HR Analytics
- Inputs: `group2_employees.csv`, `group2_departments.csv`, `group2_performance.csv`
- Output: `outputs/analysis_group2.json`

### Sub-Problem 3: Financial Risk Analysis
- Inputs: `group3_transactions.csv`, `group3_accounts.csv`, `group3_fraud_flags.csv`
- Output: `outputs/analysis_group3.json`

### Sub-Problem 4: Marketing Analytics
- Inputs: `group4_web_traffic.csv`, `group4_conversions.csv`, `group4_campaigns.csv`
- Output: `outputs/analysis_group4.json`

### Sub-Problem 5: Infrastructure Monitoring
- Inputs: `group5_sensors.csv`, `group5_maintenance_log.csv`, `group5_alerts.csv`
- Output: `outputs/analysis_group5.json`

## Grading Criteria

- [ ] All 5 analysis JSON files exist
- [ ] `total_orders` / `total_sessions` / `total_transactions` / `total_readings` match expected counts
- [ ] Numeric statistics are present and of correct type
- [ ] `return_rate` / `bounce_rate` / `flag_rate` are decimal values between 0 and 1
- [ ] `revenue_by_region` or equivalent breakdowns contain all expected keys
- [ ] Anomaly/outlier detection fields are present

## LLM Judge Rubric

You are evaluating a multi-dataset statistical analysis task. The agent was given 5 groups of related CSV files to analyze.

For each group's output, evaluate:
- **accuracy** (0-10): Are the computed statistics correct? Check totals, rates, and averages.
- **completeness** (0-10): Are all required fields present? Are join operations performed correctly?
- **insight_quality** (0-10): Does the analysis identify meaningful patterns or anomalies?

Provide a JSON response: `{"scores": {"accuracy": N, "completeness": N, "insight_quality": N}, "notes": "..."}`

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    GROUPS = [
        {
            "name": "group1",
            "file": "analysis_group1.json",
            "checks": {
                "total_orders": (18, 22),   # 20 orders, allow ±2 for flexible counting
                "required_keys": ["total_orders", "total_revenue", "return_rate", "top_product_by_revenue"],
                "rate_keys": ["return_rate"],
                "breakdown_key": "revenue_by_region",
                "breakdown_min_keys": 3,
            }
        },
        {
            "name": "group2",
            "file": "analysis_group2.json",
            "checks": {
                "total_employees": (10, 18),  # 12-16 employees depending on MGR inclusion
                "required_keys": ["total_employees", "avg_salary", "promotion_rate"],
                "rate_keys": ["promotion_rate"],
                "breakdown_key": "department_avg_salary",
                "breakdown_min_keys": 3,
            }
        },
        {
            "name": "group3",
            "file": "analysis_group3.json",
            "checks": {
                "total_transactions": (18, 22),
                "required_keys": ["total_transactions", "flagged_transaction_count", "flag_rate"],
                "rate_keys": ["flag_rate"],
                "breakdown_key": None,
                "breakdown_min_keys": 0,
            }
        },
        {
            "name": "group4",
            "file": "analysis_group4.json",
            "checks": {
                "total_sessions": (18, 22),
                "required_keys": ["total_sessions", "bounce_rate", "conversion_count"],
                "rate_keys": ["bounce_rate"],
                "breakdown_key": None,
                "breakdown_min_keys": 0,
            }
        },
        {
            "name": "group5",
            "file": "analysis_group5.json",
            "checks": {
                "total_readings": (18, 22),
                "required_keys": ["total_readings", "critical_alert_count", "devices_with_incidents"],
                "rate_keys": [],
                "breakdown_key": None,
                "breakdown_min_keys": 0,
            }
        },
    ]

    for idx, group in enumerate(GROUPS, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / group["file"]
        checks = group["checks"]

        if not out_path.exists():
            for key in ("exists", "valid_json", "required_keys", "count_range", "rates_valid"):
                scores[f"{prefix}_{key}"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        try:
            data = json.loads(out_path.read_text())
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for key in ("valid_json", "required_keys", "count_range", "rates_valid"):
                scores[f"{prefix}_{key}"] = 0.0
            continue

        # Check required keys
        required = checks["required_keys"]
        found_keys = sum(1 for k in required if k in data)
        scores[f"{prefix}_required_keys"] = round(found_keys / len(required), 2) if required else 1.0

        # Check count range
        count_key = None
        for k in ("total_orders", "total_employees", "total_transactions", "total_sessions", "total_readings"):
            if k in checks:
                count_key = k
                break
        if count_key and count_key in data:
            lo, hi = checks[count_key]
            val = data[count_key]
            in_range = isinstance(val, (int, float)) and lo <= val <= hi
            scores[f"{prefix}_count_range"] = 1.0 if in_range else 0.0
        else:
            # If the count key doesn't exist, give partial credit
            scores[f"{prefix}_count_range"] = 0.0

        # Check rate keys are valid decimals [0,1]
        rate_keys = checks["rate_keys"]
        if rate_keys:
            rate_ok = 0
            for rk in rate_keys:
                val = data.get(rk)
                if isinstance(val, (int, float)) and 0.0 <= val <= 1.0:
                    rate_ok += 1
            scores[f"{prefix}_rates_valid"] = round(rate_ok / len(rate_keys), 2)
        else:
            scores[f"{prefix}_rates_valid"] = 1.0

    return scores
```
