# task_05_multi_node_sync.sh

Purpose: Synchronize a local configuration directory to multiple remote servers with `rsync` over `ssh`, run per-host pre-flight checks, reload the remote service, continue past individual failures, and report which hosts need manual rollback.

## Usage

```bash
chmod +x outputs/task_05_multi_node_sync.sh
./outputs/task_05_multi_node_sync.sh
./outputs/task_05_multi_node_sync.sh --dry-run
```

## Required/configurable environment variables

- `LOCAL_CONFIG_DIR` — local config directory. Default: `/etc/myapp/config/`
- `REMOTE_PATH` — remote destination path. Default: `/etc/myapp/config/`
- `SSH_USER` — remote SSH user. Default: `deploy`
- `SSH_KEY` — SSH private key path. Default: `/home/deploy/.ssh/id_rsa`
- `SSH_TIMEOUT_SECONDS` — SSH pre-flight timeout. Default: `5`
- `REMOTE_RELOAD_CMD` — remote reload command. Default: `sudo systemctl reload myapp`
- `REMOTE_SERVER_1` — default: `web01.internal:22`
- `REMOTE_SERVER_2` — default: `web02.internal:22`
- `REMOTE_SERVER_3` — default: `web03.internal:22`

## Behavior notes

- If the first argument is `--dry-run`, the script prints the planned `ssh` and `rsync` actions without executing changes.
- Uses `rsync` with `--delete`, `--times`, and `--perms`.
- Excludes `*.bak`, `*.tmp`, and `secrets.conf`.
- Continues processing other servers even if one host fails.
- Exits `0` only if every server syncs and reloads successfully.

## Example output

```text
server                 sync_status        reload_status    duration_s
------                 -----------        -------------    ----------
web01.internal:22      ok                 ok               4
web02.internal:22      rsync_failed       skipped          2
web03.internal:22      ok                 failed           5

Manual rollback required on these servers: web03.internal:22
```
