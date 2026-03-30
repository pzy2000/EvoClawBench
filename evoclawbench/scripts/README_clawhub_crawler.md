# ClawHub Skill Crawler

`clawhub_skill_crawler.py` 是一个 API-first 的 ClawHub skill 抓取脚本。

## 功能

- 支持模式：`all` / `highlighted` / `popular`
- 输出：JSON
- 增量：基于 `state` 指纹跳过未变化记录
- 失败重试：指数退避
- 代理：支持环境变量和 `--proxy`（CLI 优先）

## 快速开始

在 `evoclawbench/scripts` 目录执行：

```bash
python clawhub_skill_crawler.py --mode all --output ./skills.json --state-file ./.clawhub_state.json
```

## 常用命令

只抓 highlighted：

```bash
python clawhub_skill_crawler.py --mode highlighted --output ./skills_highlighted.json
```

只抓 popular：

```bash
python clawhub_skill_crawler.py --mode popular --output ./skills_popular.json
```

开启代理（CLI 优先于环境变量）：

```bash
python clawhub_skill_crawler.py --mode all --proxy http://127.0.0.1:7890
```

更激进的速度参数（大页 + 短超时 + 重试）：

```bash
python clawhub_skill_crawler.py --mode all --page-size 200 --timeout 10 --retries 4
```

全量扫描（忽略常规分页上限）：

```bash
python clawhub_skill_crawler.py --mode all --full-scan --output ./skills_full.json
```

## 参数说明

- `--mode`: 抓取范围，`all|highlighted|popular`
- `--output`: 输出 JSON 文件路径，默认 `./skills.json`
- `--state-file`: 增量状态文件路径，默认 `./.clawhub_state.json`
- `--proxy`: 代理 URL，例如 `http://127.0.0.1:7890`
- `--timeout`: 请求超时（秒），默认 `15`
- `--retries`: 每个请求最大重试次数，默认 `4`
- `--backoff-base`: 退避基数（秒），默认 `0.5`
- `--page-size`: 每页条数，默认 `100`
- `--max-pages`: 分页请求安全上限，默认 `5000`
- `--full-scan`: 开启后使用超大页数上限，尽可能扫描完整站点
- `--include-suspicious`: 包含可疑 skill（默认仅抓非可疑）
- `--pretty`: 以格式化 JSON 打印统计信息

## 输出结构（示例）

```json
{
  "meta": {
    "mode": "all",
    "source_url": "https://clawhub.ai",
    "convex_url": "https://wry-manatee-359.convex.cloud",
    "fetched_at": "2026-03-24T00:00:00+00:00",
    "stats": {
      "mode": "all",
      "total_seen": 0,
      "added": 0,
      "updated": 0,
      "skipped": 0,
      "failed_requests": 0,
      "retries": 0,
      "pages": 0
    }
  },
  "items": [
    {
      "fetched_at": "2026-03-24T00:00:00+00:00",
      "source_url": "https://clawhub.ai",
      "crawl_mode": "all",
      "raw": {}
    }
  ]
}
```

其中 `raw` 保存页面可见字段对应的原始 API 数据。
