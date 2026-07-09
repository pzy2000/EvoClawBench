# task_04_dir_monitor.sh

Purpose: Poll a directory for new or modified files without using inotify, store a persistent hash snapshot, ignore configured filename patterns, and emit alerts to both stdout and a log file.

## Usage

```bash
chmod +x outputs/task_04_dir_monitor.sh
./outputs/task_04_dir_monitor.sh
```

First run creates the baseline state file and exits without alerts.

## Required/configurable environment variables

- `WATCH_DIR` — directory to monitor. Default: `/var/app/uploads`
- `POLL_INTERVAL_SECONDS` — polling interval. Default: `30`
- `STATE_FILE` — persistent hash snapshot file. Default: `/tmp/dir_monitor_state.txt`
- `ALERT_LOG` — alert log file. Default: `/var/log/dir_alerts.log`
- `MAX_RUNTIME_MINUTES` — stop after this runtime. Default: `60`
- `IGNORE_PATTERN_1` — default: `*.tmp`
- `IGNORE_PATTERN_2` — default: `.DS_Store`
- `IGNORE_PATTERN_3` — default: `*.swp`

## Behavior notes

- Uses `sha256sum` when available, otherwise falls back to `md5sum`.
- Detects both new files and modified file content.
- Uses a `while` polling loop and a `SIGINT` trap so Ctrl+C stops it cleanly.
- Alerts are formatted as required and written to stdout and `ALERT_LOG`.

## Example output

```text
Baseline created at /tmp/dir_monitor_state.txt
[ALERT] 2026-07-10 03:15:22 New/modified file detected: /var/app/uploads/report.csv (size: 2048)
Monitor runtime reached 60 minutes, exiting.
```
