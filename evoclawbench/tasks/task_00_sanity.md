---
id: task_00_sanity
name: Sanity Check
category: sanity
grading_type: automated
timeout_seconds: 60
sub_problems: 0
skill_category: none
workspace_files: []
---

## Prompt

Respond with "EvoClawBench ready" to confirm you are operational.

## Expected Behavior

The agent should respond with text containing "EvoClawBench ready" or similar confirmation.

## Grading Criteria

- [ ] Agent responded with confirmation text

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    for event in transcript:
        if event.get("type") != "message":
            continue
        msg = event.get("message", {})
        if msg.get("role") == "assistant":
            content = msg.get("content", [])
            if isinstance(content, str):
                text = content.lower()
            elif isinstance(content, list):
                text = " ".join(
                    item.get("text", "") for item in content if isinstance(item, dict)
                ).lower()
            else:
                continue
            if "ready" in text or "operational" in text or "evoclawbench" in text:
                return {"responded": 1.0}
    return {"responded": 0.0}
```
