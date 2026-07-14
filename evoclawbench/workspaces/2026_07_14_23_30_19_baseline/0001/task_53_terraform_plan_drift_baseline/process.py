#!/usr/bin/env python3
"""Process all 5 terraform plan drift cases and produce output reports."""

import hashlib
import json
import yaml
import os
from pathlib import Path

DEFAULT_BASE = "assets/generated_tasks/task_53_terraform_plan_drift"
OUT = "outputs"
SEED = "evoclawbench-difficulty-hardening-20260524-v4"


def resolve_base_dir():
    """Resolve the task asset directory even when this workspace omits local assets."""
    env_base = os.environ.get("TASK_53_BASE")
    candidates = []
    if env_base:
        candidates.append(Path(env_base))

    cwd = Path.cwd()
    repo_root = Path(__file__).resolve().parents[4]
    candidates.extend([
        cwd / DEFAULT_BASE,
        Path(__file__).resolve().parent / DEFAULT_BASE,
        repo_root / "assets/generated_tasks/task_53_terraform_plan_drift",
    ])

    for candidate in candidates:
        if (candidate / "case_01.yaml").exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate task assets for task_53_terraform_plan_drift. "
        "Set TASK_53_BASE or provide assets/generated_tasks/task_53_terraform_plan_drift locally."
    )

def compute_checksum(task_id, case_id, packet_id, nonce):
    """First 16 hex chars of sha256 of the seed string."""
    s = f"{SEED}|{task_id}|{case_id}|{packet_id}|{nonce}"
    h = hashlib.sha256(s.encode()).hexdigest()
    return h[:16]

def select_packet(manifest, task_id, case_id):
    """Select the winning packet from the manifest."""
    candidates = []
    for pkt in manifest:
        if pkt.get('state') != 'approved':
            continue
        if pkt.get('superseded_by', ''):
            continue
        expected = compute_checksum(task_id, case_id, pkt['packet_id'], pkt['nonce'])
        if pkt['checksum'] != expected:
            continue
        candidates.append(pkt)
    
    if not candidates:
        raise ValueError("No valid packets found")
    
    candidates.sort(key=lambda p: (-p['revision'], -p['source_weight'], p['packet_id']))
    return candidates[0]

def process_case(case_file):
    """Process a single case YAML file and return the report dict."""
    with open(case_file, 'r') as f:
        data = yaml.safe_load(f)
    
    task_id = data['task_id']
    case_id = data['case_id']
    manifest = data['packet_manifest']
    records = data['records']
    
    selected = select_packet(manifest, task_id, case_id)
    selected_id = selected['packet_id']
    
    # Filter records: only selected packet_id and status=final
    selected_records = [r for r in records 
                        if r.get('packet_id') == selected_id and r.get('status') == 'final']
    
    report = {}
    
    # B1: boolean gates
    b1_records = [r for r in selected_records if r['channel'] == 'B1' and r['kind'] == 'boolean_gate']
    report['backup_passed'] = all(r['observed'] == r['expected'] for r in b1_records)
    
    # L1: list actions -> policy_violations
    l1_records = [r for r in selected_records if r['channel'] == 'L1' and r['kind'] == 'list_action']
    l1_records.sort(key=lambda r: r['revision'])
    l1_set = set()
    for r in l1_records:
        action = r['action']
        if action == 'include':
            l1_set.add(r['value'])
        elif action == 'remove':
            l1_set.discard(r.get('target', r.get('value')))
        elif action == 'alias':
            target = r['target']
            if target in l1_set:
                l1_set.discard(target)
                l1_set.add(r['value'])
    report['policy_violations'] = sorted(l1_set)
    
    # L2: list actions -> required_changes
    l2_records = [r for r in selected_records if r['channel'] == 'L2' and r['kind'] == 'list_action']
    l2_records.sort(key=lambda r: r['revision'])
    l2_set = set()
    for r in l2_records:
        action = r['action']
        if action == 'include':
            l2_set.add(r['value'])
        elif action == 'remove':
            l2_set.discard(r.get('target', r.get('value')))
        elif action == 'alias':
            target = r['target']
            if target in l2_set:
                l2_set.discard(target)
                l2_set.add(r['value'])
    report['required_changes'] = sorted(l2_set)
    
    # N1: numeric deltas -> risk_score
    n1_records = [r for r in selected_records if r['channel'] == 'N1' and r['kind'] == 'numeric_delta']
    total = 0.0
    for r in n1_records:
        val = r['amount_minor'] / r['scale']
        if r['operator'] == 'subtract':
            total -= val
        else:
            total += val
    report['risk_score'] = round(total, 2)
    
    # T1: text candidates -> slo_status
    t1_records = [r for r in selected_records if r['channel'] == 'T1' and r['kind'] == 'text_candidate']
    best = None
    best_net = None
    for r in t1_records:
        net = r['score'] - r['penalty']
        if best is None or net > best_net or (net == best_net and r['candidate'] < best):
            best = r['candidate']
            best_net = net
    report['slo_status'] = best
    
    return report

def main():
    base_dir = resolve_base_dir()
    os.makedirs(OUT, exist_ok=True)
    print(f"Using task assets from: {base_dir}")
    for i in range(1, 6):
        case_file = base_dir / f"case_{i:02d}.yaml"
        report = process_case(case_file)
        out_file = os.path.join(OUT, f"case_{i:02d}_report.json")
        with open(out_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"case_{i:02d}: {out_file}")
        print(f"  policy_violations: {report['policy_violations']}")
        print(f"  required_changes: {report['required_changes']}")
        print(f"  slo_status: {report['slo_status']}")
        print(f"  backup_passed: {report['backup_passed']}")
        print(f"  risk_score: {report['risk_score']}")

if __name__ == '__main__':
    main()