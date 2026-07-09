# task_03_db_dump.sh

Purpose: Dump a PostgreSQL database with `pg_dump`, compress the dump, upload it with `aws s3 cp`, verify the uploaded object size is greater than zero, and remove the local artifact only after success.

## Usage

```bash
chmod +x outputs/task_03_db_dump.sh
export PGPASSWORD='supersecret'
./outputs/task_03_db_dump.sh
```

## Required/configurable environment variables

- `DB_HOST` — database host. Default: `localhost`
- `DB_PORT` — database port. Default: `5432`
- `DB_NAME` — database name. Default: `production_db`
- `DB_USER` — database user. Default: `backup_user`
- `PGPASSWORD` — required PostgreSQL password environment variable
- `DUMP_DIR` — local dump directory. Default: `/tmp/db_dumps`
- `S3_BUCKET` — destination bucket/prefix. Default: `s3://company-db-backups/postgres/`
- `LOG_FILE` — backup log file. Default: `/var/log/db_backup.log`
- `TIMEOUT_MINUTES` — max dump runtime. Default: `60`

## Dependencies

- `pg_dump`
- `aws`
- `gzip`
- `timeout` or `gtimeout`

## Behavior notes

- Keeps local dump files on failure.
- Writes start time, end time, and compressed dump size to the log.
- Upload verification checks that the remote S3 object size is numeric and greater than zero.

## Example output

```text
Database backup completed: file=production_db_20260710_021500.sql.gz uploaded_to=s3://company-db-backups/postgres/production_db_20260710_021500.sql.gz size_bytes=4821931
```
