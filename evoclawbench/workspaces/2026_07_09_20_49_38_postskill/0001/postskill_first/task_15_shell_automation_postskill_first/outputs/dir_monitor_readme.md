# Directory Change Monitor

## Purpose
Polls `/var/app/uploads` for new or modified files without inotify, tracks hashes in a state file, and alerts on change.

## Usage
```bash
./outputs/dir_monitor.sh
```

## Required environment variables
None.

## Notes
- Baselines the directory on first run with no alerts.
- Alerts are appended to `/var/log/dir_alerts.log`.

## Example output
```text
Baseline created; no alerts emitted
[ALERT] 2024-03-20 02:30:00 New/modified file detected: /var/app/uploads/report.csv (size: 2048)
```