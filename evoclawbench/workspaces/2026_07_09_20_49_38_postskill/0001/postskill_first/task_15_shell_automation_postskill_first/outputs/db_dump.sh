#!/usr/bin/env bash
set -euo pipefail

DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="production_db"
DB_USER="backup_user"
DUMP_DIR="/tmp/db_dumps"
S3_BUCKET="s3://company-db-backups/postgres/"
LOG_FILE="/var/log/db_backup.log"
TIMEOUT_MINUTES=60

require_tool() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required tool: $1" >&2; exit 1; }
}

log_msg() {
  local msg="$1"
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$msg" | tee -a "$LOG_FILE" >/dev/null
}

main() {
  require_tool pg_dump
  require_tool aws
  mkdir -p "$DUMP_DIR"
  touch "$LOG_FILE"

  local ts dump_file
  ts="$(date '+%Y%m%d_%H%M%S')"
  dump_file="${DUMP_DIR}/${DB_NAME}_${ts}.sql.gz"

  log_msg "START db=${DB_NAME} host=${DB_HOST}:${DB_PORT} file=${dump_file}"

  if ! timeout "${TIMEOUT_MINUTES}m" bash -c "PGPASSWORD=\"${PGPASSWORD:-}\" pg_dump -h '$DB_HOST' -p '$DB_PORT' -U '$DB_USER' '$DB_NAME' | gzip > '$dump_file'"; then
    log_msg "FAIL dump_failed file=${dump_file}"
    echo "Error: database dump failed" >&2
    exit 1
  fi

  size_bytes=$(stat -c %s "$dump_file")
  if [[ "$size_bytes" -le 0 ]]; then
    log_msg "FAIL empty_dump file=${dump_file}"
    echo "Error: dump file is empty" >&2
    exit 1
  fi

  if ! aws s3 cp "$dump_file" "$S3_BUCKET"; then
    log_msg "FAIL upload_failed file=${dump_file} size=${size_bytes}"
    echo "Error: upload failed" >&2
    exit 1
  fi

  remote_key="${S3_BUCKET}${DB_NAME}_${ts}.sql.gz"
  remote_size=$(aws s3 ls "$remote_key" 2>/dev/null | awk '{print $3}' || true)
  if [[ -z "${remote_size:-}" || "$remote_size" -le 0 ]]; then
    log_msg "FAIL verify_failed file=${dump_file}"
    echo "Error: upload verification failed" >&2
    exit 1
  fi

  rm -f "$dump_file"
  log_msg "END success size=${size_bytes} file=${dump_file}"
  echo "Backup complete: uploaded and removed local dump (${size_bytes} bytes)"
}

main "$@"
