#!/usr/bin/env python3
import csv
import hashlib
import json
import re
from html import unescape
from pathlib import Path
from typing import Any

SEED = "evoclawbench-difficulty-hardening-20260524-v4"
TASK_ID = "task_82_facilities_maintenance_prioritization"
REQUIRED_FIELDS = [
    "priority_assets",
    "maintenance_due",
    "anomaly_ids",
    "diagnostic_codes",
    "dispatch_required",
]


def coerce_scalar(value: Any):
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return ""
        low = s.lower()
        if low == "null":
            return None
        if low == "true":
            return True
        if low == "false":
            return False
        if (s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']')):
            try:
                return json.loads(s)
            except Exception:
                return value
    return value


def parse_json_or_yaml(text: str):
    try:
        return json.loads(text)
    except Exception:
        import yaml  # type: ignore
        return yaml.safe_load(text)


def load_fixture(path: Path):
    suffix = path.suffix.lower()
    if suffix in {'.json', '.yaml', '.yml'}:
        data = parse_json_or_yaml(path.read_text())
        return data
    if suffix == '.csv':
        manifest, records = [], []
        meta = {}
        with path.open(newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = {k: coerce_scalar(v) for k, v in row.items()}
                section = row.pop('section', None)
                if section == 'manifest':
                    manifest.append(row)
                elif section == 'record':
                    records.append(row)
                elif section == 'protocol':
                    meta.update({k: v for k, v in row.items() if v not in (None, '')})
        out = dict(meta)
        out['packet_manifest'] = manifest
        out['records'] = records
        return out
    if suffix in {'.txt', '.jsonl', '.ndjson'}:
        manifest, records = [], []
        meta = {}
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith('MANIFEST'):
                _, payload = line.split(None, 1)
                manifest.append(json.loads(payload))
            elif line.startswith('RECORD'):
                _, payload = line.split(None, 1)
                records.append(json.loads(payload))
            elif line.startswith('PROTOCOL'):
                _, payload = line.split(None, 1)
                meta.update(json.loads(payload))
        out = dict(meta)
        out['packet_manifest'] = manifest
        out['records'] = records
        return out
    if suffix in {'.html', '.htm'}:
        text = path.read_text()
        def extract(section):
            m = re.search(rf'<script[^>]*type=["\']application/json["\'][^>]*data-section=["\']{section}["\'][^>]*>(.*?)</script>', text, re.S | re.I)
            if not m:
                return None
            return json.loads(unescape(m.group(1).strip()))
        manifest = extract('manifest') or []
        records = extract('records') or []
        protocol = extract('protocol') or {}
        out = dict(protocol)
        out['packet_manifest'] = manifest
        out['records'] = records
        return out
    raise ValueError(f'Unsupported fixture format: {path}')


def valid_checksum(task_id: str, case_id: str, packet_id: str, nonce: str) -> str:
    s = f"{SEED}|{task_id}|{case_id}|{packet_id}|{nonce}"
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def select_packet(data: dict):
    task_id = data['task_id']
    case_id = data['case_id']
    candidates = []
    for pkt in data['packet_manifest']:
        if pkt.get('state') != 'approved':
            continue
        if str(pkt.get('superseded_by', '') or '') != '':
            continue
        expected = valid_checksum(task_id, case_id, pkt['packet_id'], pkt['nonce'])
        if pkt.get('checksum') != expected:
            continue
        candidates.append(pkt)
    if not candidates:
        raise ValueError(f'No valid packet for {case_id}')
    candidates.sort(key=lambda p: (-int(p.get('revision', 0)), -int(p.get('source_weight', 0)), str(p['packet_id'])))
    return candidates[0]


def reduce_list(records):
    items = []
    for idx, r in sorted(enumerate(records), key=lambda t: (int(t[1].get('revision', 0)), t[0])):
        action = r.get('action') or r.get('list_action')
        value = r.get('value')
        target = r.get('target')
        if action == 'include':
            if value is not None:
                items.append(str(value))
        elif action == 'remove':
            victim = target if target not in (None, '') else value
            if victim is not None:
                victim = str(victim)
                items = [x for x in items if x != victim]
        elif action == 'alias':
            if target is not None:
                target = str(target)
                items = [x for x in items if x != target]
            if value is not None:
                items.append(str(value))
    return sorted(set(items))


def reduce_bool(records):
    gates = [r for r in records if r.get('kind') == 'boolean_gate']
    return all(str(r.get('observed')) == str(r.get('expected')) for r in gates)


def solve_case(path: Path):
    data = load_fixture(path)
    packet = select_packet(data)
    selected = [r for r in data['records'] if r.get('packet_id') == packet['packet_id'] and r.get('status') == 'final']
    channels = {}
    for r in selected:
        channels.setdefault(r.get('channel'), []).append(r)
    report = {
        'priority_assets': reduce_list([r for r in channels.get('L1', []) if r.get('kind') == 'list_action']),
        'maintenance_due': reduce_list([r for r in channels.get('L2', []) if r.get('kind') == 'list_action']),
        'anomaly_ids': reduce_list([r for r in channels.get('L3', []) if r.get('kind') == 'list_action']),
        'diagnostic_codes': reduce_list([r for r in channels.get('L4', []) if r.get('kind') == 'list_action']),
        'dispatch_required': reduce_bool(channels.get('B1', [])),
    }
    return {k: report[k] for k in REQUIRED_FIELDS}


def main():
    base = Path(__file__).resolve().parents[3]
    in_dir = base / 'assets' / 'generated_tasks' / TASK_ID
    out_dir = base / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = sorted([p for p in in_dir.iterdir() if p.is_file() and p.name.startswith('case_')])
    if len(cases) != 5:
        print(f'warning: expected 5 cases, found {len(cases)}')
    for case_path in cases:
        report = solve_case(case_path)
        out_path = out_dir / f'{case_path.stem}_report.json'
        out_path.write_text(json.dumps(report, indent=2, sort_keys=False) + '\n')
        print(f'wrote {out_path}')

if __name__ == '__main__':
    main()
