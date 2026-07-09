#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/myapp}"
ROTATE_SIZE_MB="${ROTATE_SIZE_MB:-100}"
COMPRESS_AFTER_DAYS="${COMPRESS_AFTER_DAYS:-3}"
DELETE_AFTER_DAYS="${DELETE_AFTER_DAYS:-30}"
LOG_PATTERN="${LOG_PATTERN:-*.log}"
COMPRESSED_EXTENSION="${COMPRESSED_EXTENSION:-.gz}"
KEEP_LAST_N_UNCOMPRESSED="${KEEP_LAST_N_UNCOMPRESSED:-5}"

fail() { echo "Error: $*" >&2; exit 1; }

ensure_log_dir() {
  [[ -d "$LOG_DIR" ]] || mkdir -p "$LOG_DIR" || fail "Unable to create log directory: $LOG_DIR"
}

is_open_for_write() {
  local file="$1"
  lsof "$file" >/dev/null 2>&1
}

human_size_mb() {
  awk -v bytes="$1" 'BEGIN { printf "%.1f", bytes / 1024 / 1024 }'
}

rotate_file() {
  local file="$1" rotated
  rotated="${file}.$(date +%Y%m%d_%H%M%S)"
  mv "$file" "$rotated"
  : > "$file"
  gzip -f "$rotated"
  echo "rotated"
}

compress_file() {
  local file="$1"
  gzip -f "$file"
  echo "compressed"
}

cleanup_file() {
  local file="$1"
  rm -f "$file"
  echo "deleted"
}

main() {
  ensure_log_dir
  printf '%-40s %-10s %-8s %-15s\n' "filename" "size" "age" "action_taken"
  shopt -s nullglob
  local files=("$LOG_DIR"/$LOG_PATTERN)
  local count=0
  local now size age action
  now=$(date +%s)
  for file in "${files[@]}"; do
    [[ -f "$file" ]] || continue
    count=$((count + 1))
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    age=$(( (now - $(stat -f%m "$file" 2>/dev/null || stat -c%Y "$file")) / 86400 ))
    action="none"
    if [[ "$file" != *"$COMPRESSED_EXTENSION" ]] && (( size >= ROTATE_SIZE_MB * 1024 * 1024 )); then
      [[ ! -e "$file" || ! is_open_for_write "$file" ]] || { action="skipped_open"; printf '%-40s %-10s %-8s %-15s\n' "$(basename "$file")" "$(human_size_mb "$size")MB" "${age}d" "$action"; continue; }
      rotate_file "$file" >/dev/null
      action="rotated+compressed"
    elif [[ "$file" != *"$COMPRESSED_EXTENSION" ]] && (( age >= COMPRESS_AFTER_DAYS )); then
      [[ ! -e "$file" || ! is_open_for_write "$file" ]] || { action="skipped_open"; printf '%-40s %-10s %-8s %-15s\n' "$(basename "$file")" "$(human_size_mb "$size")MB" "${age}d" "$action"; continue; }
      compress_file "$file" >/dev/null
      action="compressed"
    elif [[ "$file" == *"$COMPRESSED_EXTENSION" ]] && (( age >= DELETE_AFTER_DAYS )); then
      [[ ! -e "$file" || ! is_open_for_write "$file" ]] || { action="skipped_open"; printf '%-40s %-10s %-8s %-15s\n' "$(basename "$file")" "$(human_size_mb "$size")MB" "${age}d" "$action"; continue; }
      cleanup_file "$file" >/dev/null
      action="deleted"
    fi
    printf '%-40s %-10s %-8s %-15s\n' "$(basename "$file")" "$(human_size_mb "$size")MB" "${age}d" "$action"
  done
  if (( count == 0 )); then
    echo "No matching log files found."
  fi
}

main
