#!/usr/bin/env bash
set -euo pipefail

# Cron schedule: 30 2 * * * /path/to/task_01_file_backup.sh

SOURCE_DIR="${SOURCE_DIR:-/var/app/data}"
DEST_DIR="${DEST_DIR:-/mnt/backups}"
LOG_FILE="${LOG_FILE:-/var/log/backup.log}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
INCREMENTAL_HOURS="${INCREMENTAL_HOURS:-24}"
BACKUP_PREFIX="${BACKUP_PREFIX:-backup}"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
ARCHIVE_FILE="${DEST_DIR}/${BACKUP_PREFIX}_${TIMESTAMP}.tar.gz"
TMP_FILE_LIST="${TMPDIR:-/tmp}/${BACKUP_PREFIX}_${TIMESTAMP}_files.txt"

log() {
  local message="$1"
  mkdir -p "$(dirname "$LOG_FILE")"
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >> "$LOG_FILE"
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

cleanup() {
  rm -f "$TMP_FILE_LIST"
}

validate_config() {
  [[ -d "$SOURCE_DIR" ]] || fail "Source directory does not exist: $SOURCE_DIR"
  mkdir -p "$DEST_DIR" || fail "Unable to create destination directory: $DEST_DIR"
  [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || fail "RETENTION_DAYS must be an integer"
  [[ "$INCREMENTAL_HOURS" =~ ^[0-9]+$ ]] || fail "INCREMENTAL_HOURS must be an integer"
}

build_file_list() {
  # Build a deterministic list of files changed within the incremental window.
  find "$SOURCE_DIR" -type f -mmin "-$((INCREMENTAL_HOURS * 60))" | sort > "$TMP_FILE_LIST"
}

create_archive() {
  local file_count
  file_count="$(wc -l < "$TMP_FILE_LIST" | tr -d ' ')"

  if [[ "$file_count" -eq 0 ]]; then
    # Create a valid empty tar.gz when there are no recent changes.
    tar -czf "$ARCHIVE_FILE" --files-from /dev/null || fail "Failed to create empty tar.gz archive"
    return 0
  fi

  tar -czf "$ARCHIVE_FILE" -T "$TMP_FILE_LIST" || fail "tar backup creation failed"
}

cleanup_old_archives() {
  find "$DEST_DIR" -type f -name "${BACKUP_PREFIX}_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete || fail "Retention cleanup failed"
}

main() {
  trap cleanup EXIT

  require_command date
  require_command find
  require_command tar
  validate_config

  build_file_list

  local file_count
  file_count="$(wc -l < "$TMP_FILE_LIST" | tr -d ' ')"

  create_archive
  cleanup_old_archives

  log "SUCCESS archive=${ARCHIVE_FILE} file_count=${file_count}"
  echo "Backup completed: archive=${ARCHIVE_FILE} status=success file_count=${file_count}"
}

main "$@"
