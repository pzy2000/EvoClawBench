# Database Dump and Upload

## Purpose
Dumps the PostgreSQL database `production_db`, compresses the dump, uploads it to S3-compatible storage, verifies the upload, and removes the local dump on success.

## Usage
```bash
export PGPASSWORD='your-password'
./outputs/db_dump.sh
```

## Required environment variables
- `PGPASSWORD`

## Notes
- Requires `pg_dump` and `aws` CLI.
- Logs to `/var/log/db_backup.log`.

## Example output
```text
Backup complete: uploaded and removed local dump (1843200 bytes)
```