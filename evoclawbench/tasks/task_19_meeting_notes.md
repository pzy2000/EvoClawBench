---
id: task_19_meeting_notes
name: 会议纪要结构化提取
category: office_daily
grading_type: hybrid
grading_weights:
  automated: 0.65
  llm_judge: 0.35
timeout_seconds: 600
sub_problems: 5
skill_category: document_structuring
workspace_files:
  - assets/meeting_notes/meeting_01_product_review.txt
  - assets/meeting_notes/meeting_02_project_retrospective.txt
  - assets/meeting_notes/meeting_03_sales_weekly.txt
  - assets/meeting_notes/meeting_04_tech_architecture.txt
  - assets/meeting_notes/meeting_05_hr_interview.txt
---

# 会议纪要结构化提取

读取 5 份非结构化中文会议记录文本，从中提取议题、决策、行动项、负责人和截止日期，输出为标准化 JSON 格式。

---

## Prompt

`assets/meeting_notes/` 目录下有 5 份中文会议记录文本文件，每份来自不同行业场景。请逐一分析，提取结构化信息，输出到 `outputs/` 目录。

**输入文件：**

1. `meeting_01_product_review.txt` — 产品评审会（功能讨论、时间节点）
2. `meeting_02_project_retrospective.txt` — 项目复盘会（问题分析、改进措施）
3. `meeting_03_sales_weekly.txt` — 销售周会（业绩数据、客户跟进）
4. `meeting_04_tech_architecture.txt` — 技术架构讨论（技术选型、方案决策）
5. `meeting_05_hr_interview.txt` — 面试评审会（候选人评估、后续安排）

**每份会议记录的输出：** `outputs/meeting_0X_minutes.json`（X 为 1~5）

**输出格式：**

```json
{
  "meeting_id": "meeting_01",
  "title": "会议标题",
  "date": "YYYY-MM-DD",
  "duration_minutes": 数值（若无法确定则为 null）,
  "location": "会议地点（若有）",
  "participants": [
    {"name": "姓名", "role": "职务/角色"}
  ],
  "agenda_items": [
    {
      "topic": "议题名称",
      "summary": "1-2句话描述讨论内容和结论"
    }
  ],
  "decisions": [
    {
      "description": "决策内容",
      "rationale": "决策原因（若有）"
    }
  ],
  "action_items": [
    {
      "description": "行动项内容",
      "owner": "负责人姓名",
      "due_date": "YYYY-MM-DD（若有，否则 null）",
      "priority": "high | medium | low"
    }
  ],
  "next_meeting": "下次会议时间或说明（若有，否则 null）",
  "recorder": "记录人姓名（若有）"
}
```

**提取规则：**
- `action_items` 应提取所有明确提到"负责人+任务"的条目，尤其是有截止日期的
- `priority` 判断：涉及上线/客户/安全/故障为 high；有明确截止日期为 medium；其他为 low
- 日期统一转为 `YYYY-MM-DD` 格式；年份若未提及则假定为 2024 年
- `participants` 应包含所有出现在参会者名单中的人

---

## Expected Behavior

1. Agent 读取第一份会议记录（产品评审），识别参与者、议题、行动项和截止日期。
2. 处理第二份（项目复盘）时，结构相似，Agent 开始复用解析逻辑。
3. 3份处理后，Agent 建立会议纪要结构化技能：提取参与者 → 识别议题 → 定位行动项（"谁+什么+什么时间"） → 提取决策 → 输出 JSON。
4. 使用技能处理后续会议记录，适配不同写法（有些用"行动项汇总"表格，有些混在正文中）。
5. 所有输出格式一致，action_items 完整不遗漏。

---

## Sub-Problems

### Sub-Problem 1: 产品评审会（meeting_01_product_review.txt）
- 行动项：≥5个（李娜3/22方案、陈磊3/25水印、赵敏3/27测试、刘洋3/29接口、陈磊协调运维等）
- 特殊处理：议题按功能模块划分；注意"下次会议4月3日"
- Expected output: `outputs/meeting_01_minutes.json`

### Sub-Problem 2: 项目复盘会（meeting_02_project_retrospective.txt）
- 行动项：≥5个（孙磊4/5流程、马超+吴强4/10压测规范、马超故障报告3/28、吴强SOP4/15等）
- 特殊处理：包含多个项目的复盘；每个项目独立作为 agenda_item
- Expected output: `outputs/meeting_02_minutes.json`

### Sub-Problem 3: 销售周会（meeting_03_sales_weekly.txt）
- 行动项：≥4个（钱丽3/25分析报告、徐丹安排技术顾问、各区Q1冲刺名单3/25、CRM录入3/29等）
- 特殊处理：包含数据汇报内容；next_meeting 为3月28日（日期变更）
- Expected output: `outputs/meeting_03_minutes.json`

### Sub-Problem 4: 技术架构讨论（meeting_04_tech_architecture.txt）
- 行动项：≥6个（文末有"行动项汇总"清单，应与正文中的任务对应）
- 特殊处理：有分歧记录，需在 decisions 中体现最终决策
- Expected output: `outputs/meeting_04_minutes.json`

### Sub-Problem 5: 面试评审会（meeting_05_hr_interview.txt）
- 行动项：≥3个（周静约候选人3/25、周静探薪资、启动背调3/29）
- 特殊处理：较短会议；"其他在面候选人"信息纳入备注或 agenda
- Expected output: `outputs/meeting_05_minutes.json`

---

## Grading Criteria

- [ ] 5 个输出文件均存在
- [ ] 每个文件为有效 JSON
- [ ] 每个文件包含所有必填顶层字段
- [ ] 每个文件的 `action_items` 数组非空（≥ 1 条）
- [ ] 每个文件的 `participants` 数组非空（≥ 2 人）
- [ ] meeting_01 的 action_items 数量 ≥ 4
- [ ] meeting_04 的 action_items 数量 ≥ 5
- [ ] 所有 `action_items` 条目包含 `owner` 和 `description` 字段

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    meetings = [
        ("meeting_01", 4, 3),   # (id, min_action_items, min_participants)
        ("meeting_02", 4, 5),
        ("meeting_03", 3, 4),
        ("meeting_04", 5, 5),
        ("meeting_05", 2, 3),
    ]

    required_fields = {"meeting_id", "title", "date", "participants",
                       "agenda_items", "decisions", "action_items"}
    action_required = {"description", "owner"}

    for i, (mid, min_actions, min_participants) in enumerate(meetings, start=1):
        prefix = f"sub_{i}"
        filepath = workspace / "outputs" / f"{mid}_minutes.json"

        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for k in ["valid_json", "fields", "action_items", "action_structure",
                      "participants", "action_count"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for k in ["valid_json", "fields", "action_items", "action_structure",
                      "participants", "action_count"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        if not isinstance(data, dict):
            for k in ["fields", "action_items", "action_structure", "participants", "action_count"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        scores[f"{prefix}_fields"] = 1.0 if required_fields.issubset(data.keys()) else 0.0

        actions = data.get("action_items", [])
        scores[f"{prefix}_action_items"] = 1.0 if (
            isinstance(actions, list) and len(actions) > 0
        ) else 0.0
        scores[f"{prefix}_action_count"] = 1.0 if (
            isinstance(actions, list) and len(actions) >= min_actions
        ) else 0.0

        action_struct_ok = (
            isinstance(actions, list)
            and all(
                isinstance(a, dict) and action_required.issubset(a.keys())
                for a in actions
            )
        ) if actions else False
        scores[f"{prefix}_action_structure"] = 1.0 if action_struct_ok else 0.0

        participants = data.get("participants", [])
        scores[f"{prefix}_participants"] = 1.0 if (
            isinstance(participants, list) and len(participants) >= min_participants
        ) else 0.0

    return scores
```

---

## LLM Judge Rubric

您正在评估会议纪要结构化提取任务。Agent 读取了 5 份中文会议记录文本，并生成了 JSON 格式的结构化纪要。

请对以下两个维度打分（0.0 到 1.0）：

**1. action_items_completeness（行动项完整性，占 60%）**
对每份会议记录，比对原文中明确提到的"谁负责+什么任务+何时完成"条目，是否都被提取到了 `action_items` 中？遗漏重要行动项（有明确负责人和截止日期的）扣分。完全无遗漏=1.0，遗漏超过一半=0.0。返回 5 份会议的平均分。

**2. date_accuracy（日期提取准确性，占 40%）**
行动项中 `due_date` 字段的准确性：原文中标注了截止日期的行动项，`due_date` 是否正确填写且格式为 YYYY-MM-DD？未提截止日期的行动项，`due_date` 是否为 null？完全正确=1.0，有较多错误=0.0。返回 5 份会议的平均分。
