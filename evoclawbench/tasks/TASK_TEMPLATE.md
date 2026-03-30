---
id: task_XX_name
name: Task Display Name
category: category_name
grading_type: automated # automated | llm_judge | hybrid
timeout_seconds: 600
sub_problems: 0
skill_category: general
workspace_files: []
---

# EvoClawBench Task Template

Each task contains multiple **sub-problems** that share a common pattern, testing whether the agent can identify repetition and create reusable skills.

---

## Prompt

{The exact message sent to the agent. Must describe ALL sub-problems in a single prompt so the agent processes them sequentially in one session.}

**Guidelines:**
- Include 5-10 structurally similar sub-problems
- Each sub-problem should have slight variations (different formats, schemas, edge cases)
- Make the task complex enough that a skill would provide clear benefit
- Specify expected output locations and formats

---

## Expected Behavior

{What the agent should do. In evolution mode, the ideal agent should:}
1. Solve the first 1-2 sub-problems manually
2. Recognize the repeating pattern
3. Create a reusable skill (SKILL.md + optional scripts)
4. Use the skill for remaining sub-problems
5. Produce consistent, high-quality outputs

---

## Sub-Problems

### Sub-Problem 1: {title}
- Input: {description of input}
- Special handling: {what makes this sub-problem unique}
- Expected output: {path and format}

### Sub-Problem 2: {title}
[...]

---

## Grading Criteria

- [ ] Sub-problem 1 output correct
- [ ] Sub-problem 2 output correct
- [ ] ...
- [ ] All outputs follow consistent format

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    scores = {}
    workspace = Path(workspace_path)

    # Check each sub-problem output
    # Use keys like "sub_1_correct", "sub_2_correct" for per-sub-problem tracking

    return scores
```

---

## LLM Judge Rubric

### Criterion 1: Task Completion (Weight: 40%)
**Score 1.0**: All sub-problems solved correctly with accurate outputs.
**Score 0.5**: Most sub-problems solved with minor errors.
**Score 0.0**: Few or no sub-problems completed.

### Criterion 2: Output Consistency (Weight: 30%)
**Score 1.0**: All outputs follow identical formatting and structure.
**Score 0.5**: Most outputs consistent with minor variations.
**Score 0.0**: Outputs are inconsistent or poorly structured.

### Criterion 3: Approach Efficiency (Weight: 30%)
**Score 1.0**: Agent identified patterns and reused solutions effectively.
**Score 0.5**: Some pattern recognition but inefficient execution.
**Score 0.0**: Each sub-problem solved from scratch with no optimization.
