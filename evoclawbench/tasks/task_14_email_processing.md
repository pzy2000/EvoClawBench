---
id: task_14_email_processing
name: 企业邮件线程分析与回复生成
category: office_automation
grading_type: hybrid
grading_weights:
  automated: 0.70
  llm_judge: 0.30
timeout_seconds: 600
sub_problems: 5
skill_category: email_processing
workspace_files:
  - assets/email_processing/thread_01_payment_reminder.json
  - assets/email_processing/thread_02_project_confirmation.json
  - assets/email_processing/thread_03_complaint_handling.json
  - assets/email_processing/thread_04_meeting_invite.json
  - assets/email_processing/thread_05_cross_dept_collab.json
---

# 企业邮件线程分析与回复生成

分析 5 个中文商务邮件线程，为每个线程生成结构化摘要、分类标签，并草拟下一封合适的回复邮件。

---

## Prompt

`assets/email_processing/` 目录下有 5 个 JSON 格式的企业邮件线程，每个线程包含不同业务场景下的多轮往来邮件。

请逐一分析每个邮件线程，在 `outputs/` 目录下为每个线程生成一个结构化 JSON 报告。

**输入文件：**

1. `thread_01_payment_reminder.json` — 供应商催款场景（多轮沟通）
2. `thread_02_project_confirmation.json` — 项目启动会确认（含抄送方）
3. `thread_03_complaint_handling.json` — 客户投诉处理（4轮往来）
4. `thread_04_meeting_invite.json` — 内部会议邀请与回复
5. `thread_05_cross_dept_collab.json` — 跨部门资源协调（三方沟通）

**每个线程的输出文件：** `outputs/thread_XX_report.json`（XX 为 01~05）

**输出格式：**

```json
{
  "thread_id": "thread_01",
  "subject": "邮件主题",
  "category": "一级分类，如：财务催款 | 项目协作 | 客户投诉 | 内部通知 | 跨部门协调",
  "priority": "high | medium | low",
  "participants_count": 2,
  "message_count": 3,
  "summary": "2-3句话概括整个线程的核心内容和当前状态",
  "key_info": {
    "deadline": "若存在截止日期则填写，如 '2024-03-22'，否则 null",
    "amount": "若涉及金额则填写，如 '58000元'，否则 null",
    "action_required": "当前需要采取的行动，如 '等待付款确认' 或 '发送测试材料'"
  },
  "next_reply": {
    "from": "应由谁来发下一封邮件（邮件地址）",
    "to": "发给谁（邮件地址）",
    "subject": "回复的邮件主题",
    "body": "草拟的回复正文（中文，语气专业，50-150字）"
  }
}
```

**注意：**
- `priority` 判断依据：涉及金额逾期/投诉/紧急上线为 high；有明确截止日期为 medium；纯通知或已解决为 low
- `next_reply` 应基于线程当前状态推断最合适的下一步回复，而非重复已有内容
- 若线程已完结（所有事项已确认），`next_reply.body` 可写结案确认邮件

---

## Expected Behavior

1. Agent 读取第一个邮件线程（催款），解析 JSON 结构，提取参与者、日期、金额等关键信息，生成报告。
2. 处理第二个线程（项目确认）时，识别到结构相似，开始抽象通用解析逻辑。
3. 处理 2-3 个线程后，Agent 建立可复用的邮件分析技能：解析 JSON → 提取参与者/时间/关键实体 → 判断优先级 → 生成摘要 → 草拟回复。
4. 后续线程使用该技能，仅调整场景相关的判断逻辑（如投诉场景需识别用户情绪、协作场景需提取多方承诺）。
5. 最终 5 个报告格式一致，回复草稿语气专业、内容合理。

---

## Sub-Problems

### Sub-Problem 1: 催款线程（thread_01_payment_reminder.json）
- 输入：3 轮往来邮件，核心是货款逾期催收
- 特殊处理：提取合同编号、金额（58000元）、逾期天数，判断 priority=high
- Expected output: `outputs/thread_01_report.json`

### Sub-Problem 2: 项目确认线程（thread_02_project_confirmation.json）
- 输入：3 轮往来邮件，含抄送方（cc 字段）
- 特殊处理：识别 cc 参与者，提取会议时间（4月8日）、准备材料截止日期（3月29日）
- Expected output: `outputs/thread_02_report.json`

### Sub-Problem 3: 投诉处理线程（thread_03_complaint_handling.json）
- 输入：4 轮往来邮件，客户投诉 + 解决方案
- 特殊处理：识别投诉已解决状态，提取退款金额（459元+80元券），priority=high
- Expected output: `outputs/thread_03_report.json`

### Sub-Problem 4: 会议邀请线程（thread_04_meeting_invite.json）
- 输入：3 轮邮件（1邀请 + 2回复），内部群发场景
- 特殊处理：提取会议时间（3月29日14:00）、地点、议程，next_reply 为尚未回复的部门
- Expected output: `outputs/thread_04_report.json`

### Sub-Problem 5: 跨部门协调线程（thread_05_cross_dept_collab.json）
- 输入：4 轮邮件，三方参与
- 特殊处理：提取多个截止日期和各方承诺，需综合判断 action_required
- Expected output: `outputs/thread_05_report.json`

---

## Grading Criteria

- [ ] 5 个输出文件均存在
- [ ] 每个报告为有效 JSON
- [ ] 每个报告包含所有必填顶层字段
- [ ] `key_info` 中 amount 字段在涉及金额的线程（01、03）中非 null
- [ ] `key_info` 中 deadline 字段在有明确截止日期的线程（02、04、05）中非 null
- [ ] `next_reply` 包含 from、to、subject、body 四个字段
- [ ] `next_reply.body` 长度在 50-300 字之间

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    threads = [
        ("thread_01", True, False),   # (id, has_amount, deadline_expected)
        ("thread_02", False, True),
        ("thread_03", True, False),
        ("thread_04", False, True),
        ("thread_05", False, True),
    ]

    required_top_fields = {"thread_id", "subject", "category", "priority",
                           "participants_count", "message_count", "summary",
                           "key_info", "next_reply"}
    required_key_info_fields = {"deadline", "amount", "action_required"}
    required_reply_fields = {"from", "to", "subject", "body"}

    for i, (tid, has_amount, has_deadline) in enumerate(threads, start=1):
        prefix = f"sub_{i}"
        filepath = workspace / "outputs" / f"{tid}_report.json"

        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for k in ["valid_json", "fields", "key_info", "next_reply", "reply_body_len"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for k in ["valid_json", "fields", "key_info", "next_reply", "reply_body_len"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        if not isinstance(data, dict):
            for k in ["fields", "key_info", "next_reply", "reply_body_len"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        # Required top-level fields
        scores[f"{prefix}_fields"] = 1.0 if required_top_fields.issubset(data.keys()) else 0.0

        # key_info structure
        ki = data.get("key_info", {})
        ki_ok = (
            isinstance(ki, dict)
            and required_key_info_fields.issubset(ki.keys())
            and (ki.get("amount") is not None if has_amount else True)
            and (ki.get("deadline") is not None if has_deadline else True)
        )
        scores[f"{prefix}_key_info"] = 1.0 if ki_ok else 0.0

        # next_reply structure
        nr = data.get("next_reply", {})
        nr_ok = isinstance(nr, dict) and required_reply_fields.issubset(nr.keys())
        scores[f"{prefix}_next_reply"] = 1.0 if nr_ok else 0.0

        # reply body length
        body = nr.get("body", "") if isinstance(nr, dict) else ""
        body_len = len(body)
        scores[f"{prefix}_reply_body_len"] = 1.0 if 50 <= body_len <= 500 else 0.0

    return scores
```

---

## LLM Judge Rubric

您正在评估一个企业邮件分析任务。Agent 读取了 5 个中文商务邮件线程，并在 `outputs/` 目录下生成了对应的 JSON 报告。

请对以下两个维度打分（0.0 到 1.0）：

**1. summary_quality（摘要质量，占 50%）**
对每个线程的 `summary` 字段评估：是否准确概括了邮件核心内容和当前状态？好的摘要应指明沟通目的、当前进展、未解决事项（如有）。0.0 = 内容缺失/通用/与实际不符；1.0 = 5个摘要均准确、具体、反映线程真实状态。返回 5 个线程的平均分。

**2. next_reply_quality（回复草稿质量，占 50%）**
对每个线程的 `next_reply.body` 字段评估：回复内容是否符合商务邮件规范、语气是否恰当、内容是否与线程当前状态一致（不重复已沟通内容、不遗漏必要跟进）？0.0 = 回复内容不当或与场景不符；1.0 = 5封回复均专业、得体、内容准确。返回 5 个线程的平均分。
