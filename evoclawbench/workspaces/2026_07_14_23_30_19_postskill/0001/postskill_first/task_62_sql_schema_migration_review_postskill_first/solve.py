#!/usr/bin/env python3
"""Solve all 5 SQL schema migration review cases."""

import csv
import hashlib
import json
import os

TASK_ID = "task_62_sql_schema_migration_review"
PREFIX = "evoclawbench-difficulty-hardening-20260524-v4"
INPUT_DIR = "assets/generated_tasks/task_62_sql_schema_migration_review"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_csv(path):
    manifests = []
    records = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            section = row.get("section", "").strip()
            if section == "manifest":
                manifests.append(row)
            elif section == "record":
                records.append(row)
    return manifests, records


def compute_checksum(packet_id, nonce, case_id):
    seed = f"{PREFIX}|{TASK_ID}|{case_id}|{packet_id}|{nonce}"
    h = hashlib.sha256(seed.encode()).hexdigest()
    return h[:16]


def select_packet(manifests, case_id):
    candidates = []
    for m in manifests:
        packet_id = m["packet_id"].strip()
        nonce = m["nonce"].strip()
        state = m.get("state", "").strip()
        superseded_by = m.get("superseded_by", "").strip()
        checksum = m.get("checksum", "").strip()
        source_weight = int(m.get("source_weight", "0").strip())
        revision = int(m.get("revision", "0").strip())

        if state != "approved":
            continue
        if superseded_by:
            continue
        expected = compute_checksum(packet_id, nonce, case_id)
        if checksum != expected:
            continue

        candidates.append((revision, source_weight, packet_id))

    if not candidates:
        raise ValueError(f"No valid packet found for {case_id}")

    candidates.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return candidates[0][2]


def process_numeric(records, selected_packet, channel):
    total = 0.0
    for r in records:
        if r["packet_id"].strip() != selected_packet:
            continue
        if r.get("status", "").strip() != "final":
            continue
        if r.get("channel", "").strip() != channel:
            continue
        if r.get("kind", "").strip() != "numeric_delta":
            continue

        amount = int(r.get("amount_minor", "0").strip())
        scale = int(r.get("scale", "1").strip())
        operator = r.get("operator", "").strip()

        delta = amount / scale
        if operator == "subtract":
            total -= delta
        else:
            total += delta

    if channel == "N1":
        return int(round(total))
    return round(total, 2)


def process_list(records, selected_packet, channel):
    actions = []
    for r in records:
        if r["packet_id"].strip() != selected_packet:
            continue
        if r.get("status", "").strip() != "final":
            continue
        if r.get("channel", "").strip() != channel:
            continue
        if r.get("kind", "").strip() != "list_action":
            continue

        revision = int(r.get("revision", "0").strip())
        action = r.get("action", "").strip()
        value = r.get("value", "").strip()
        target = r.get("target", "").strip()
        actions.append((revision, action, value, target))

    actions.sort(key=lambda x: x[0])

    result_set = set()
    for _, action, value, target in actions:
        if action == "include":
            result_set.add(value)
        elif action == "remove":
            result_set.discard(target)
        elif action == "alias":
            if target in result_set:
                result_set.discard(target)
                result_set.add(value)

    return sorted(result_set)


def process_text(records, selected_packet, channel):
    candidates = []
    for r in records:
        if r["packet_id"].strip() != selected_packet:
            continue
        if r.get("status", "").strip() != "final":
            continue
        if r.get("channel", "").strip() != channel:
            continue
        if r.get("kind", "").strip() != "text_candidate":
            continue

        candidate = r.get("candidate", "").strip()
        score = int(r.get("score", "0").strip())
        penalty = int(r.get("penalty", "0").strip())
        candidates.append((score - penalty, candidate))

    if not candidates:
        return ""

    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][1]


def solve_case(case_path, case_id):
    manifests, records = parse_csv(case_path)
    selected = select_packet(manifests, case_id)

    row_count = process_numeric(records, selected, "N1")
    quality_failures = process_list(records, selected, "L1")
    metric_delta = process_numeric(records, selected, "N2")
    rule_ids = process_list(records, selected, "L2")
    experiment_winner = process_text(records, selected, "T1")

    return {
        "row_count": row_count,
        "quality_failures": quality_failures,
        "metric_delta": metric_delta,
        "rule_ids": rule_ids,
        "experiment_winner": experiment_winner,
    }


def main():
    for i in range(1, 6):
        case_id = f"case_{i:02d}"
        case_path = os.path.join(INPUT_DIR, f"{case_id}.csv")
        report = solve_case(case_path, case_id)
        out_path = os.path.join(OUTPUT_DIR, f"{case_id}_report.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"{case_id}: {json.dumps(report, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
