#!/usr/bin/env bash
set -euo pipefail

WATCH_DIR="${WATCH_DIR:-/var/app/uploads}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-30}"
STATE_FILE="${STATE_FILE:-/tmp/dir_monitor_state.txt}"
ALERT_LOG="${ALERT_LOG:-/var/log/dir_alerts.log}"
MAX_RUNTIME_MINUTES="${MAX_RUNTIME_MINUTES:-60}"
IGNORE_PATTERNS=("${IGNORE_PATTERN_1:-*.tmp}" "${IGNORE_PATTERN_2:-.DS_Store}" "${IGNORE_PATTERN_3:-*.swp}")
HASH_CMD=""
STOP_REQUESTED=0

log_alert() {
  local message="$1"
  mkdir -p "$(dirname "$ALERT_LOG")"
  printf '%s\n' "$message" | tee -a "$ALERT_LOG"
}

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

on_sigint() {
  STOP_REQUESTED=1
  echo "Received SIGINT, stopping monitor..." >&2
}

trap on_sigint SIGINT

validate_config() {
  [[ -d "$WATCH_DIR" ]] || fail "Watch directory does not exist: $WATCH_DIR"
  [[ "$POLL_INTERVAL_SECONDS" =~ ^[0-9]+$ ]] || fail "POLL_INTERVAL_SECONDS must be an integer"
  [[ "$MAX_RUNTIME_MINUTES" =~ ^[0-9]+$ ]] || fail "MAX_RUNTIME_MINUTES must be an integer"
}

select_hash_command() {
  if command -v sha256sum >/dev/null 2>&1; then
    HASH_CMD="sha256sum"
  elif command -v md5sum >/dev/null 2>&1; then
    HASH_CMD="md5sum"
  else
    fail "Neither sha256sum nor md5sum is available"
  fi
}

should_ignore() {
  local path="$1"
  local name
  name="$(basename "$path")"

  for pattern in "${IGNORE_PATTERNS[@]}"; do
    if [[ "$name" == $pattern ]]; then
      return 0
    fi
  done
  return 1
}

snapshot_directory() {
  local output_file="$1"
  : > "$output_file"

  while IFS= read -r path; do
    [[ -f "$path" ]] || continue
    if should_ignore "$path"; then
      continue
    fi

    local hash
    hash="$($HASH_CMD "$path" | awk '{print $1}')"
    printf '%s|%s\n' "$hash" "$path" >> "$output_file"
  done < <(find "$WATCH_DIR" -type f | sort)
}

baseline_state() {
  mkdir -p "$(dirname "$STATE_FILE")"
  snapshot_directory "$STATE_FILE"
}

emit_changes() {
  local old_state="$1"
  local new_state="$2"
  local path hash size timestamp

  while IFS='|' read -r hash path; do
    [[ -n "$path" ]] || continue
    if ! grep -Fqx "$hash|$path" "$old_state" 2>/dev/null; then
      size="$(stat -f %z "$path")"
      timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
      log_alert "[ALERT] ${timestamp} New/modified file detected: ${path} (size: ${size})"
    fi
  done < "$new_state"
}

main() {
  require_command date
  require_command find
  require_command awk
  require_command grep
  require_command stat
  validate_config
  select_hash_command

  if [[ ! -f "$STATE_FILE" ]]; then
    baseline_state
    echo "Baseline created at $STATE_FILE"
    exit 0
  fi

  local start_epoch end_epoch tmp_state
  start_epoch="$(date +%s)"
  end_epoch=$((start_epoch + MAX_RUNTIME_MINUTES * 60))
  tmp_state="${STATE_FILE}.new"

  while (( STOP_REQUESTED == 0 )); do
    snapshot_directory "$tmp_state"
    emit_changes "$STATE_FILE" "$tmp_state"
    mv "$tmp_state" "$STATE_FILE"

    if (( $(date +%s) >= end_epoch )); then
      echo "Monitor runtime reached ${MAX_RUNTIME_MINUTES} minutes, exiting."
      break
    fi

    sleep "$POLL_INTERVAL_SECONDS"
  done
}

main "$@"
