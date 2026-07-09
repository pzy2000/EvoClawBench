# Scheduled File Backup

## Purpose
Backs up files modified in the last 24 hours from `/var/app/data` into `/mnt/backups` as a timestamped `tar.gz` archive, then removes backup archives older than 14 days.

## Usage
```bash
bash outputs/file_backup.sh
```

## Required env vars
- `SOURCE_DIR` (default: `/var/app/data`)
- `DEST_DIR` (default: `/mnt/backups`)
- `LOG_FILE` (default: `/var/log/backup.log`)
- `RETENTION_DAYS` (default: `14`)
- `BACKUP_PREFIX` (default: `backup`)

## Example output
```text
Backup completed: 12 files archived to /mnt/backups/backup_20240320_023000.tar.gz
```

## Cron
Run daily at 02:30 AM:
```cron
30 2 * * *
```