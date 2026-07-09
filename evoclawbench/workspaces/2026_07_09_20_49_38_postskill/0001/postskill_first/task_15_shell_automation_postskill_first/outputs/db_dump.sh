#!/usr/bin/env bash
set -euo pipefail

PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-postgres}"
PGUSER="${PGUSER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-./db_backups}"
S3_BUCKET="${S3_BUCKET:-}"
S3_KEY_PREFIX="${S3_KEY_PREFIX:-database-dumps}"
AWS_REGION="${AWS_REGION:-us-east-1}"

fail() { echo "Error: $*" >&2; exit 1; }

require_cmd() { command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"; }

main() {
  require_cmd pg_dump
  require_cmd gzip
  [[ -n "$S3_BUCKET" ]] || fail "S3_BUCKET is required"
  mkdir -p "$BACKUP_DIR" || fail "Unable to create backup dir: $BACKUP_DIR"

  local ts dump_file gz_file s3_uri
  ts="$(date +%Y%m%d_%H%M%S)"
  dump_file="$BACKUP_DIR/${PGDATABASE}_${ts}.sql"
  gz_file="$dump_file.gz"
  s3_uri="s3://${S3_BUCKET}/${S3_KEY_PREFIX}/${PGDATABASE}_${ts}.sql.gz"

  echo "Running pg_dump for $PGDATABASE..."
  pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" > "$dump_file" || fail "pg_dump failed"
  gzip -f "$dump_file" || fail "Compression failed"

  if command -v aws >/dev/null 2>&1; then
    aws s3 cp "$gz_file" "$s3_uri" --region "$AWS_REGION" || fail "S3 upload failed"
  elif command -v s3cmd >/dev/null 2>&1; then
    s3cmd put "$gz_file" "$s3_uri" || fail "S3 upload failed"
  else
    fail "Neither aws nor s3cmd found for S3 upload"
  fi

  echo "Backup complete: $gz_file uploaded to $s3_uri"
}

main
