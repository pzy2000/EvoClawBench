---
id: task_15_shell_automation
name: Shell Automation Script Generation
category: automation
grading_type: hybrid
grading_weights:
  automated: 0.80
  llm_judge: 0.20
timeout_seconds: 600
sub_problems: 5
skill_category: shell_scripting
workspace_files:
  - assets/automation_tasks/task_01_file_backup.yaml
  - assets/automation_tasks/task_02_log_rotation.yaml
  - assets/automation_tasks/task_03_db_dump.yaml
  - assets/automation_tasks/task_04_dir_monitor.yaml
  - assets/automation_tasks/task_05_multi_node_sync.yaml
---

# Shell Automation Script Generation

Read 5 YAML task specification files and generate a production-quality Bash shell script plus a README for each automation task.

---

## Prompt

You have 5 automation task specification files in `assets/automation_tasks/`. Each YAML file describes a different system automation scenario with requirements and constraints. Implement each task as a working Bash shell script.

**Input files:**

1. `task_01_file_backup.yaml` — Scheduled incremental file backup with tar.gz and retention
2. `task_02_log_rotation.yaml` — Log file rotation, compression, and cleanup
3. `task_03_db_dump.yaml` — PostgreSQL dump, compression, and S3 upload
4. `task_04_dir_monitor.yaml` — Directory change monitoring with alerting (no inotify)
5. `task_05_multi_node_sync.yaml` — Multi-server config sync via rsync/SSH with rollback

**For each task, produce two output files:**
- `outputs/<task_id>.sh` — the executable Bash script
- `outputs/<task_id>_readme.md` — brief documentation (purpose, usage, required env vars, example output)

**Script requirements (apply to all tasks):**
- Start with `#!/usr/bin/env bash` and `set -euo pipefail`
- Include meaningful comments for non-obvious logic
- Use functions to organize repeated logic
- Handle errors explicitly; never fail silently
- All configurable values (paths, thresholds, credentials) as variables at the top of the script

---

## Expected Behavior

1. Agent reads the first YAML spec and writes a complete bash script implementing all requirements.
2. After 2 tasks, agent recognizes common patterns: read config → preflight checks → main operation → error handling → logging/reporting.
3. Agent creates a reusable script template or skill with standard boilerplate (error handler, logging function, usage banner).
4. Remaining scripts are generated using the template, adapting only the task-specific logic.
5. All scripts are syntactically valid and follow bash best practices.

---

## Sub-Problems

### Sub-Problem 1: File Backup (task_01_file_backup.yaml)
- Core logic: find files modified in last 24h, tar+gzip, timestamp naming, 14-day retention
- Special handling: incremental detection using `-mtime -1`; append to log file
- Expected output: `outputs/task_01_file_backup.sh` + `outputs/task_01_file_backup_readme.md`

### Sub-Problem 2: Log Rotation (task_02_log_rotation.yaml)
- Core logic: find oversized logs, compress old ones, delete aged ones, skip open files
- Special handling: `lsof` check before deletion; idempotent runs
- Expected output: `outputs/task_02_log_rotation.sh` + `outputs/task_02_log_rotation_readme.md`

### Sub-Problem 3: Database Dump (task_03_db_dump.yaml)
- Core logic: pg_dump to compressed file, aws s3 cp upload, verify object size, cleanup
- Special handling: dependency check (pg_dump, aws); 60-minute timeout via `timeout` command
- Expected output: `outputs/task_03_db_dump.sh` + `outputs/task_03_db_dump_readme.md`

### Sub-Problem 4: Directory Monitor (task_04_dir_monitor.yaml)
- Core logic: poll loop with sha256sum state file, diff against previous state, alert on change
- Special handling: ignore pattern filtering; SIGINT trap; 60-minute max runtime
- Expected output: `outputs/task_04_dir_monitor.sh` + `outputs/task_04_dir_monitor_readme.md`

### Sub-Problem 5: Multi-Node Sync (task_05_multi_node_sync.yaml)
- Core logic: SSH preflight per server, rsync with options, remote reload, per-server status table
- Special handling: `--dry-run` mode; continue on single-server failure; exit 0 only on full success
- Expected output: `outputs/task_05_multi_node_sync.sh` + `outputs/task_05_multi_node_sync_readme.md`

---

## Grading Criteria

- [ ] All 10 output files exist (5 scripts + 5 READMEs)
- [ ] Each `.sh` file starts with `#!/usr/bin/env bash` or `#!/bin/bash`
- [ ] Each `.sh` file contains `set -e` or `set -euo pipefail`
- [ ] Script 01 contains `tar` and a date/timestamp command
- [ ] Script 02 contains `gzip` or `compress` and `find` with `-mtime`
- [ ] Script 03 contains `pg_dump` and `aws s3`
- [ ] Script 04 contains a loop (`while`) and hash command (`sha256sum` or `md5sum`)
- [ ] Script 05 contains `rsync` and `ssh`
- [ ] Each README file is non-empty (> 50 bytes)

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    tasks = [
        ("task_01_file_backup",    [r"\btar\b", r"\bdate\b"]),
        ("task_02_log_rotation",   [r"\bgzip\b|compress", r"\bfind\b.*-mtime|-mtime.*\bfind\b"]),
        ("task_03_db_dump",        [r"\bpg_dump\b", r"\baws\b.*s3|s3.*\baws\b"]),
        ("task_04_dir_monitor",    [r"\bwhile\b", r"\bsha256sum\b|\bmd5sum\b"]),
        ("task_05_multi_node_sync",[r"\brsync\b", r"\bssh\b"]),
    ]

    for i, (task_id, patterns) in enumerate(tasks, start=1):
        prefix = f"sub_{i}"
        sh_path = workspace / "outputs" / f"{task_id}.sh"
        md_path = workspace / "outputs" / f"{task_id}_readme.md"

        # Check script exists
        sh_exists = sh_path.is_file()
        scores[f"{prefix}_sh_exists"] = 1.0 if sh_exists else 0.0

        # Check readme exists and non-empty
        md_exists = md_path.is_file() and md_path.stat().st_size > 50
        scores[f"{prefix}_readme_exists"] = 1.0 if md_exists else 0.0

        if not sh_exists:
            scores[f"{prefix}_shebang"] = 0.0
            scores[f"{prefix}_set_e"] = 0.0
            for j in range(len(patterns)):
                scores[f"{prefix}_pattern_{j+1}"] = 0.0
            continue

        content = sh_path.read_text(errors="replace")

        # Check shebang
        scores[f"{prefix}_shebang"] = 1.0 if re.search(r"^#!.*bash", content, re.MULTILINE) else 0.0

        # Check set -e
        scores[f"{prefix}_set_e"] = 1.0 if re.search(r"set\s+-[a-z]*e[a-z]*", content) else 0.0

        # Check task-specific patterns
        for j, pat in enumerate(patterns):
            scores[f"{prefix}_pattern_{j+1}"] = 1.0 if re.search(pat, content) else 0.0

    return scores
```

---

## LLM Judge Rubric

You are evaluating shell scripts generated by an AI agent from YAML specifications. Each script is in `outputs/` and has a corresponding `_readme.md`. Focus only on script quality — automated checks already verified structure.

Score the following criterion from 0.0 to 1.0:

**script_quality**: For each of the 5 scripts, does it correctly implement the key requirements from its YAML spec? Consider: (1) Does the main logic reflect the spec's requirements? (2) Are errors handled (the script won't silently fail)? (3) Are configurable values defined as variables, not hardcoded inline? A score of 1.0 means all 5 scripts are logically correct and production-ready. A score of 0.0 means scripts are stubs, contain obvious errors, or ignore major requirements. Return the average across all 5 scripts.
