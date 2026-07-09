#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/myapp}"
ROTATE_SIZE_MB="${ROTATE_SIZE_MB:-100}"
COMPRESS_AFTER_DAYS="${COMPRESS_AFTER_DAYS:-3}"
DELETE_AFTER_DAYS="${DELETE_AFTER_DAYS:-30}"
LOG_PATTERN="${LOG_PATTERN:-*.log}"
COMPRESSED_EXTENSION="${COMPRESSED_EXTENSION:-.gz}"
KEEP_LAST_N_UNCOMPRESSED="${KEEP_LAST_N_UNCOMPRESSED:-5}"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

SUMMARY_ROWS=()

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >&2
}

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

validate_config() {
  [[ "$ROTATE_SIZE_MB" =~ ^[0-9]+$ ]] || fail "ROTATE_SIZE_MB must be an integer"
  [[ "$COMPRESS_AFTER_DAYS" =~ ^[0-9]+$ ]] || fail "COMPRESS_AFTER_DAYS must be an integer"
  [[ "$DELETE_AFTER_DAYS" =~ ^[0-9]+$ ]] || fail "DELETE_AFTER_DAYS must be an integer"
  [[ "$KEEP_LAST_N_UNCOMPRESSED" =~ ^[0-9]+$ ]] || fail "KEEP_LAST_N_UNCOMPRESSED must be an integer"
}

add_summary() {
  local filename="$1"
  local size="$2"
  local age="$3"
  local action_taken="$4"
  SUMMARY_ROWS+=("${filename}|${size}|${age}|${action_taken}")
}

file_age_days() {
  local file="$1"
  local now epoch
  now="$(date +%s)"
  epoch="$(stat -f %m "$file")"
  echo $(((now - epoch) / 86400))
}

file_size_bytes() {
  stat -f %z "$1"
}

rotate_logs() {
  local threshold_bytes
  threshold_bytes=$((ROTATE_SIZE_MB * 1024 * 1024))

  while IFS= read -r file; do
    [[ -f "$file" ]] || continue

    local size age rotated_file
    size="$(file_size_bytes "$file")"
    age="$(file_age_days "$file")"

    if lsof "$file" >/dev/null 2>&1; then
      add_summary "$file" "$size" "$age" "skipped_open"
      continue
    fi

    if (( size < threshold_bytes )); then
      add_summary "$file" "$size" "$age" "no_rotation"
      continue
    fi

    rotated_file="${file}.${TIMESTAMP}"
    mv "$file" "$rotated_file"
    : > "$file"
    add_summary "$file" "$size" "$age" "rotated_to_${rotated_file##*/}"
  done < <(find "$LOG_DIR" -maxdepth 1 -type f -name "$LOG_PATTERN" | sort)
}

compress_old_rotations() {
  local base

  while IFS= read -r base; do
    local rotations=()
    local idx=0

    while IFS= read -r rotation; do
      rotations+=("$rotation")
    done < <(find "$LOG_DIR" -maxdepth 1 -type f -name "$(basename "$base").*" ! -name "*.gz" | sort -r)

    for rotation in "${rotations[@]}"; do
      idx=$((idx + 1))
      [[ -f "$rotation" ]] || continue

      local age size
      age="$(file_age_days "$rotation")"
      size="$(file_size_bytes "$rotation")"

      if (( idx <= KEEP_LAST_N_UNCOMPRESSED )); then
        add_summary "$rotation" "$size" "$age" "kept_uncompressed"
        continue
      fi

      if (( age >= COMPRESS_AFTER_DAYS )); then
        gzip -f "$rotation"
        add_summary "${rotation}${COMPRESSED_EXTENSION}" "$size" "$age" "compressed"
      else
        add_summary "$rotation" "$size" "$age" "awaiting_compress_age"
      fi
    done
  done < <(find "$LOG_DIR" -maxdepth 1 -type f -name "$LOG_PATTERN" | sort)
}

cleanup_expired_compressed() {
  while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    local age size
    age="$(file_age_days "$file")"
    size="$(file_size_bytes "$file")"
    rm -f "$file"
    add_summary "$file" "$size" "$age" "deleted"
  done < <(find "$LOG_DIR" -maxdepth 1 -type f -name "*${COMPRESSED_EXTENSION}" -mtime "+$DELETE_AFTER_DAYS" | sort)
}

print_summary_table() {
  printf '%-50s %-12s %-8s %-24s\n' "filename" "size_bytes" "age_d" "action_taken"
  printf '%-50s %-12s %-8s %-24s\n' "--------" "----------" "-----" "------------"
  for row in "${SUMMARY_ROWS[@]}"; do
    IFS='|' read -r filename size age action_taken <<< "$row"
    printf '%-50s %-12s %-8s %-24s\n' "$filename" "$size" "$age" "$action_taken"
  done
}

main() {
  require_command date
  require_command find
  require_command gzip
  require_command lsof
  require_command stat
  validate_config

  if [[ ! -d "$LOG_DIR" ]]; then
    mkdir -p "$LOG_DIR" || {
      log "log_dir missing and could not be created: $LOG_DIR"
      exit 0
    }
  fi

  rotate_logs
  compress_old_rotations
  cleanup_expired_compressed
  print_summary_table
}

main "$@"
