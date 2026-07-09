# Directory Change Monitoring

## Purpose
Monitors a directory for file additions and removals without using inotify, by comparing periodic snapshots.

## Usage
```bash
bash outputs/dir_monitor.sh
```

## Required env vars
- `WATCH_DIR` (default: `/var/app/watch`)
- `STATE_FILE` (default: `/tmp/dir_monitor.state`)
- `ALERT_RECIPIENT` (default: `stdout`)
- `MAX_DEPTH` (default: `3`)

## Example output
```text
Initialized baseline for /var/app/watch
```
Or:
```text
ALERT: Directory changes detected in /var/app/watch: added=2 removed=1
```
