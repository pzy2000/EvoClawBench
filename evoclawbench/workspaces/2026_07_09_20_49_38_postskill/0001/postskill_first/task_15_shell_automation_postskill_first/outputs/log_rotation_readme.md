# Log Rotation and Cleanup

## Purpose
Rotates large `.log` files in `/var/log/myapp`, compresses older logs, and removes expired logs while avoiding files that are currently open.

## Usage
```bash
./outputs/log_rotation.sh
```

## Required environment variables
None.

## Notes
- Creates `/var/log/myapp` if it does not exist.
- Uses `lsof` to avoid touching files currently being written.

## Example output
```text
filename                                      size       age      action_taken        
app.log                                       104857600  4        rotated -> app.log.20240320_023000
```