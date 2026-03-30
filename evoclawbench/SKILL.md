---
name: evoclawbench
description: EvoClawBench - Benchmark for evaluating LLM agent skill evolution capabilities. Tests whether agents can identify repeating patterns, create reusable skills, and effectively reuse them across sub-problems.
---

# EvoClawBench

An open-source benchmark for evaluating LLM agents' ability to create and reuse skills (auto-evolution) at runtime.

## Quick Start

```bash
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode both
```

## Key Concepts

- **Baseline mode**: Agent is forbidden from creating skills
- **Evolution mode**: Agent is encouraged to create reusable skills
- **fail2pass ratio**: Measures the benefit of skill creation
