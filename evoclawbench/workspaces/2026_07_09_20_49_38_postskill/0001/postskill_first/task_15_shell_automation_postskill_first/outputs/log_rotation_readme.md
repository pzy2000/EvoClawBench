# Log Rotation and Cleanup

## Purpose
Rotates large log files in `/var/log/myapp`, compresses older logs, and removes compressed logs older than 30 days.

## Usage
```bash
bash outputs/log_rotation.sh
```

## Required env vars
- `LOG_DIR` (default: `/var/log/myapp`)
- `ROTATE_SIZE_MB` (default: `100`)
- `COMPRESS_AFTER_DAYS` (default: `3`)
- `DELETE_AFTER_DAYS` (default: `30`)
- `LOG_PATTERN` (default: `*.log`)
- `COMPRESSED_EXTENSION` (default: `.gz`)
- `KEEP_LAST_N_UNCOMPRESSED` (default: `5`)

## Example output
```text
filename                                 size       age      action_taken   
app.log                                  120.4MB    1d       rotated+compressed
old.log                                  12.1MB     5d       compressed
archive.log.gz                           3.2MB      40d      deleted
```
