#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${SOURCE_DIR:-/etc/myapp}"
TARGETS="${TARGETS:-server1:/etc/myapp server2:/etc/myapp}"
SSH_OPTS="${SSH_OPTS:--o BatchMode=yes}"
RSYNC_OPTS="${RSYNC_OPTS:--aH --delete --numeric-ids}"
BACKUP_SUFFIX="${BACKUP_SUFFIX:-.backup}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-1}"

fail() { echo "Error: $*" >&2; exit 1; }

backup_remote() {
  local target="$1" remote_path="$2"
  ssh $SSH_OPTS "$target" "test -e '$remote_path' && cp -a '$remote_path' '${remote_path}${BACKUP_SUFFIX}' || true"
}

sync_target() {
  local target="$1" remote_path="$2"
  backup_remote "$target" "$remote_path"
  rsync $RSYNC_OPTS "$SOURCE_DIR"/ "$target":"$remote_path"/
}

rollback_target() {
  local target="$1" remote_path="$2"
  ssh $SSH_OPTS "$target" "if [ -e '${remote_path}${BACKUP_SUFFIX}' ]; then rm -rf '$remote_path' && mv '${remote_path}${BACKUP_SUFFIX}' '$remote_path'; fi"
}

main() {
  [[ -d "$SOURCE_DIR" ]] || fail "Source directory missing: $SOURCE_DIR"
  local failed=0
  for target in $TARGETS; do
    remote_path="${target#*:}"
    host="${target%%:*}"
    echo "Syncing to $host:$remote_path"
    if ! sync_target "$host" "$remote_path"; then
      echo "Sync failed for $host"
      failed=1
      [[ "$ROLLBACK_ON_FAILURE" == "1" ]] && rollback_target "$host" "$remote_path"
    else
      echo "Sync succeeded for $host"
    fi
  done
  (( failed == 0 )) || exit 1
  echo "All sync operations completed successfully"
}

main
