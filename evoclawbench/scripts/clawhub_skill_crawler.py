#!/usr/bin/env python3
"""
ClawHub skill crawler (API-first).

Fetches skills from ClawHub's public Convex API with support for:
- mode: all / highlighted / popular
- JSON output
- retries with exponential backoff
- incremental state (skip unchanged records)
- proxy from env and/or --proxy (CLI has priority)
"""

# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, request

CONVEX_URL = "https://wry-manatee-359.convex.cloud"
QUERY_URL = f"{CONVEX_URL}/api/query"
SITE_URL = "https://clawhub.ai"
DEFAULT_PAGE_SIZE = 100


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dumps_compact(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def fingerprint_record(record: Dict[str, Any]) -> str:
    payload = json_dumps_compact(record).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def dump_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def setup_opener(cli_proxy: Optional[str]) -> request.OpenerDirector:
    """
    Build urllib opener.
    - If --proxy is provided, force both HTTP/HTTPS to that proxy (CLI priority).
    - Else, use environment proxy settings.
    """
    if cli_proxy:
        proxies = {"http": cli_proxy, "https": cli_proxy}
    else:
        proxies = request.getproxies()
    handler = request.ProxyHandler(proxies)
    return request.build_opener(handler)


@dataclass
class CrawlerStats:
    mode: str
    total_seen: int = 0
    added: int = 0
    updated: int = 0
    skipped: int = 0
    failed_requests: int = 0
    retries: int = 0
    pages: int = 0


class ClawHubCrawler:
    def __init__(
        self,
        *,
        mode: str,
        timeout: float,
        retries: int,
        backoff_base: float,
        output_path: Path,
        state_path: Path,
        proxy: Optional[str],
        page_size: int,
        non_suspicious_only: bool,
        max_pages: int,
    ) -> None:
        self.mode = mode
        self.timeout = timeout
        self.max_retries = retries
        self.backoff_base = backoff_base
        self.output_path = output_path
        self.state_path = state_path
        self.page_size = max(1, page_size)
        self.non_suspicious_only = non_suspicious_only
        self.max_pages = max(1, max_pages)
        self.opener = setup_opener(proxy)
        self.stats = CrawlerStats(mode=mode)

        self.state = load_json_file(
            state_path, default={"items": {}, "updated_at": None, "meta": {}}
        )
        if not isinstance(self.state, dict):
            self.state = {"items": {}, "updated_at": None, "meta": {}}
        self.state.setdefault("items", {})
        if not isinstance(self.state["items"], dict):
            self.state["items"] = {}

    def _post_query(self, path: str, args: Dict[str, Any]) -> Any:
        payload = {"path": path, "format": "convex_encoded_json", "args": [args]}
        body = json_dumps_compact(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "clawhub-skill-crawler/1.0",
        }

        for attempt in range(self.max_retries + 1):
            try:
                req = request.Request(QUERY_URL, data=body, headers=headers, method="POST")
                with self.opener.open(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    if data.get("status") != "success":
                        raise RuntimeError(f"Convex non-success status: {data}")
                    return data.get("value")
            except (
                error.URLError,
                error.HTTPError,
                TimeoutError,
                RuntimeError,
                json.JSONDecodeError,
            ) as exc:
                if attempt >= self.max_retries:
                    self.stats.failed_requests += 1
                    raise RuntimeError(f"request failed after retries: {exc}") from exc
                self.stats.retries += 1
                sleep_s = self.backoff_base * (2**attempt)
                time.sleep(sleep_s)

    @staticmethod
    def _record_key(entry: Dict[str, Any], mode: str) -> str:
        skill = entry.get("skill", {})
        latest = entry.get("latestVersion", {})
        sid = skill.get("_id") or entry.get("_id")
        slug = skill.get("slug")
        version_id = latest.get("_id")
        if sid and version_id:
            return f"{mode}:{sid}:{version_id}"
        if sid:
            return f"{mode}:{sid}"
        if slug:
            return f"{mode}:{slug}"
        return f"{mode}:{hashlib.sha256(json_dumps_compact(entry).encode('utf-8')).hexdigest()}"

    def _enrich_entry(self, entry: Dict[str, Any], crawl_mode: str) -> Dict[str, Any]:
        return {
            "fetched_at": utc_now_iso(),
            "source_url": SITE_URL,
            "crawl_mode": crawl_mode,
            "raw": entry,
        }

    def _collect_highlighted(self) -> List[Dict[str, Any]]:
        # This endpoint has a tighter server-side validation than listPublicPageV4.
        highlighted_limit = min(self.page_size, 20)
        result = self._post_query("skills:listHighlightedPublic", {"limit": highlighted_limit})
        self.stats.pages += 1
        if not isinstance(result, list):
            return []
        return result

    def _collect_popular_or_all(self) -> List[Dict[str, Any]]:
        all_items: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        seen_cursors = set()

        while True:
            if self.stats.pages >= self.max_pages:
                break
            args: Dict[str, Any] = {
                "numItems": self.page_size,
                "sort": "downloads",
                "dir": "desc",
                "nonSuspiciousOnly": self.non_suspicious_only,
            }
            if cursor:
                args["cursor"] = cursor

            value = self._post_query("skills:listPublicPageV4", args)
            self.stats.pages += 1

            page = value.get("page", []) if isinstance(value, dict) else []
            if not isinstance(page, list):
                page = []

            all_items.extend(page)
            has_more = bool(value.get("hasMore")) if isinstance(value, dict) else False
            next_cursor = value.get("nextCursor") if isinstance(value, dict) else None

            if not has_more or not next_cursor:
                break
            if next_cursor in seen_cursors:
                break
            seen_cursors.add(next_cursor)
            cursor = str(next_cursor)

        return all_items

    def collect(self) -> List[Dict[str, Any]]:
        if self.mode == "highlighted":
            return self._collect_highlighted()
        if self.mode in {"popular", "all"}:
            return self._collect_popular_or_all()
        raise ValueError(f"unsupported mode: {self.mode}")

    def run(self) -> Dict[str, Any]:
        raw_entries = self.collect()
        results: List[Dict[str, Any]] = []
        state_items: Dict[str, str] = self.state.get("items", {})

        for entry in raw_entries:
            if not isinstance(entry, dict):
                continue
            self.stats.total_seen += 1
            key = self._record_key(entry, self.mode)
            enriched = self._enrich_entry(entry, self.mode)
            fp = fingerprint_record(enriched["raw"])

            prev_fp = state_items.get(key)
            if prev_fp is None:
                self.stats.added += 1
            elif prev_fp != fp:
                self.stats.updated += 1
            else:
                self.stats.skipped += 1

            state_items[key] = fp
            results.append(enriched)

        output = {
            "meta": {
                "mode": self.mode,
                "source_url": SITE_URL,
                "convex_url": CONVEX_URL,
                "fetched_at": utc_now_iso(),
                "stats": self.stats.__dict__,
            },
            "items": results,
        }

        self.state["updated_at"] = utc_now_iso()
        self.state["meta"] = {
            "last_mode": self.mode,
            "last_output": str(self.output_path),
            "last_total_seen": self.stats.total_seen,
            "last_pages": self.stats.pages,
        }

        dump_json_file(self.output_path, output)
        dump_json_file(self.state_path, self.state)
        return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ClawHub skill crawler (API-first)")
    parser.add_argument(
        "--mode",
        choices=["all", "highlighted", "popular"],
        default="all",
        help="crawl scope",
    )
    parser.add_argument("--output", default="./skills.json", help="output JSON path")
    parser.add_argument("--state-file", default="./.clawhub_state.json", help="state JSON path")
    parser.add_argument("--proxy", default=None, help="proxy URL, e.g. http://127.0.0.1:7890")
    parser.add_argument("--timeout", type=float, default=15.0, help="request timeout seconds")
    parser.add_argument("--retries", type=int, default=4, help="max retries per request")
    parser.add_argument(
        "--backoff-base", type=float, default=0.5, help="retry backoff base seconds"
    )
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="items per page")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5000,
        help="safety cap for paginated requests",
    )
    parser.add_argument(
        "--full-scan",
        action="store_true",
        help="disable practical page cap (sets max-pages to a very large value)",
    )
    parser.add_argument(
        "--include-suspicious",
        action="store_true",
        help="include suspicious skills (default: non-suspicious only)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="print final stats as indented JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    effective_max_pages = (10**9) if args.full_scan else max(1, args.max_pages)
    crawler = ClawHubCrawler(
        mode=args.mode,
        timeout=max(1.0, args.timeout),
        retries=max(0, args.retries),
        backoff_base=max(0.1, args.backoff_base),
        output_path=Path(args.output),
        state_path=Path(args.state_file),
        proxy=args.proxy,
        page_size=max(1, args.page_size),
        non_suspicious_only=not args.include_suspicious,
        max_pages=effective_max_pages,
    )

    try:
        output = crawler.run()
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    stats = output["meta"]["stats"]
    if args.pretty:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(json_dumps_compact(stats))
    print(f"output={crawler.output_path}")
    print(f"state={crawler.state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
