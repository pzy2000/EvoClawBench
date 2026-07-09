# Multi-Server Config Sync via rsync/SSH

## Purpose
Synchronizes a configuration directory from one source node to multiple remote nodes using `rsync` over SSH, with a simple rollback mechanism if a sync fails.

## Usage
```bash
bash outputs/multi_node_sync.sh
```

## Required env vars
- `SOURCE_DIR` (default: `/etc/myapp`)
- `TARGETS` (default: `server1:/etc/myapp server2:/etc/myapp`)
- `SSH_OPTS` (default: `-o BatchMode=yes`)
- `RSYNC_OPTS` (default: `-aH --delete --numeric-ids`)
- `BACKUP_SUFFIX` (default: `.backup`)
- `ROLLBACK_ON_FAILURE` (default: `1`)

## Example output
```text
Syncing to server1:/etc/myapp
Sync succeeded for server1
Syncing to server2:/etc/myapp
Sync succeeded for server2
All sync operations completed successfully
```
