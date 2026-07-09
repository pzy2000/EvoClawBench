#!/usr/bin/env bash
set -euo pipefail

LOCAL_CONFIG_DIR="${LOCAL_CONFIG_DIR:-/etc/myapp/config/}"
REMOTE_PATH="${REMOTE_PATH:-/etc/myapp/config/}"
SSH_USER="${SSH_USER:-deploy}"
SSH_KEY="${SSH_KEY:-/home/deploy/.ssh/id_rsa}"
SSH_TIMEOUT_SECONDS="${SSH_TIMEOUT_SECONDS:-5}"
REMOTE_RELOAD_CMD="${REMOTE_RELOAD_CMD:-sudo systemctl reload myapp}"
REMOTE_SERVERS=(
  "${REMOTE_SERVER_1:-web01.internal:22}"
  "${REMOTE_SERVER_2:-web02.internal:22}"
  "${REMOTE_SERVER_3:-web03.internal:22}"
)
RSYNC_EXCLUDES=("*.bak" "*.tmp" "secrets.conf")
DRY_RUN=0
RESULT_ROWS=()
ROLLBACK_NEEDED=()
ALL_OK=1

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

add_result() {
  local server="$1"
  local sync_status="$2"
  local reload_status="$3"
  local duration_s="$4"
  RESULT_ROWS+=("${server}|${sync_status}|${reload_status}|${duration_s}")
}

run_ssh() {
  local host="$1"
  local port="$2"
  shift 2

  if (( DRY_RUN == 1 )); then
    echo "[DRY-RUN] ssh -i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=$SSH_TIMEOUT_SECONDS -p $port $SSH_USER@$host $*"
    return 0
  fi

  ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout="$SSH_TIMEOUT_SECONDS" -p "$port" "$SSH_USER@$host" "$@"
}

sync_server() {
  local server="$1"
  local host port start_epoch duration_s sync_status reload_status
  start_epoch="$(date +%s)"
  sync_status="failed"
  reload_status="skipped"

  host="${server%%:*}"
  port="${server##*:}"

  if ! run_ssh "$host" "$port" "mkdir -p '$REMOTE_PATH'"; then
    duration_s=$(( $(date +%s) - start_epoch ))
    add_result "$server" "ssh_preflight_failed" "$reload_status" "$duration_s"
    ALL_OK=0
    return 0
  fi

  local rsync_args=(
    -az
    --delete
    --times
    --perms
    --exclude "*.bak"
    --exclude "*.tmp"
    --exclude "secrets.conf"
    -e "ssh -i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=$SSH_TIMEOUT_SECONDS -p $port"
  )

  if (( DRY_RUN == 1 )); then
    rsync_args+=(--dry-run)
  fi

  if rsync "${rsync_args[@]}" "$LOCAL_CONFIG_DIR" "$SSH_USER@$host:$REMOTE_PATH"; then
    sync_status="ok"
  else
    duration_s=$(( $(date +%s) - start_epoch ))
    add_result "$server" "rsync_failed" "$reload_status" "$duration_s"
    ALL_OK=0
    return 0
  fi

  if run_ssh "$host" "$port" "$REMOTE_RELOAD_CMD"; then
    reload_status="ok"
  else
    reload_status="failed"
    ROLLBACK_NEEDED+=("$server")
    ALL_OK=0
  fi

  duration_s=$(( $(date +%s) - start_epoch ))
  add_result "$server" "$sync_status" "$reload_status" "$duration_s"
}

print_report() {
  printf '%-22s %-18s %-16s %-10s\n' "server" "sync_status" "reload_status" "duration_s"
  printf '%-22s %-18s %-16s %-10s\n' "------" "-----------" "-------------" "----------"
  local row
  for row in "${RESULT_ROWS[@]}"; do
    IFS='|' read -r server sync_status reload_status duration_s <<< "$row"
    printf '%-22s %-18s %-16s %-10s\n' "$server" "$sync_status" "$reload_status" "$duration_s"
  done

  if (( ${#ROLLBACK_NEEDED[@]} > 0 )); then
    echo
    echo "Manual rollback required on these servers: ${ROLLBACK_NEEDED[*]}"
  fi
}

main() {
  require_command ssh
  require_command rsync
  require_command date

  [[ -d "$LOCAL_CONFIG_DIR" ]] || fail "Local config directory does not exist: $LOCAL_CONFIG_DIR"

  if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    shift
  fi

  local server
  for server in "${REMOTE_SERVERS[@]}"; do
    sync_server "$server"
  done

  print_report

  if (( ALL_OK == 1 )); then
    exit 0
  fi
  exit 1
}

main "$@"
