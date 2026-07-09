# task_01_file_backup.sh

Purpose: Create a scheduled incremental `tar.gz` backup of files modified within the last 24 hours, retain recent archives, append run results to a log file, and print a completion summary.

## Usage

```bash
chmod +x outputs/task_01_file_backup.sh
./outputs/task_01_file_backup.sh
```

## Required/configurable environment variables

- `SOURCE_DIR` — source directory to scan. Default: `/var/app/data`
- `DEST_DIR` — destination directory for archives. Default: `/mnt/backups`
- `LOG_FILE` — append-only run log. Default: `/var/log/backup.log`
- `RETENTION_DAYS` — delete archives older than this many days. Default: `14`
- `INCREMENTAL_HOURS` — modified-file window. Default: `24`
- `BACKUP_PREFIX` — archive filename prefix. Default: `backup`

## Behavior notes

- Includes a cron comment for `02:30` daily scheduling.
- Uses `find` to build the incremental file list.
- Uses `tar -czf` to create `backup_YYYYMMDD_HHMMSS.tar.gz`.
- Creates a valid empty archive if no files changed in the last 24 hours.
- Logs timestamp, status, archive path, and file count.
- Removes old archives with `find ... -mtime` retention cleanup.

## Example output

```text
Backup completed: archive=/mnt/backups/backup_20260710_023000.tar.gz status=success file_count=17
```
