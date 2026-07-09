# task_02_log_rotation.sh

Purpose: Rotate oversized application log files, keep a small recent set uncompressed, compress older rotations with `gzip`, and delete expired compressed logs while avoiding files that are still open.

## Usage

```bash
chmod +x outputs/task_02_log_rotation.sh
./outputs/task_02_log_rotation.sh
```

## Required/configurable environment variables

- `LOG_DIR` — log directory. Default: `/var/log/myapp`
- `ROTATE_SIZE_MB` — rotate files at or above this size. Default: `100`
- `COMPRESS_AFTER_DAYS` — compress rotated files at or above this age. Default: `3`
- `DELETE_AFTER_DAYS` — delete compressed files older than this age. Default: `30`
- `LOG_PATTERN` — base logs to manage. Default: `*.log`
- `COMPRESSED_EXTENSION` — compressed suffix. Default: `.gz`
- `KEEP_LAST_N_UNCOMPRESSED` — newest rotated logs to keep plain. Default: `5`

## Behavior notes

- Creates `LOG_DIR` if missing; exits gracefully if creation fails.
- Checks `lsof` before rotating active files.
- Uses `find ... -mtime` to delete expired compressed logs.
- Safe to re-run: active logs are skipped, rotated logs are only compressed or deleted when eligible.
- Prints a summary table to stdout.

## Example output

```text
filename                                           size_bytes   age_d    action_taken
--------                                           ----------   -----    ------------
/var/log/myapp/app.log                             154009600    0        rotated_to_app.log.20260710_010101
/var/log/myapp/app.log.20260701_010101.gz          154009600    9        compressed
/var/log/myapp/app.log.20260601_010101.gz          812345       39       deleted
```
