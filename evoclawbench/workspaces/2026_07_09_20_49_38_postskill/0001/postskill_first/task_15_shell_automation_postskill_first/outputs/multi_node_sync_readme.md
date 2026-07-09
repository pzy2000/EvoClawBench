# Multi-Node Config File Sync

## Purpose
Synchronizes `/etc/myapp/config/` to multiple remote servers over SSH/rsync, reloads `myapp` on each host, and reports failures for manual rollback.

## Usage
```bash
./outputs/multi_node_sync.sh
./outputs/multi_node_sync.sh --dry-run
```

## Required environment variables
None.

## Notes
- Uses SSH key `/home/deploy/.ssh/id_rsa`.
- Excludes `*.bak`, `*.tmp`, and `secrets.conf`.

## Example output
```text
server             sync_status  reload_status duration_s
web01.internal     ok           ok           4
web02.internal     ok           fail         5
Manual rollback needed for: web02.internal
```