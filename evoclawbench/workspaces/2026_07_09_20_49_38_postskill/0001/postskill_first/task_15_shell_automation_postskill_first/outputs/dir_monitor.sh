#!/usr/bin/env bash
set -euo pipefail

WATCH_DIR="/var/app/uploads"
POLL_INTERVAL_SECONDS=30
STATE_FILE="/tmp/dir_monitor_state.txt"
ALERT_LOG="/var/log/dir_alerts.log"
MAX_RUNTIME_MINUTES=60
IGNORE_PATTERNS=('*.tmp' '.DS_Store' '*.swp')

running=true
trap 'running=false' SIGINT

should_ignore() {
  local path="$1"
  local pat
  for pat in "${IGNORE_PATTERNS[@]}"; do
    [[ "$path" == $pat ]] && return 0
  done
  return 1
}

snapshot_dir() {
  find "$WATCH_DIR" -type f | sort | while IFS= read -r file; do
    local rel size hash
    rel="${file#$WATCH_DIR/}"
    should_ignore "$rel" && continue
    size=$(stat -c %s "$file")
    hash=$(sha256sum "$file" | awk '{print $1}')
    printf '%s\t%s\t%s\n' "$rel" "$size" "$hash"
  done
}

load_state() {
  if [[ -f "$STATE_FILE" ]]; then cat "$STATE_FILE"; fi
}

save_state() {
  local tmp
  tmp="$(mktemp)"
  snapshot_dir > "$tmp"
  mv "$tmp" "$STATE_FILE"
}

alert_change() {
  local rel="$1" size="$2"
  local line
  line="[ALERT] $(date '+%Y-%m-%d %H:%M:%S') New/modified file detected: ${WATCH_DIR}/${rel} (size: ${size})"
  echo "$line" | tee -a "$ALERT_LOG"
}

main() {
  mkdir -p "$(dirname "$STATE_FILE")" "$(dirname "$ALERT_LOG")"
  touch "$ALERT_LOG"

  if [[ ! -d "$WATCH_DIR" ]]; then
    echo "Error: watch directory does not exist: $WATCH_DIR" >&2
    exit 1
  fi

  if [[ ! -f "$STATE_FILE" ]]; then
    save_state
    echo "Baseline created; no alerts emitted"
  fi

  start_ts=$(date +%s)
  runtime_limit=$(( MAX_RUNTIME_MINUTES * 60 ))

  while $running; do
    current="$(snapshot_dir)"
    previous="$(load_state)"

    if [[ "$current" != "$previous" ]]; then
      while IFS=$'\t' read -r rel size hash; do
        [[ -z "${rel:-}" ]] && continue
        if ! grep -Fqx "$rel" "$STATE_FILE" 2>/dev/null; then
          alert_change "$rel" "$size"
        else
          old_hash="$(awk -F '\t' -v f="$rel" '$1==f {print $3}' "$STATE_FILE" | head -n1)"
          if [[ "$old_hash" != "$hash" ]]; then
            alert_change "$rel" "$size"
          fi
        fi
      done <<< "$current"
      printf '%s\n' "$current" > "$STATE_FILE"
    fi

    if (( $(date +%s) - start_ts >= runtime_limit )); then
      echo "Monitor exiting after reaching max runtime"
      break
    fi

    sleep "$POLL_INTERVAL_SECONDS"
  done
}

main "$@"
