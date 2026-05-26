---
id: task_05_config_migration
name: Config Migration v1 to v2
category: data_transformation
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: config_migration
workspace_files:
  - assets/config_migration/webapp_v1.json
  - assets/config_migration/worker_v1.json
  - assets/config_migration/gateway_v1.json
  - assets/config_migration/scheduler_v1.json
  - assets/config_migration/mailer_v1.json
---

# Config Migration v1 to v2

Migrate application configuration files from a flat dot-notation format (v1) to a nested, typed format (v2).

---

## Prompt

You have 5 application configuration files in `assets/config_migration/` that use a legacy flat key format (v1). Migrate each one to the new nested v2 format and save the results in `outputs/`.

**v1 format** (flat dot-notation keys):
```json
{
  "app.name": "MyApp",
  "app.port": 8080,
  "db.host": "localhost",
  "db.port": 5432,
  "cache.enabled": true,
  "cache.ttl": 300
}
```

**v2 format** (nested structure with type annotations):
```json
{
  "app": {
    "name": {"value": "MyApp", "type": "string"},
    "port": {"value": 8080, "type": "integer"}
  },
  "database": {
    "host": {"value": "localhost", "type": "string"},
    "port": {"value": 5432, "type": "integer"}
  },
  "cache": {
    "enabled": {"value": true, "type": "boolean"},
    "ttl": {"value": 300, "type": "integer"}
  }
}
```

**Key renaming rules for v2:**
- `db` becomes `database`
- `rate_limit` becomes `rate_limiting`
- `notification` becomes `notifications`
- All other top-level keys remain the same

**Type detection rules:**
- Strings → `"type": "string"`
- Integers → `"type": "integer"`
- Floats → `"type": "float"`
- Booleans → `"type": "boolean"`
- Arrays/Lists → `"type": "list"`

**Files to migrate:**
1. `assets/config_migration/webapp_v1.json` → `outputs/webapp_v2.json`
2. `assets/config_migration/worker_v1.json` → `outputs/worker_v2.json`
3. `assets/config_migration/gateway_v1.json` → `outputs/gateway_v2.json`
4. `assets/config_migration/scheduler_v1.json` → `outputs/scheduler_v2.json`
5. `assets/config_migration/mailer_v1.json` → `outputs/mailer_v2.json`

---

## Expected Behavior

1. Agent reads the first config file and manually converts it to v2 format
2. Agent recognizes the repeating pattern across config files
3. Agent creates a reusable skill or script for config migration
4. Agent applies the skill to all remaining config files
5. All outputs use consistent nested structure with correct type annotations

---

## Sub-Problems

### Sub-Problem 1: Web App Config
- Input: `assets/config_migration/webapp_v1.json` (20 keys: app.*, server.*, db.*, session.*, logging.*)
- Special handling: `db` → `database` renaming; mixed types including float (max_size_mb, timeout)
- Expected output: `outputs/webapp_v2.json`

### Sub-Problem 2: Worker Config
- Input: `assets/config_migration/worker_v1.json` (19 keys: worker.*, queue.*, db.*, retry.*, monitoring.*)
- Special handling: `db` → `database` renaming; float values in retry backoff
- Expected output: `outputs/worker_v2.json`

### Sub-Problem 3: API Gateway Config
- Input: `assets/config_migration/gateway_v1.json` (18 keys: gateway.*, upstream.*, auth.*, rate_limit.*, cors.*)
- Special handling: `rate_limit` → `rate_limiting` renaming; list values (upstream.services, cors.allowed_origins)
- Expected output: `outputs/gateway_v2.json`

### Sub-Problem 4: Task Scheduler Config
- Input: `assets/config_migration/scheduler_v1.json` (19 keys: scheduler.*, jobs.*, db.*, notification.*, timezone.*)
- Special handling: `db` → `database` and `notification` → `notifications` renaming; list values (notification.channels, notification.email_recipients)
- Expected output: `outputs/scheduler_v2.json`

### Sub-Problem 5: Email Service Config
- Input: `assets/config_migration/mailer_v1.json` (19 keys: mailer.*, smtp.*, templates.*, queue.*, tracking.*)
- Special handling: No key renaming needed; float value (smtp.timeout)
- Expected output: `outputs/mailer_v2.json`

---

## Grading Criteria

- [ ] All 5 output files exist in outputs/
- [ ] All output files are valid JSON
- [ ] All output files use nested structure (no flat dot-notation keys)
- [ ] All values are wrapped in `{"value": ..., "type": ...}` objects
- [ ] Type annotations are correct (string, integer, float, boolean, list)
- [ ] Key renaming applied correctly (db→database, rate_limit→rate_limiting, notification→notifications)
- [ ] All original values are preserved accurately

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    KEY_RENAMES = {
        "db": "database",
        "rate_limit": "rate_limiting",
        "notification": "notifications",
    }

    TYPE_MAP = {
        str: "string",
        int: "integer",
        float: "float",
        bool: "boolean",
        list: "list",
    }

    files = [
        ("webapp", "webapp_v1.json", "webapp_v2.json"),
        ("worker", "worker_v1.json", "worker_v2.json"),
        ("gateway", "gateway_v1.json", "gateway_v2.json"),
        ("scheduler", "scheduler_v1.json", "scheduler_v2.json"),
        ("mailer", "mailer_v1.json", "mailer_v2.json"),
    ]

    for idx, (label, v1_name, v2_name) in enumerate(files, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / v2_name
        v1_path = workspace / "assets" / "config_migration" / v1_name

        # Check file exists
        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_nested"] = 0.0
            scores[f"{prefix}_typed"] = 0.0
            scores[f"{prefix}_renamed"] = 0.0
            scores[f"{prefix}_values"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        # Check valid JSON
        try:
            with open(out_path) as f:
                v2 = json.load(f)
        except (json.JSONDecodeError, Exception):
            scores[f"{prefix}_valid_json"] = 0.0
            scores[f"{prefix}_nested"] = 0.0
            scores[f"{prefix}_typed"] = 0.0
            scores[f"{prefix}_renamed"] = 0.0
            scores[f"{prefix}_values"] = 0.0
            continue

        scores[f"{prefix}_valid_json"] = 1.0

        # Check nested structure (no flat dot-notation keys at top level)
        flat_keys = [k for k in v2.keys() if "." in k]
        scores[f"{prefix}_nested"] = 1.0 if len(flat_keys) == 0 else 0.0

        # Load v1 for comparison
        try:
            with open(v1_path) as f:
                v1 = json.load(f)
        except Exception:
            v1 = {}

        # Check that values are wrapped in {value, type}
        typed_count = 0
        total_leaves = 0
        for section_key, section_val in v2.items():
            if isinstance(section_val, dict):
                for field_key, field_val in section_val.items():
                    total_leaves += 1
                    if (isinstance(field_val, dict)
                            and "value" in field_val
                            and "type" in field_val):
                        typed_count += 1

        if total_leaves > 0:
            scores[f"{prefix}_typed"] = round(typed_count / total_leaves, 2)
        else:
            scores[f"{prefix}_typed"] = 0.0

        # Check key renaming
        rename_correct = True
        for old_key, new_key in KEY_RENAMES.items():
            # Check if any v1 key starts with old_key.
            has_old_prefix = any(k.startswith(old_key + ".") for k in v1.keys())
            if has_old_prefix:
                # old_key should NOT be in v2, new_key SHOULD be
                if old_key in v2:
                    rename_correct = False
                if new_key not in v2 and has_old_prefix:
                    rename_correct = False

        scores[f"{prefix}_renamed"] = 1.0 if rename_correct else 0.0

        # Check values preserved
        values_correct = 0
        values_total = 0
        for flat_key, orig_value in v1.items():
            parts = flat_key.split(".", 1)
            if len(parts) != 2:
                continue
            section, field = parts
            # Apply renaming
            renamed_section = KEY_RENAMES.get(section, section)
            values_total += 1
            if renamed_section in v2 and isinstance(v2[renamed_section], dict):
                if field in v2[renamed_section]:
                    entry = v2[renamed_section][field]
                    if isinstance(entry, dict) and "value" in entry:
                        if entry["value"] == orig_value:
                            values_correct += 1

        if values_total > 0:
            scores[f"{prefix}_values"] = round(values_correct / values_total, 2)
        else:
            scores[f"{prefix}_values"] = 0.0

    return scores
```
