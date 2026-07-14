import csv, json, hashlib, os
from pathlib import Path

TASK_ID = 'task_92_crm_pipeline_hygiene'
SALT = 'evoclawbench-difficulty-hardening-20260524-v4'
CHANNEL_MAP = {
    'L1': 'stale_opportunities',
    'N1': 'forecast_delta',
    'L2': 'campaign_errors',
    'L3': 'action_items',
    'T1': 'executive_summary',
}


def load_csv_fixture(path: Path):
    rows = list(csv.DictReader(path.open(newline='', encoding='utf-8')))
    manifest = [r for r in rows if r.get('section') == 'manifest']
    records = [r for r in rows if r.get('section') == 'record']
    return manifest, records


def checksum_for(case_id: str, packet_id: str, nonce: str) -> str:
    raw = f'{SALT}|{TASK_ID}|{case_id}|{packet_id}|{nonce}'
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def pick_packet(case_id: str, manifest_rows):
    eligible = []
    for row in manifest_rows:
        if row.get('state') != 'approved':
            continue
        if (row.get('superseded_by') or '').strip():
            continue
        if checksum_for(case_id, row['packet_id'], row['nonce']) != row.get('checksum', ''):
            continue
        eligible.append(row)
    if not eligible:
        raise ValueError(f'No eligible packet for {case_id}')
    eligible.sort(key=lambda r: (-int(r['revision']), -int(r['source_weight']), r['packet_id']))
    return eligible[0]


def reduce_list(rows):
    state = []
    for row in rows:
        action = row.get('action')
        value = row.get('value')
        target = row.get('target')
        if action == 'include':
            if value and value not in state:
                state.append(value)
        elif action == 'remove':
            victim = target or value
            state = [x for x in state if x != victim]
        elif action == 'alias':
            if target:
                state = [x for x in state if x != target]
            if value and value not in state:
                state.append(value)
    return sorted(set(state))


def reduce_numeric(rows, field_name):
    total = 0.0
    for row in rows:
        amt = float(row['amount_minor']) / float(row['scale'])
        if row.get('operator') == 'subtract':
            amt = -amt
        total += amt
    if 'count' in field_name or field_name.endswith('_count'):
        return int(round(total))
    return round(total + 0.0, 2)


def reduce_text(rows):
    best = None
    for row in rows:
        candidate = row.get('candidate', '')
        score = float(row.get('score') or 0)
        penalty = float(row.get('penalty') or 0)
        rank = score - penalty
        item = (rank, candidate)
        if best is None or rank > best[0] or (rank == best[0] and candidate < best[1]):
            best = item
    return '' if best is None else best[1]


def solve_case(path: Path, output_dir: Path):
    case_id = path.stem
    manifest, records = load_csv_fixture(path)
    packet = pick_packet(case_id, manifest)
    packet_id = packet['packet_id']

    filtered = [r for r in records if r.get('packet_id') == packet_id and r.get('status') == 'final']

    by_channel = {}
    for idx, row in enumerate(filtered):
        row = dict(row)
        row['_idx'] = idx
        by_channel.setdefault(row.get('channel'), []).append(row)

    report = {
        'stale_opportunities': reduce_list(by_channel.get('L1', [])),
        'forecast_delta': reduce_numeric(by_channel.get('N1', []), 'forecast_delta'),
        'campaign_errors': reduce_list(by_channel.get('L2', [])),
        'action_items': reduce_list(by_channel.get('L3', [])),
        'executive_summary': reduce_text(by_channel.get('T1', [])),
    }

    out_path = output_dir / f'{case_id}_report.json'
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return packet_id, report


def main():
    workspace = Path('/Volumes/T7/EvoClaw/evoclawbench/workspaces/2026_07_14_23_30_11_preskill/0001/preskill_author/task_92_crm_pipeline_hygiene_preskill_author')
    inputs = Path('/Volumes/T7/EvoClaw/evoclawbench/assets/generated_tasks/task_92_crm_pipeline_hygiene')
    outputs = workspace / 'outputs'
    outputs.mkdir(parents=True, exist_ok=True)

    summary = {}
    for path in sorted(inputs.glob('case_*.csv')):
        packet_id, report = solve_case(path, outputs)
        summary[path.stem] = {'packet_id': packet_id, 'report': report}

    (workspace / 'outputs' / '_batch_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
