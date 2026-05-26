---
id: task_17_invoice_processing
name: 企业发票费用处理与汇总
category: office_daily
grading_type: hybrid
grading_weights:
  automated: 0.90
  llm_judge: 0.10
timeout_seconds: 600
sub_problems: 5
skill_category: invoice_parsing
workspace_files:
  - assets/invoice_processing/invoice_01.json
  - assets/invoice_processing/invoice_02.xml
  - assets/invoice_processing/invoice_03.csv
  - assets/invoice_processing/invoice_04.tsv
  - assets/invoice_processing/invoice_05.txt
---

# 企业发票费用处理与汇总

解析 5 种不同格式的企业发票/收据文件，将其标准化为统一的 JSON 结构，并生成一份费用汇总报表。

---

## Prompt

`assets/invoice_processing/` 目录下有 5 张来自不同系统导出的发票或收据文件，格式各异。请解析每张发票，将其转化为标准化 JSON，并最终生成一份汇总报表。

**输入文件：**

1. `invoice_01.json` — 增值税专用发票（JSON格式，含多条明细）
2. `invoice_02.xml` — 餐饮普通收据（XML格式）
3. `invoice_03.csv` — 商务用车发票（CSV格式，多行）
4. `invoice_04.tsv` — 云服务费用发票（TSV 键值对格式，竖排）
5. `invoice_05.txt` — 印刷费专用发票（纯文本 key=value 格式）

**每张发票的输出：** `outputs/invoice_0X_parsed.json`（X 为 1~5）

**标准化输出格式：**

```json
{
  "invoice_id": "发票号码（字符串）",
  "invoice_type": "发票类型，如 增值税专用发票 | 增值税普通发票",
  "issue_date": "YYYY-MM-DD",
  "vendor": {
    "name": "供应商/销售方名称",
    "tax_id": "纳税人识别号（若有）"
  },
  "customer": {
    "name": "购买方/客户名称",
    "tax_id": "纳税人识别号（若有）"
  },
  "items": [
    {
      "description": "货物/服务名称",
      "quantity": 数值,
      "unit_price": 数值,
      "amount": 数值,
      "tax_rate": "税率字符串，如 13%",
      "tax_amount": 数值
    }
  ],
  "subtotal": 不含税总金额（数值）,
  "total_tax": 税额合计（数值）,
  "grand_total": 价税合计（数值）,
  "category": "报销类别，如 办公设备 | 差旅费 | 餐饮招待 | IT费用 | 市场推广费",
  "notes": "备注信息（若有，否则为 null）"
}
```

**另外，** 所有发票解析完成后，生成 `outputs/expense_summary.json`：

```json
{
  "total_invoices": 5,
  "total_amount": 所有发票 grand_total 之和,
  "total_tax": 所有发票 total_tax 之和,
  "by_category": {
    "办公设备": {"count": 1, "amount": 50612.70},
    "差旅费": {"count": 1, "amount": 1569.60},
    ...
  },
  "by_vendor": [
    {"vendor": "供应商名", "invoice_count": 1, "total_amount": 50612.70}
  ],
  "invoices": ["invoice_01", "invoice_02", "invoice_03", "invoice_04", "invoice_05"]
}
```

**注意：**
- `invoice_03.csv` 含多行（同一供应商的多条记录），应合并为一张发票（多个 items），grand_total 为各行价税合计之和
- 日期统一转换为 `YYYY-MM-DD` 格式
- 数值字段必须为数字类型（不含货币符号和千位分隔符）

---

## Expected Behavior

1. Agent 解析第一个文件（JSON 格式发票），直接读取并映射字段。
2. 解析第二个文件（XML）时，需要用 XML 解析库提取节点。
3. 处理 2-3 个文件后，Agent 建立可复用的发票解析技能：检测格式 → 提取字段 → 映射到标准 schema → 输出 JSON。
4. 后续文件（CSV、TSV、key=value）使用技能并添加对应格式解析器。
5. 最终生成汇总报表，正确聚合金额和分类。

---

## Sub-Problems

### Sub-Problem 1: JSON 发票（invoice_01.json）
- 输入：结构化 JSON，含嵌套对象和明细数组
- 特殊处理：字段为中文键名；items 数组已存在；grand_total = 价税合计小写
- Expected output: `outputs/invoice_01_parsed.json`

### Sub-Problem 2: XML 收据（invoice_02.xml）
- 输入：XML 格式，含 `<Items>` 子节点
- 特殊处理：需 XML 解析（ElementTree/lxml/BeautifulSoup）；报销类别从 `<Note>` 推断
- Expected output: `outputs/invoice_02_parsed.json`

### Sub-Problem 3: CSV 发票（invoice_03.csv）
- 输入：CSV 多行，同一供应商多条明细
- 特殊处理：多行合并为单张发票；grand_total 为各行 `价税合计` 之和（414.20+850.20+305.20=1569.60）
- Expected output: `outputs/invoice_03_parsed.json`

### Sub-Problem 4: TSV 竖排格式（invoice_04.tsv）
- 输入：每行为 `字段\t值` 的竖排键值对
- 特殊处理：需按行解析；日期 `2024年03月19日` 转为 `2024-03-19`；items 为单条
- Expected output: `outputs/invoice_04_parsed.json`

### Sub-Problem 5: key=value 文本（invoice_05.txt）
- 输入：`key=value` 纯文本，日期格式为 `YYYYMMDD`
- 特殊处理：日期 `20240320` 转为 `2024-03-20`；items 为单条；notes 含多段信息
- Expected output: `outputs/invoice_05_parsed.json`

---

## Grading Criteria

- [ ] 6 个输出文件均存在（5个 parsed + 1个 summary）
- [ ] 每个 parsed 文件为有效 JSON
- [ ] 每个 parsed 文件包含所有必填顶层字段
- [ ] 所有 `grand_total` 字段为数值类型（非字符串）
- [ ] `invoice_01` 的 grand_total ≈ 50612.70（误差 < 0.1）
- [ ] `invoice_03` 的 grand_total ≈ 1569.60（误差 < 0.1，多行合并）
- [ ] `expense_summary.json` 的 `total_invoices` == 5
- [ ] `expense_summary.json` 的 `by_category` 为非空对象

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    expected = [
        ("invoice_01", 50612.70),
        ("invoice_02", 1727.80),
        ("invoice_03", 1569.60),
        ("invoice_04", 3816.00),
        ("invoice_05", 15820.00),
    ]

    required_fields = {"invoice_id", "invoice_type", "issue_date", "vendor",
                       "customer", "items", "subtotal", "total_tax", "grand_total", "category"}

    for i, (inv_id, expected_total) in enumerate(expected, start=1):
        prefix = f"sub_{i}"
        filepath = workspace / "outputs" / f"{inv_id}_parsed.json"

        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for k in ["valid_json", "fields", "grand_total_type", "grand_total_value"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        try:
            with open(filepath) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for k in ["valid_json", "fields", "grand_total_type", "grand_total_value"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        if not isinstance(data, dict):
            for k in ["fields", "grand_total_type", "grand_total_value"]:
                scores[f"{prefix}_{k}"] = 0.0
            continue

        scores[f"{prefix}_fields"] = 1.0 if required_fields.issubset(data.keys()) else 0.0

        gt = data.get("grand_total")
        scores[f"{prefix}_grand_total_type"] = 1.0 if isinstance(gt, (int, float)) else 0.0
        if isinstance(gt, (int, float)):
            scores[f"{prefix}_grand_total_value"] = 1.0 if abs(gt - expected_total) < 0.5 else 0.0
        else:
            scores[f"{prefix}_grand_total_value"] = 0.0

    # Check expense_summary.json
    summary_path = workspace / "outputs" / "expense_summary.json"
    scores["summary_exists"] = 1.0 if summary_path.is_file() else 0.0
    if summary_path.is_file():
        try:
            with open(summary_path) as f:
                summary = json.load(f)
            scores["summary_valid_json"] = 1.0
            scores["summary_total_invoices"] = 1.0 if summary.get("total_invoices") == 5 else 0.0
            scores["summary_by_category"] = 1.0 if (
                isinstance(summary.get("by_category"), dict)
                and len(summary.get("by_category", {})) > 0
            ) else 0.0
            total = summary.get("total_amount", 0)
            expected_grand = sum(e for _, e in expected)
            scores["summary_total_amount"] = 1.0 if (
                isinstance(total, (int, float)) and abs(total - expected_grand) < 1.0
            ) else 0.0
        except Exception:
            for k in ["summary_valid_json", "summary_total_invoices", "summary_by_category", "summary_total_amount"]:
                scores[k] = 0.0
    else:
        for k in ["summary_valid_json", "summary_total_invoices", "summary_by_category", "summary_total_amount"]:
            scores[k] = 0.0

    return scores
```

---

## LLM Judge Rubric

您正在评估企业发票解析任务。Agent 读取了 5 张不同格式的发票文件，并生成了标准化 JSON 输出。

请对以下维度打分（0.0 到 1.0）：

**category_accuracy（分类准确性）**：对 5 张发票的 `category` 字段，是否正确识别报销类别？（invoice_01=办公设备，invoice_02=餐饮招待/业务招待，invoice_03=差旅费，invoice_04=IT费用/信息技术费，invoice_05=市场推广费/宣传费）。完全正确=1.0，部分正确按比例计分，全错=0.0。
