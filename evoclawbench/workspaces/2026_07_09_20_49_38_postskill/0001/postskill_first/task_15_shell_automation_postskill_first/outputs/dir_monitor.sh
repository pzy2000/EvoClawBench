#!/usr/bin/env bash
set -euo pipefail

WATCH_DIR="${WATCH_DIR:-/var/app/watch}"
STATE_FILE="${STATE_FILE:-/tmp/dir_monitor.state}"
ALERT_RECIPIENT="${ALERT_RECIPIENT:-stdout}"
MAX_DEPTH="${MAX_DEPTH:-3}"

fail() { echo "Error: $*" >&2; exit 1; }

snapshot_dir() {
  find "$WATCH_DIR" -maxdepth "$MAX_DEPTH" -type f -printf '%P|%s|%T@\n' | sort
}

alert() {
  local message="$1"
  if [[ "$ALERT_RECIPIENT" == "stdout" ]]; then
    echo "ALERT: $message"
  else
    printf '%s\n' "$message" | mail -s "Directory change alert" "$ALERT_RECIPIENT"
  fi
}

main() {
  [[ -d "$WATCH_DIR" ]] || fail "Watch directory does not exist: $WATCH_DIR"
  mkdir -p "$(dirname "$STATE_FILE")" || fail "Unable to create state directory"

  local current previous added removed changed
  current="$(mktemp)"
  snapshot_dir > "$current"

  if [[ ! -f "$STATE_FILE" ]]; then
    mv "$current" "$STATE_FILE"
    echo "Initialized baseline for $WATCH_DIR"
    return 0
  fi

  previous="$(mktemp)"
  cp "$STATE_FILE" "$previous"

  added=$(comm -13 "$previous" "$current" | wc -l | tr -d ' ')
  removed=$(comm -23 "$previous" "$current" | wc -l | tr -d ' ')
  changed=0
  if [[ "$added" -gt 0 || "$removed" -gt 0 ]]; then
    changed=1
    alert "Directory changes detected in $WATCH_DIR: added=$added removed=$removed"
  else
    echo "No changes detected in $WATCH_DIR"
  fi

  mv "$current" "$STATE_FILE"
  rm -f "$previous"
  (( changed == 0 )) || true
}

main
