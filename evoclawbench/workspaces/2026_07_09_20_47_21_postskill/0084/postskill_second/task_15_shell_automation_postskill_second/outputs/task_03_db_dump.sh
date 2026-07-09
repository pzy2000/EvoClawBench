#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-production_db}"
DB_USER="${DB_USER:-backup_user}"
DUMP_DIR="${DUMP_DIR:-/tmp/db_dumps}"
S3_BUCKET="${S3_BUCKET:-s3://company-db-backups/postgres/}"
LOG_FILE="${LOG_FILE:-/var/log/db_backup.log}"
TIMEOUT_MINUTES="${TIMEOUT_MINUTES:-60}"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
DUMP_SQL_FILE="${DUMP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"
DUMP_GZ_FILE="${DUMP_SQL_FILE}.gz"
S3_OBJECT="${S3_BUCKET%/}/$(basename "$DUMP_GZ_FILE")"

log() {
  mkdir -p "$(dirname "$LOG_FILE")"
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

fail() {
  local message="$1"
  log "FAILURE ${message}"
  echo "ERROR: ${message}" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

dump_size_bytes() {
  stat -f %z "$1"
}

validate_config() {
  [[ -n "${PGPASSWORD:-}" ]] || fail "PGPASSWORD environment variable is required"
  [[ "$TIMEOUT_MINUTES" =~ ^[0-9]+$ ]] || fail "TIMEOUT_MINUTES must be an integer"
  mkdir -p "$DUMP_DIR" || fail "Unable to create dump directory: $DUMP_DIR"
}

run_with_timeout() {
  local timeout_seconds
  timeout_seconds=$((TIMEOUT_MINUTES * 60))

  if command -v timeout >/dev/null 2>&1; then
    timeout "$timeout_seconds" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$timeout_seconds" "$@"
  else
    fail "Neither timeout nor gtimeout is available"
  fi
}

perform_dump() {
  PGPASSWORD="$PGPASSWORD" run_with_timeout pg_dump \
    --host "$DB_HOST" \
    --port "$DB_PORT" \
    --username "$DB_USER" \
    --format plain \
    --file "$DUMP_SQL_FILE" \
    "$DB_NAME" || fail "pg_dump failed"
}

compress_dump() {
  gzip -f "$DUMP_SQL_FILE" || fail "gzip compression failed"
  [[ -s "$DUMP_GZ_FILE" ]] || fail "Compressed dump is empty: $DUMP_GZ_FILE"
}

upload_dump() {
  aws s3 cp "$DUMP_GZ_FILE" "$S3_OBJECT" || fail "aws s3 cp upload failed"
}

verify_upload() {
  local size
  size="$(aws s3 ls "$S3_OBJECT" | awk '{print $3}')"
  [[ -n "$size" ]] || fail "Unable to determine remote object size for $S3_OBJECT"
  [[ "$size" =~ ^[0-9]+$ ]] || fail "Remote object size is not numeric: $size"
  (( size > 0 )) || fail "Remote object size is zero for $S3_OBJECT"
}

cleanup_local_on_success() {
  rm -f "$DUMP_GZ_FILE" || fail "Failed to delete local dump after successful upload"
}

main() {
  require_command pg_dump
  require_command aws
  require_command gzip
  require_command awk
  require_command stat
  validate_config

  local start_time end_time size_bytes
  start_time="$(date '+%Y-%m-%d %H:%M:%S')"
  log "START db=${DB_NAME} file=${DUMP_GZ_FILE} start_time=${start_time}"

  perform_dump
  compress_dump
  upload_dump
  verify_upload

  size_bytes="$(dump_size_bytes "$DUMP_GZ_FILE")"
  end_time="$(date '+%Y-%m-%d %H:%M:%S')"
  log "SUCCESS db=${DB_NAME} file=${DUMP_GZ_FILE} size_bytes=${size_bytes} start_time=${start_time} end_time=${end_time}"

  cleanup_local_on_success
  echo "Database backup completed: file=$(basename "$DUMP_GZ_FILE") uploaded_to=${S3_OBJECT} size_bytes=${size_bytes}"
}

main "$@"
