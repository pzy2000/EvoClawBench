#!/usr/bin/env bash
set -euo pipefail

# Cron: 30 2 * * *

SOURCE_DIR="${SOURCE_DIR:-/var/app/data}"
DEST_DIR="${DEST_DIR:-/mnt/backups}"
LOG_FILE="${LOG_FILE:-/var/log/backup.log}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
BACKUP_PREFIX="${BACKUP_PREFIX:-backup}"

fail() {
  echo "Error: $*" >&2
  exit 1
}

ensure_dirs() {
  [[ -d "$SOURCE_DIR" ]] || fail "Source directory not found: $SOURCE_DIR"
  mkdir -p "$DEST_DIR" || fail "Could not create destination directory: $DEST_DIR"
  mkdir -p "$(dirname "$LOG_FILE")" || fail "Could not create log directory"
}

create_backup() {
  local timestamp archive tmp_list file_count
  timestamp="$(date +%Y%m%d_%H%M%S)"
  archive="$DEST_DIR/${BACKUP_PREFIX}_${timestamp}.tar.gz"
  tmp_list="$(mktemp)"
  find "$SOURCE_DIR" -type f -mtime -1 -print > "$tmp_list"
  file_count="$(wc -l < "$tmp_list" | tr -d ' ')"
  if [[ "$file_count" == "0" ]]; then
    rm -f "$tmp_list"
    echo "Backup completed: no files modified in the last 24 hours."
    printf '%s SUCCESS file_count=0 archive=%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$archive" >> "$LOG_FILE"
    return 0
  fi
  tar -czf "$archive" -C "$SOURCE_DIR" -T "$tmp_list"
  rm -f "$tmp_list"
  printf '%s SUCCESS file_count=%s archive=%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$file_count" "$archive" >> "$LOG_FILE"
  echo "Backup completed: $file_count files archived to $archive"
}

cleanup_old_backups() {
  find "$DEST_DIR" -maxdepth 1 -type f -name "${BACKUP_PREFIX}_*.tar.gz" -mtime +"$RETENTION_DAYS" -delete
}

main() {
  ensure_dirs
  create_backup
  cleanup_old_backups
}

trap 'printf "%s FAILURE error=%s\n" "$(date '\''+%Y-%m-%d %H:%M:%S'\'')" "$?" >> "$LOG_FILE"; exit 1' ERR
main
