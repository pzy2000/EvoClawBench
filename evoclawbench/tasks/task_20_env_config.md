---
id: task_20_env_config
name: Multi-Environment Config Generation
category: devops_automation
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: config_generation
workspace_files:
  - assets/env_config/app_01_web_service.json
  - assets/env_config/app_02_worker_service.json
  - assets/env_config/app_03_ml_inference.json
  - assets/env_config/app_04_notification_service.json
  - assets/env_config/app_05_data_exporter.json
---

# Multi-Environment Config Generation

Read 5 application base configuration JSON files with environment override rules, and generate three environment-specific YAML config files (`dev`, `staging`, `prod`) for each application.

---

## Prompt

You have 5 application specification files in `assets/env_config/`. Each JSON file describes an application's base configuration and per-environment overrides using dot-notation keys (e.g., `"database.host"` overrides the `host` key inside the `database` section).

For each application, generate three YAML config files in `outputs/<app_name>/`:
- `config.dev.yml`
- `config.staging.yml`
- `config.prod.yml`

**Input files:**

1. `app_01_web_service.json` — REST API service with database, cache, rate limiting
2. `app_02_worker_service.json` — Async task worker with Celery/Redis
3. `app_03_ml_inference.json` — ML model serving with GPU/CPU switching in prod
4. `app_04_notification_service.json` — Multi-channel notification service with mocked providers in dev
5. `app_05_data_exporter.json` — Scheduled data export pipeline

**How to apply overrides:**
- Start from `base_config` (a nested dict)
- For each environment, apply its overrides from `environment_overrides.<env>`
- Dot-notation keys like `"database.host": "localhost"` mean: set `config["database"]["host"] = "localhost"`
- The final YAML is the merged result

**Output format:** Valid YAML, preserving the nested structure of `base_config`

**Example** (for a fictitious app):
If base has `server.port: 8080` and dev overrides `server.port: 3000`, then `config.dev.yml` should have:
```yaml
server:
  port: 3000
```

---

## Expected Behavior

1. Agent reads the first spec and implements dot-notation override merging to produce 3 YAML files.
2. After the second spec, agent recognizes the pattern: load JSON → deep-merge overrides → dump YAML.
3. Agent builds a reusable config generation skill (a Python script or function) that handles dot-notation key expansion.
4. Remaining apps are processed using the skill.
5. All 15 YAML files are valid and correctly reflect their respective environment settings.

---

## Sub-Problems

### Sub-Problem 1: Web Service (app_01_web_service.json)
- Dev: workers=1, localhost DB, DEBUG logging, rate limiting disabled, CORS allows localhost
- Staging: workers=2, staging DB name, increased rate limit
- Prod: workers=8, pool_size=20, WARN logging
- Expected output: `outputs/web-service/config.dev.yml`, `config.staging.yml`, `config.prod.yml`

### Sub-Problem 2: Worker Service (app_02_worker_service.json)
- Dev: concurrency=1, local Redis, DEBUG logging, max_retries=1
- Staging: concurrency=2, staging DB name
- Prod: concurrency=8, increased pool and retry settings
- Expected output: `outputs/worker-service/config.dev.yml`, `config.staging.yml`, `config.prod.yml`

### Sub-Problem 3: ML Inference (app_03_ml_inference.json)
- Dev: no warmup, local model path, monitoring disabled, DEBUG
- Staging: staging model name, higher trace sample rate
- Prod: cuda device, float16 precision, batch_size=64
- Expected output: `outputs/ml-inference/config.dev.yml`, `config.staging.yml`, `config.prod.yml`

### Sub-Problem 4: Notification Service (app_04_notification_service.json)
- Dev: local mock SMTP (port 1025, no TLS), mock Twilio/FCM endpoints
- Staging: staging email address, reduced rate limits
- Prod: increased rate limits and batch size
- Expected output: `outputs/notification-service/config.dev.yml`, `config.staging.yml`, `config.prod.yml`

### Sub-Problem 5: Data Exporter (app_05_data_exporter.json)
- Dev: schedule disabled, csv/no-compression, local DB, no alerting
- Staging: different cron, staging DB and bucket
- Prod: gzip compression, WARN logging, longer query timeout
- Expected output: `outputs/data-exporter/config.dev.yml`, `config.staging.yml`, `config.prod.yml`

---

## Grading Criteria

- [ ] All 15 output YAML files exist
- [ ] Each YAML file is parseable (valid YAML)
- [ ] `web-service/config.dev.yml` has `workers: 1`
- [ ] `web-service/config.prod.yml` has `workers: 8`
- [ ] `ml-inference/config.prod.yml` has `device: cuda`
- [ ] `ml-inference/config.dev.yml` has `warmup_on_start: false`
- [ ] `notification-service/config.dev.yml` has SMTP port 1025
- [ ] `data-exporter/config.dev.yml` has `enabled: false` (schedule disabled)

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import yaml
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    apps = [
        "web-service",
        "worker-service",
        "ml-inference",
        "notification-service",
        "data-exporter",
    ]
    envs = ["dev", "staging", "prod"]

    for i, app in enumerate(apps, start=1):
        prefix = f"sub_{i}"
        app_dir = workspace / "outputs" / app

        # Check all 3 env files exist
        all_exist = all((app_dir / f"config.{env}.yml").is_file() for env in envs)
        scores[f"{prefix}_all_exist"] = 1.0 if all_exist else (
            sum(1 for env in envs if (app_dir / f"config.{env}.yml").is_file()) / 3.0
        )

        # Check each file is valid YAML
        valid_count = 0
        configs = {}
        for env in envs:
            path = app_dir / f"config.{env}.yml"
            if path.is_file():
                try:
                    with open(path) as f:
                        configs[env] = yaml.safe_load(f)
                    valid_count += 1
                except Exception:
                    configs[env] = None
        scores[f"{prefix}_valid_yaml"] = valid_count / 3.0

        def get_nested(d, *keys):
            for k in keys:
                if not isinstance(d, dict):
                    return None
                d = d.get(k)
            return d

        # App-specific correctness checks
        if i == 1:  # web-service
            dev = configs.get("dev") or {}
            prod = configs.get("prod") or {}
            scores[f"{prefix}_dev_workers"] = 1.0 if get_nested(dev, "server", "workers") == 1 else 0.0
            scores[f"{prefix}_prod_workers"] = 1.0 if get_nested(prod, "server", "workers") == 8 else 0.0
            scores[f"{prefix}_dev_debug"] = 1.0 if str(get_nested(dev, "logging", "level") or "").upper() == "DEBUG" else 0.0

        elif i == 2:  # worker-service
            dev = configs.get("dev") or {}
            prod = configs.get("prod") or {}
            scores[f"{prefix}_dev_concurrency"] = 1.0 if get_nested(dev, "worker", "concurrency") == 1 else 0.0
            scores[f"{prefix}_prod_concurrency"] = 1.0 if get_nested(prod, "worker", "concurrency") == 8 else 0.0

        elif i == 3:  # ml-inference
            dev = configs.get("dev") or {}
            prod = configs.get("prod") or {}
            scores[f"{prefix}_prod_device"] = 1.0 if str(get_nested(prod, "model", "device") or "").lower() == "cuda" else 0.0
            dev_warmup = get_nested(dev, "model", "warmup_on_start")
            scores[f"{prefix}_dev_no_warmup"] = 1.0 if dev_warmup is False else 0.0

        elif i == 4:  # notification-service
            dev = configs.get("dev") or {}
            scores[f"{prefix}_dev_smtp_port"] = 1.0 if get_nested(dev, "email", "port") == 1025 else 0.0
            dev_tls = get_nested(dev, "email", "use_tls")
            scores[f"{prefix}_dev_no_tls"] = 1.0 if dev_tls is False else 0.0

        elif i == 5:  # data-exporter
            dev = configs.get("dev") or {}
            prod = configs.get("prod") or {}
            dev_enabled = get_nested(dev, "schedule", "enabled")
            scores[f"{prefix}_dev_schedule_disabled"] = 1.0 if dev_enabled is False else 0.0
            scores[f"{prefix}_prod_compression"] = 1.0 if str(get_nested(prod, "destination", "compression") or "").lower() == "gzip" else 0.0

    return scores
```
