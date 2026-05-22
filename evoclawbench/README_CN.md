# EvoClawBench

**用于评测通用代理任务表现的基准：对比是否使用可复用技能时的差异。**

EvoClawBench 经由 OpenClaw 或 nanobot 运行同一套任务，并对比三种执行策略：

- **baseline**：直接完成任务；禁止创建技能或修改已有技能。
- **preskill**：先生成任务相关技能，再在全新工作区中用这些技能执行任务；执行阶段不得再改技能。
- **postskill**：先在无技能下一次执行；从首轮运行摘要可复用技能；再在全新工作区用这些技能重复同一任务。

默认 `--mode all` 会跑满三种策略，并报告仅执行阶段与端到端两个阶段的表现。

## 决策纪要

以下为设计评审中选定的 v1 基准约定，有意放在靠前的位置，用于界定如何解读结果。

| 问题 | 选定方案 | 影响 |
|------|----------|------|
| 旧的 `baseline/evolution/bench/both` 语义由什么替代？ | 直接改为 `baseline`、`preskill`、`postskill` 与 `all`；不提供旧版 CLI 模式兼容。 | 新结果 JSON 使用 `baseline_results`、`preskill_results`、`postskill_results` 与 `metrics`。 |
| 默认 CLI 模式是什么？ | `--mode all`。 | 默认一次运行按顺序对比三种策略：baseline，然后 preskill，然后 postskill。 |
| 谁来创建或摘要技能？ | 与被测的是同一运行时与同一模型。 | 技能生成属于代理表现的一部分，不是外部裁判或独立摘要步骤。 |
| v1 中 `postskill` 重跑什么？ | 同一任务与同一套 fixture。 | v1 不引入「相似任务变体」。 |
| 性能指什么？ | 任务得分、token 用量、成本与耗时。 | 仅执行与端到端两种范围都会出指标。 |
| baseline 或执行阶段能否改技能？ | 不能。baseline 与技能复用执行阶段均不得创建、编辑或删除技能。 | 执行前后对技能文件做哈希；若有变更则标记 `skill_mutation_violation=true`。 |
| `postskill` 如何从首轮学习？ | 首轮工作区会写入 `.evoclawbench/first_run_context.json`，内含任务、评分、输出与对话摘要。 | 摘要阶段基于首轮证据，不再重跑任务。 |
| 任务与评分器应改多少？ | 除非编排需要，否则保留现有任务、资源与评分行为。 | 本次基准变更聚焦编排、提示词、技能流、结果结构、指标与文档。 |

## 快速开始

```bash
cd evoclawbench
uv sync --extra dev

# 跑完整三种策略对比
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot

# 在 OpenClaw 上跑子集任务
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime openclaw \
  --suite task_01_batch_data_transform,task_02_log_analysis

# 只跑某一种模式
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --mode preskill

# 每个任务多次运行
uv run scripts/benchmark.py --model anthropic/claude-sonnet-4 --runtime nanobot --runs 3
```

## 模式

| 模式 | 阶段 | 技能行为 |
|------|------|----------|
| `baseline` | 执行 -> 评分 | 不创建技能、不改动技能 |
| `preskill` | 技能生成 -> 执行 -> 评分 | 生成阶段会种子化 `skills/skill-creator`；执行阶段仅加载已生成技能 |
| `postskill` | 首轮执行 -> 评分 -> 技能摘要 -> 第二轮执行 -> 评分 | 摘要依赖 `.evoclawbench/first_run_context.json`；第二轮执行加载摘要后的技能 |
| `all` | baseline + preskill + postskill | 默认完整对比 |

技能编写阶段同样由被测的运行时与模型完成。复用执行阶段会在执行前后对技能文件哈希；若在执行期间增删改了技能，结果会标记 `skill_mutation_violation=true`。

## 支持的运行时

| 运行时 | CLI |
|--------|-----|
| **OpenClaw** | `openclaw agent --message` |
| **nanobot** | `nanobot run --message` |

两者均使用 `SKILL.md` 格式。编写技能需要 monorepo 中紧邻 `evoclawbench/` 的 `skills/skill-creator/` 目录。

## 指标

输出 JSON 包含：

- `baseline_results`
- `preskill_results`
- `postskill_results`
- `metrics`

`metrics.execution_only` 只对比任务执行阶段：

- baseline 执行
- preskill 在技能生成之后的执行
- postskill 在摘要之后的第二轮执行

`metrics.end_to_end` 计入整条流水线的总成本：

- baseline 单次执行
- preskill：技能生成 + 执行
- postskill：首轮执行 + 技能摘要 + 第二轮执行

两种范围都会报告平均分、token、成本与时间，以及相对 baseline 的效率。postskill 另报告首轮得分、第二轮得分，以及第二轮相对首轮的提升。preskill 与 postskill 会分别报告新建技能数量与启发式技能质量。

## 任务

任务定义在 `tasks/task_*.md`。每个任务包含提示、工作区资产、评分标准，以及通常 5～10 道结构相似的子问题。当前类别包括数据转换、日志分析、API 脚手架、测试生成、配置迁移、安全审查、文档抽取、Excel 与报表、网页抓取、邮件、发票与会议记录处理、Shell 自动化、CI 生成、环境配置以及指标异常检测等。

## 结果

默认写入 `results/`：

```json
{
  "benchmark": "evoclawbench",
  "model": "anthropic/claude-sonnet-4",
  "runtime": "nanobot",
  "mode": "all",
  "baseline_results": {},
  "preskill_results": {},
  "postskill_results": {},
  "metrics": {
    "execution_only": {},
    "end_to_end": {},
    "postskill": {},
    "created_skills": {},
    "skill_quality": {},
    "skill_mutation_violations": {}
  }
}
```

每次运行还会写入 `.trajectories.json`，包含对话轨迹、工作区摘要、评分细节与错误，便于调试。

## 项目结构

```text
evoclawbench/
├── scripts/
│   ├── benchmark.py       # 主编排入口
│   ├── lib_agent.py       # 运行时适配、提示词、工作区与技能流程
│   ├── lib_grading.py     # 自动化 / LLM / 混合评分
│   ├── lib_metrics.py     # 三模式指标与遗留辅助函数
│   └── lib_tasks.py       # 任务加载
├── tasks/                 # Markdown 任务定义
├── assets/                # 任务 fixture
├── results/               # 输出产物
├── workspaces/            # 每次运行的工作目录
└── pyproject.toml
```

## 开发

```bash
uv run pytest tests/ -v
uv run ruff check scripts/ tests/
uv run black scripts/ tests/
```
