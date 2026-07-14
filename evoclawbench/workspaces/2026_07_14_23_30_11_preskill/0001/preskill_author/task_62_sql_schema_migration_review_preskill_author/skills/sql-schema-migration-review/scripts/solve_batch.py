#!/usr/bin/env python3
import argparse
import csv
import hashlib
import html as html_lib
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

PREFIX = "evoclawbench-difficulty-hardening-20260524-v4"
OUTPUT_MAP = {
    "N1": "row_count",
    "L1": "quality_failures",
    "N2": "metric_delta",
    "L2": "rule_ids",
    "T1": "experiment_winner",
}


def clean(v):
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s if s != "" else None
    return v


def as_int(v, default=0):
    v = clean(v)
    if v is None:
        return default
    return int(v)


def as_decimal(v, default="0"):
    v = clean(v)
    if v is None:
        return Decimal(default)
    return Decimal(str(v))


def checksum(task_id, case_id, packet_id, nonce):
    msg = f"{PREFIX}|{task_id}|{case_id}|{packet_id}|{nonce}".encode()
    return hashlib.sha256(msg).hexdigest()[:16]


def normalize_manifest_entry(entry):
    return {
        "packet_id": clean(entry.get("packet_id")),
        "nonce": clean(entry.get("nonce")),
        "checksum": clean(entry.get("checksum")),
        "state": clean(entry.get("state")),
        "superseded_by": clean(entry.get("superseded_by")),
        "source_weight": as_int(entry.get("source_weight")),
        "revision": as_int(entry.get("revision")),
    }


def normalize_record(entry, seq):
    out = {k: clean(v) for k, v in entry.items()}
    out["_seq"] = seq
    out["revision"] = as_int(entry.get("revision"), 0)
    out["amount_minor"] = as_decimal(entry.get("amount_minor"), "0")
    out["scale"] = as_decimal(entry.get("scale"), "1")
    out["score"] = as_decimal(entry.get("score"), "0")
    out["penalty"] = as_decimal(entry.get("penalty"), "0")
    out["delta"] = as_decimal(entry.get("delta"), "0")
    return out


class ScriptBlockParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = {}
        self._capture = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        attrs = dict(attrs)
        if attrs.get("type") == "application/json" and attrs.get("data-section"):
            self._capture = attrs["data-section"]
            self._buf = []

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._capture:
            self.blocks[self._capture] = "".join(self._buf)
            self._capture = None
            self._buf = []


def parse_csv(path):
    manifests, records = [], []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        seq = 0
        for row in reader:
            section = clean(row.get("section"))
            if section == "manifest":
                manifests.append(normalize_manifest_entry(row))
            elif section == "record":
                seq += 1
                records.append(normalize_record(row, seq))
    return manifests, records


def parse_json_yaml(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML unavailable for YAML fixture")
        data = yaml.safe_load(text)
    manifests = [normalize_manifest_entry(x) for x in data.get("packet_manifest", [])]
    records = [normalize_record(x, i + 1) for i, x in enumerate(data.get("records", []))]
    return manifests, records


def parse_text_jsonl(path):
    manifests, records = [], []
    seq = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("MANIFEST"):
            payload = json.loads(line[len("MANIFEST"):].strip())
            manifests.append(normalize_manifest_entry(payload))
        elif line.startswith("RECORD"):
            payload = json.loads(line[len("RECORD"):].strip())
            seq += 1
            records.append(normalize_record(payload, seq))
    return manifests, records


def parse_html(path):
    parser = ScriptBlockParser()
    parser.feed(path.read_text(encoding="utf-8"))
    manifest_raw = parser.blocks.get("manifest", "[]")
    records_raw = parser.blocks.get("records", "[]")
    manifests = [normalize_manifest_entry(x) for x in json.loads(html_lib.unescape(manifest_raw))]
    records = [normalize_record(x, i + 1) for i, x in enumerate(json.loads(html_lib.unescape(records_raw)))]
    return manifests, records


def parse_fixture(path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return parse_csv(path)
    if suffix in {".json", ".yaml", ".yml"}:
        return parse_json_yaml(path)
    if suffix in {".txt", ".jsonl", ".ndjson"}:
        return parse_text_jsonl(path)
    if suffix in {".html", ".htm"}:
        return parse_html(path)
    raise ValueError(f"Unsupported fixture format: {path}")


def select_packet(manifests, task_id, case_id):
    candidates = []
    for m in manifests:
        if m["state"] != "approved":
            continue
        if m["superseded_by"]:
            continue
        if not all([m["packet_id"], m["nonce"], m["checksum"]]):
            continue
        if checksum(task_id, case_id, m["packet_id"], m["nonce"]) != m["checksum"]:
            continue
        candidates.append(m)
    if not candidates:
        raise ValueError(f"No valid packet for {case_id}")
    candidates.sort(key=lambda m: (-m["revision"], -m["source_weight"], m["packet_id"]))
    return candidates[0]


def selected_records(records, packet_id):
    return [r for r in records if r.get("packet_id") == packet_id and r.get("status") == "final"]


def apply_numeric(rows, integer=False):
    total = Decimal("0")
    for r in rows:
        scale = r["scale"] if r["scale"] != 0 else Decimal("1")
        amount = r["amount_minor"] / scale
        if r.get("operator") == "subtract":
            amount = -amount
        total += amount
    if integer:
        return int(total)
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def apply_list(rows):
    items = []
    ordered = sorted(rows, key=lambda r: (r.get("revision", 0), r.get("_seq", 0)))
    for r in ordered:
        action = r.get("action")
        value = r.get("value")
        target = r.get("target") or value
        if action == "include":
            if value is not None:
                items.append(value)
        elif action == "remove":
            items = [x for x in items if x != target]
        elif action == "alias":
            if target is not None:
                items = [value if x == target else x for x in items]
                if target not in items and value is not None and target != value:
                    pass
    return sorted(set(x for x in items if x is not None))


def apply_text(rows):
    best = None
    for r in rows:
        score = r["score"] - r["penalty"]
        cand = r.get("candidate")
        choice = (score, cand)
        if best is None or score > best[0] or (score == best[0] and cand < best[1]):
            best = (score, cand)
    return best[1] if best else ""


def solve_case(path, task_id):
    case_id = path.stem
    manifests, records = parse_fixture(path)
    pkt = select_packet(manifests, task_id, case_id)
    rows = selected_records(records, pkt["packet_id"])
    by_channel = {}
    for r in rows:
        by_channel.setdefault(r.get("channel"), []).append(r)
    report = {
        "row_count": apply_numeric(by_channel.get("N1", []), integer=True),
        "quality_failures": apply_list(by_channel.get("L1", [])),
        "metric_delta": apply_numeric(by_channel.get("N2", []), integer=False),
        "rule_ids": apply_list(by_channel.get("L2", [])),
        "experiment_winner": apply_text(by_channel.get("T1", [])),
    }
    return case_id, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--task-id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_absolute():
        cwd_candidate = Path.cwd() / input_dir
        root_candidate = ROOT / input_dir
        input_dir = cwd_candidate if cwd_candidate.exists() else root_candidate
    task_id = args.task_id or input_dir.name
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    case_files = sorted([p for p in input_dir.iterdir() if p.is_file()])
    for path in case_files:
        case_id, report = solve_case(path, task_id)
        text = json.dumps(report, indent=2, ensure_ascii=False)
        if args.dry_run:
            print(f"== {case_id} ==")
            print(text)
        else:
            out = output_dir / f"{case_id}_report.json"
            out.write_text(text + "\n", encoding="utf-8")
            print(out)


if __name__ == "__main__":
    main()
