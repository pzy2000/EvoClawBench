#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

LOCAL_CONFIG_DIR="/etc/myapp/config/"
REMOTE_SERVERS=("web01.internal:22" "web02.internal:22" "web03.internal:22")
REMOTE_PATH="/etc/myapp/config/"
SSH_USER="deploy"
SSH_KEY="/home/deploy/.ssh/id_rsa"
EXCLUDES=("*.bak" "*.tmp" "secrets.conf")

print_dry() { echo "[dry-run] $*"; }

check_ssh() {
  local host="$1" port="$2"
  ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 -p "$port" "${SSH_USER}@${host}" "true"
}

ensure_remote_path() {
  local host="$1" port="$2"
  ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 -p "$port" "${SSH_USER}@${host}" "mkdir -p '$REMOTE_PATH'"
}

sync_server() {
  local server="$1" host="${server%%:*}" port="${server##*:}"
  local start end duration sync_status reload_status
  start=$(date +%s)
  sync_status="ok"
  reload_status="ok"

  if $DRY_RUN; then
    print_dry "Would check SSH for $server, ensure $REMOTE_PATH, rsync config, and reload myapp"
    echo "$host | dry-run | dry-run | 0"
    return 0
  fi

  if ! check_ssh "$host" "$port"; then
    echo "$host | fail | skip | 0"
    return 1
  fi

  ensure_remote_path "$host" "$port"

  rsync_args=(-az --delete -e "ssh -i $SSH_KEY -p $port")
  for ex in "${EXCLUDES[@]}"; do rsync_args+=(--exclude="$ex"); done
  if ! rsync "${rsync_args[@]}" "$LOCAL_CONFIG_DIR" "${SSH_USER}@${host}:$REMOTE_PATH"; then
    sync_status="fail"
  fi

  if [[ "$sync_status" == "ok" ]]; then
    if ! ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 -p "$port" "${SSH_USER}@${host}" "sudo systemctl reload myapp"; then
      reload_status="fail"
    fi
  else
    reload_status="skip"
  fi

  end=$(date +%s)
  duration=$(( end - start ))
  echo "$host | $sync_status | $reload_status | $duration"
  [[ "$sync_status" == "ok" && "$reload_status" == "ok" ]]
}

main() {
  local failed_reload=()
  printf '%-18s %-12s %-12s %-10s\n' "server" "sync_status" "reload_status" "duration_s"
  for server in "${REMOTE_SERVERS[@]}"; do
    if ! output=$(sync_server "$server"); then
      echo "$output"
      if [[ "$output" == *"| fail | fail"* ]]; then failed_reload+=("${server%%:*}"); fi
    else
      echo "$output"
    fi
  done

  if ((${#failed_reload[@]} > 0)); then
    echo "Manual rollback needed for: ${failed_reload[*]}" >&2
    exit 1
  fi
}

main "$@"
