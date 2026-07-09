# PostgreSQL Dump, Compression, and S3 Upload

## Purpose
Creates a PostgreSQL dump, compresses it with gzip, and uploads the archive to S3.

## Usage
```bash
bash outputs/db_dump.sh
```

## Required env vars
- `PGHOST` (default: `localhost`)
- `PGPORT` (default: `5432`)
- `PGDATABASE` (default: `postgres`)
- `PGUSER` (default: `postgres`)
- `BACKUP_DIR` (default: `./db_backups`)
- `S3_BUCKET` (required)
- `S3_KEY_PREFIX` (default: `database-dumps`)
- `AWS_REGION` (default: `us-east-1`)

## Example output
```text
Running pg_dump for appdb...
Backup complete: ./db_backups/appdb_20260709_214500.sql.gz uploaded to s3://my-bucket/database-dumps/appdb_20260709_214500.sql.gz
```
