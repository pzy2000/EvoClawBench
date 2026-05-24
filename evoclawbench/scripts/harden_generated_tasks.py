#!/usr/bin/env python3
"""Rewrite generated EvoClawBench tasks with harder deterministic fixtures.

This is a one-shot corpus maintenance script. It keeps the public output schema
for each generated task unchanged, but replaces answer-shaped fixtures with a
multi-packet evidence protocol that requires packet validation, revision
filtering, channel mapping, and per-type aggregation.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import pprint
import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
ASSETS_DIR = ROOT / "assets" / "generated_tasks"
SEED = "evoclawbench-difficulty-hardening-20260524-v4"
CASE_COUNT = 5
HARD_MODE_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class FieldSpec:
    name: str
    channel: str
    kind: str


@dataclass(frozen=True)
class TaskSpec:
    path: Path
    task_id: str
    task_name: str
    title: str
    family: str
    grader_family: str
    frontmatter_text: str
    frontmatter: dict[str, Any]
    required_fields: list[str]
    numeric_fields: list[str]
    list_fields: list[str]
    dict_fields: list[str]
    bool_fields: list[str]
    text_fields: list[str]
    field_specs: list[FieldSpec]
    subproblem_titles: list[str]


def stable_int(*parts: object, modulo: int, offset: int = 0) -> int:
    material = "|".join([SEED, *(str(part) for part in parts)])
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % modulo + offset


def stable_token(prefix: str, *parts: object, size: int = 8) -> str:
    material = "|".join([SEED, prefix, *(str(part) for part in parts)])
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:size]
    return f"{prefix}-{digest}".upper()


def packet_checksum(task_id: str, case_id: str, packet_id: str, nonce: str) -> str:
    material = f"{SEED}|{task_id}|{case_id}|{packet_id}|{nonce}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def literal_assignment(code: str, name: str) -> Any:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise ValueError(f"Could not find assignment for {name}")


def extract_code(text: str, task_path: Path) -> str:
    match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
    if not match:
        raise ValueError(f"{task_path} has no Python automated check block")
    return match.group(1)


def parse_task(path: Path) -> TaskSpec | None:
    text = path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"No frontmatter in {path}")
    frontmatter_text, body = frontmatter_match.groups()
    frontmatter = yaml.safe_load(frontmatter_text)
    task_id = str(frontmatter.get("id", ""))
    task_number_match = re.match(r"task_(\d+)_", task_id)
    if not task_number_match or int(task_number_match.group(1)) < 22:
        return None

    title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else str(frontmatter["name"])
    subproblem_titles = re.findall(r"^###\s+Sub-Problem\s+\d+:\s*(.+)$", body, re.MULTILINE)
    if len(subproblem_titles) != CASE_COUNT:
        subproblem_titles = [
            "North Region Batch",
            "Partner Portal Export",
            "Back Office Queue",
            "Legacy System Extract",
            "Daily Exception Batch",
        ]

    code = extract_code(text, path)
    required_fields = list(literal_assignment(code, "required_fields"))
    numeric_fields = list(literal_assignment(code, "numeric_fields"))
    list_fields = list(literal_assignment(code, "list_fields"))
    dict_fields = list(literal_assignment(code, "dict_fields"))
    bool_fields = list(literal_assignment(code, "bool_fields"))
    text_fields = list(literal_assignment(code, "text_fields"))

    counters = {"numeric": 0, "list": 0, "dict": 0, "bool": 0, "text": 0}
    field_specs = []
    for field in required_fields:
        if field in numeric_fields:
            kind = "numeric"
            prefix = "N"
        elif field in list_fields:
            kind = "list"
            prefix = "L"
        elif field in dict_fields:
            kind = "dict"
            prefix = "D"
        elif field in bool_fields:
            kind = "bool"
            prefix = "B"
        elif field in text_fields:
            kind = "text"
            prefix = "T"
        else:
            raise ValueError(f"{path}: {field} is not classified")
        counters[kind] += 1
        field_specs.append(FieldSpec(name=field, channel=f"{prefix}{counters[kind]}", kind=kind))

    return TaskSpec(
        path=path,
        task_id=task_id,
        task_name=str(frontmatter["name"]),
        title=title,
        family=str(frontmatter.get("task_family", "")),
        grader_family=str(frontmatter["grader_family"]),
        frontmatter_text=frontmatter_text,
        frontmatter=frontmatter,
        required_fields=required_fields,
        numeric_fields=numeric_fields,
        list_fields=list_fields,
        dict_fields=dict_fields,
        bool_fields=bool_fields,
        text_fields=text_fields,
        field_specs=field_specs,
        subproblem_titles=subproblem_titles,
    )


def field_abbrev(field: str) -> str:
    parts = re.findall(r"[a-z0-9]+", field.lower())
    if not parts:
        return "VAL"
    return "".join(part[:3] for part in parts)[:9].upper()


def list_value_for_field(field: str, task_id: str, case_index: int, ordinal: int) -> str:
    if "currenc" in field:
        currencies = ["USD", "EUR", "JPY", "GBP", "CAD", "AUD", "CHF"]
        return currencies[stable_int(field, task_id, case_index, ordinal, modulo=len(currencies))]
    if "section" in field:
        sections = ["overview", "risk", "metrics", "launch", "owner", "appendix"]
        return sections[stable_int(field, task_id, case_index, ordinal, modulo=len(sections))]
    if "action" in field and "item" not in field:
        actions = ["hold", "escalate", "approve_with_note", "reject", "manual_review"]
        return actions[stable_int(field, task_id, case_index, ordinal, modulo=len(actions))]
    prefix = field_abbrev(field)
    return f"{prefix}-{case_index:02d}-{stable_int(field, task_id, ordinal, modulo=97, offset=11)}"


def dict_buckets_for_field(field: str) -> list[str]:
    lower = field.lower()
    if "routing" in lower:
        return ["clinical", "admin", "pharmacy"]
    if "severity" in lower:
        return ["critical", "high", "medium", "low"]
    if "risk" in lower:
        return ["financial", "operational", "compliance"]
    if "score" in lower:
        return ["technical", "process", "evidence"]
    return ["alpha", "beta", "gamma"]


def text_candidates_for_field(field: str, task_id: str, case_index: int) -> list[str]:
    lower = field.lower()
    if "date" in lower:
        base_month = stable_int(field, task_id, case_index, modulo=9, offset=1)
        return [f"2026-{base_month:02d}-{day:02d}" for day in (7, 14, 21)]
    if "vendor" in lower:
        return ["Vendor-Orion", "Vendor-Nimbus", "Vendor-Kestrel"]
    if "winner" in lower:
        return ["control", "variant_a", "variant_b"]
    if "summary" in lower:
        return ["watchlist_review", "exec_escalation", "routine_closeout"]
    if "template" in lower:
        return ["apology_credit", "technical_escalation", "policy_clarification"]
    if "track" in lower:
        return ["standard", "accelerated", "intervention"]
    if "status" in lower:
        return ["green", "amber", "red"]
    return [
        f"{field_abbrev(field).lower()}_primary",
        f"{field_abbrev(field).lower()}_secondary",
        f"{field_abbrev(field).lower()}_exception",
    ]


def text_value(
    task: TaskSpec,
    field: str,
    case_id: str,
    case_index: int,
    channel: str,
) -> tuple[str, list[dict[str, Any]]]:
    candidates = text_candidates_for_field(field, task.task_id, case_index)
    rows = []
    best_value = candidates[0]
    best_net = -10_000
    for idx, candidate in enumerate(candidates):
        score = stable_int(task.task_id, case_id, channel, candidate, modulo=70, offset=20)
        penalty = stable_int(task.task_id, case_id, channel, candidate, "penalty", modulo=18)
        if idx == 1:
            score += 12
        net = score - penalty
        if net > best_net or (net == best_net and candidate < best_value):
            best_net = net
            best_value = candidate
        rows.append(
            {
                "channel": channel,
                "kind": "text_candidate",
                "record_id": stable_token("TXT", task.task_id, case_id, channel, idx),
                "candidate": candidate,
                "score": score,
                "penalty": penalty,
                "status": "final",
                "revision": 3,
                "note": "rank by score minus penalty; tie by candidate text",
            }
        )
    return best_value, rows


def numeric_value(
    task: TaskSpec,
    field: str,
    case_id: str,
    case_index: int,
    channel: str,
) -> tuple[int | float, list[dict[str, Any]]]:
    count_like = "count" in field.lower() or field.lower().endswith("_ids")
    scale = 1 if count_like else 100
    rows = []
    total_minor = 0
    for idx in range(5):
        amount_minor = stable_int(
            task.task_id,
            case_id,
            channel,
            idx,
            modulo=4600 if scale == 100 else 19,
            offset=215 if scale == 100 else 2,
        )
        operator = "subtract" if idx in {2, 4} else "add"
        signed = -amount_minor if operator == "subtract" else amount_minor
        total_minor += signed
        rows.append(
            {
                "channel": channel,
                "kind": "numeric_delta",
                "record_id": stable_token("NUM", task.task_id, case_id, channel, idx),
                "operator": operator,
                "amount_minor": amount_minor,
                "scale": scale,
                "status": "final",
                "revision": 3,
                "note": "apply signed amount_minor divided by scale",
            }
        )
    if total_minor <= 0:
        repair_minor = abs(total_minor) + (7 if scale == 1 else 725)
        total_minor += repair_minor
        rows.append(
            {
                "channel": channel,
                "kind": "numeric_delta",
                "record_id": stable_token("NUM", task.task_id, case_id, channel, "repair"),
                "operator": "add",
                "amount_minor": repair_minor,
                "scale": scale,
                "status": "final",
                "revision": 3,
                "note": "positive-control adjustment",
            }
        )
    if scale == 1:
        return int(total_minor), rows
    return round(total_minor / scale, 2), rows


def list_value(
    task: TaskSpec,
    field: str,
    case_id: str,
    case_index: int,
    channel: str,
) -> tuple[list[str], list[dict[str, Any]]]:
    base_values = []
    for idx in range(4):
        value = list_value_for_field(field, task.task_id, case_index, idx)
        if value not in base_values:
            base_values.append(value)
    if not base_values:
        base_values = [f"{field_abbrev(field)}-{case_index:02d}-A"]

    rows = []
    for idx, value in enumerate(base_values):
        rows.append(
            {
                "channel": channel,
                "kind": "list_action",
                "record_id": stable_token("LST", task.task_id, case_id, channel, idx),
                "action": "include",
                "value": value,
                "status": "final",
                "revision": 3,
                "note": "include unless a later remove or alias targets it",
            }
        )
    removed = f"{field_abbrev(field)}-{case_index:02d}-DECOY"
    rows.append(
        {
            "channel": channel,
            "kind": "list_action",
            "record_id": stable_token("LST", task.task_id, case_id, channel, "remove"),
            "action": "remove",
            "target": removed,
            "value": removed,
            "status": "final",
            "revision": 3,
            "note": "remove this candidate if it appears in a lower revision",
        }
    )
    return sorted(base_values), rows


def dict_value(
    task: TaskSpec,
    field: str,
    case_id: str,
    channel: str,
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    buckets = dict_buckets_for_field(field)
    rows = []
    totals: dict[str, int] = {}
    for idx, bucket in enumerate(buckets):
        first = stable_int(task.task_id, case_id, channel, bucket, modulo=8, offset=1)
        second = stable_int(task.task_id, case_id, channel, bucket, "second", modulo=5)
        correction = stable_int(task.task_id, case_id, channel, bucket, "correction", modulo=3)
        totals[bucket] = first + second - correction
        for suffix, delta in (("a", first), ("b", second), ("c", -correction)):
            rows.append(
                {
                    "channel": channel,
                    "kind": "dict_delta",
                    "record_id": stable_token(
                        "DCT", task.task_id, case_id, channel, bucket, suffix
                    ),
                    "bucket": bucket,
                    "delta": delta,
                    "status": "final",
                    "revision": 3,
                    "note": "sum deltas per bucket after packet selection",
                }
            )
    return {key: value for key, value in totals.items() if value != 0}, rows


def bool_value(
    task: TaskSpec,
    case_id: str,
    case_index: int,
    channel: str,
) -> tuple[bool, list[dict[str, Any]]]:
    failing_gate = stable_int(task.task_id, case_id, channel, modulo=4)
    should_fail = (
        case_index in {2, 5} or stable_int(task.task_id, case_id, channel, "fail", modulo=5) == 0
    )
    rows = []
    passed = True
    for idx in range(4):
        expected = "clear"
        observed = "blocked" if should_fail and idx == failing_gate else "clear"
        if observed != expected:
            passed = False
        rows.append(
            {
                "channel": channel,
                "kind": "boolean_gate",
                "record_id": stable_token("BOL", task.task_id, case_id, channel, idx),
                "expected": expected,
                "observed": observed,
                "status": "final",
                "revision": 3,
                "note": "field is true only when all selected gates match expected",
            }
        )
    return passed, rows


def selected_packet_manifest(task_id: str, case_id: str) -> tuple[str, list[dict[str, Any]]]:
    packet_ids = [
        stable_token("PKT", task_id, case_id, "selected", size=6),
        stable_token("PKT", task_id, case_id, "superseded", size=6),
        stable_token("PKT", task_id, case_id, "invalid", size=6),
        stable_token("PKT", task_id, case_id, "draft", size=6),
    ]
    manifest = []
    selected = packet_ids[0]
    for idx, packet_id in enumerate(packet_ids):
        nonce = stable_token("NON", task_id, case_id, packet_id, size=10)
        checksum = packet_checksum(task_id, case_id, packet_id, nonce)
        if idx == 2:
            checksum = checksum[:-1] + ("0" if checksum[-1] != "0" else "1")
        manifest.append(
            {
                "packet_id": packet_id,
                "nonce": nonce,
                "checksum": checksum,
                "state": "approved" if idx != 3 else "draft",
                "revision": 3 - idx if idx < 3 else 4,
                "superseded_by": selected if idx == 1 else "",
                "source_weight": 90 - idx * 7,
                "note": "candidate evidence packet; validate before using records",
            }
        )
    return selected, manifest


def decoy_records(
    task: TaskSpec,
    case_id: str,
    packet_ids: list[str],
    case_index: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for packet_id in packet_ids:
        for field in task.field_specs:
            for idx in range(5):
                row: dict[str, Any] = {
                    "packet_id": packet_id,
                    "channel": field.channel,
                    "record_id": stable_token(
                        "NOI", task.task_id, case_id, packet_id, field.channel, idx
                    ),
                    "status": "draft" if idx % 2 else "final",
                    "revision": 1 + idx % 2,
                    "note": "decoy from unselected or invalid packet",
                }
                if field.kind == "numeric":
                    row.update(
                        {
                            "kind": "numeric_delta",
                            "operator": "add",
                            "amount_minor": stable_int(
                                task.task_id,
                                case_id,
                                packet_id,
                                field.channel,
                                idx,
                                modulo=9000,
                                offset=100,
                            ),
                            "scale": 100,
                        }
                    )
                elif field.kind == "list":
                    row.update(
                        {
                            "kind": "list_action",
                            "action": "include",
                            "value": list_value_for_field(
                                field.name,
                                f"{task.task_id}-{packet_id}",
                                case_index,
                                idx,
                            ),
                        }
                    )
                elif field.kind == "dict":
                    buckets = dict_buckets_for_field(field.name)
                    row.update(
                        {
                            "kind": "dict_delta",
                            "bucket": buckets[idx % len(buckets)],
                            "delta": stable_int(
                                task.task_id,
                                case_id,
                                packet_id,
                                field.channel,
                                idx,
                                modulo=9,
                                offset=-2,
                            ),
                        }
                    )
                elif field.kind == "bool":
                    row.update(
                        {
                            "kind": "boolean_gate",
                            "expected": "clear",
                            "observed": "clear" if idx % 3 else "blocked",
                        }
                    )
                else:
                    candidates = text_candidates_for_field(field.name, task.task_id, case_index)
                    row.update(
                        {
                            "kind": "text_candidate",
                            "candidate": candidates[idx % len(candidates)],
                            "score": 88 - idx,
                            "penalty": idx,
                        }
                    )
                rows.append(row)
    return rows


def build_case_payload(task: TaskSpec, case_index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = f"case_{case_index:02d}"
    selected_packet, manifest = selected_packet_manifest(task.task_id, case_id)
    packet_ids = [item["packet_id"] for item in manifest if item["packet_id"] != selected_packet]
    expected: dict[str, Any] = {}
    records: list[dict[str, Any]] = []

    for field in task.field_specs:
        if field.kind == "numeric":
            value, field_rows = numeric_value(task, field.name, case_id, case_index, field.channel)
        elif field.kind == "list":
            value, field_rows = list_value(task, field.name, case_id, case_index, field.channel)
        elif field.kind == "dict":
            value, field_rows = dict_value(task, field.name, case_id, field.channel)
        elif field.kind == "bool":
            value, field_rows = bool_value(task, case_id, case_index, field.channel)
        elif field.kind == "text":
            value, field_rows = text_value(task, field.name, case_id, case_index, field.channel)
        else:
            raise ValueError(f"Unsupported field kind: {field.kind}")
        expected[field.name] = value
        for row in field_rows:
            row["packet_id"] = selected_packet
            records.append(row)

    records.extend(decoy_records(task, case_id, packet_ids, case_index))
    records = sorted(records, key=lambda row: (row["packet_id"], row["channel"], row["record_id"]))
    channel_map = {
        field.channel: {"field": field.name, "kind": field.kind} for field in task.field_specs
    }
    payload = {
        "difficulty_protocol": "evoclawbench-hard-mode-v4",
        "seed_hint": SEED,
        "task_id": task.task_id,
        "case_id": case_id,
        "case_title": task.subproblem_titles[case_index - 1],
        "channel_map": channel_map,
        "packet_manifest": manifest,
        "records": records,
        "rules_digest": {
            "packet": (
                "approved, not superseded, valid checksum, then highest " "revision/source_weight"
            ),
            "numeric": "sum selected numeric_delta rows by signed amount_minor / scale",
            "list": "include/remove/alias selected list_action rows and sort final strings",
            "dict": "sum selected dict_delta rows by bucket and omit zero buckets",
            "bool": "true only when every selected boolean_gate observed equals expected",
            "text": "choose selected text_candidate with max score minus penalty",
        },
    }
    return payload, expected


def csv_value(value: Any) -> str:
    if isinstance(value, (dict, list, bool)):
        return json.dumps(value, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def render_csv(payload: dict[str, Any]) -> str:
    fields = [
        "section",
        "packet_id",
        "nonce",
        "checksum",
        "state",
        "superseded_by",
        "source_weight",
        "revision",
        "channel",
        "kind",
        "record_id",
        "status",
        "operator",
        "amount_minor",
        "scale",
        "action",
        "value",
        "target",
        "bucket",
        "delta",
        "expected",
        "observed",
        "candidate",
        "score",
        "penalty",
        "note",
    ]
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerow(
        {
            "section": "protocol",
            "value": payload["difficulty_protocol"],
            "note": "metadata row; use manifest and record rows for derivation",
        }
    )
    for packet in payload["packet_manifest"]:
        row = {key: csv_value(packet.get(key, "")) for key in fields}
        row["section"] = "manifest"
        writer.writerow(row)
    for record in payload["records"]:
        row = {key: csv_value(record.get(key, "")) for key in fields}
        row["section"] = "record"
        writer.writerow(row)
    return out.getvalue()


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "# EvoClawBench hard-mode evidence file",
        f"# protocol={payload['difficulty_protocol']} task_id={payload['task_id']}",
        "# Lines are tab-delimited: MANIFEST<TAB>{json} or RECORD<TAB>{json}",
    ]
    for packet in payload["packet_manifest"]:
        lines.append("MANIFEST\t" + json.dumps(packet, sort_keys=True))
    for record in payload["records"]:
        lines.append("RECORD\t" + json.dumps(record, sort_keys=True))
    lines.append("")
    return "\n".join(lines)


def render_html(payload: dict[str, Any]) -> str:
    manifest = json.dumps(payload["packet_manifest"], indent=2, sort_keys=True)
    records = json.dumps(payload["records"], indent=2, sort_keys=True)
    channel_map = json.dumps(payload["channel_map"], indent=2, sort_keys=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{payload["task_id"]} {payload["case_id"]}</title>
</head>
<body data-protocol="{payload["difficulty_protocol"]}">
  <h1>{payload["case_title"]}</h1>
  <p>Protocol: {payload["difficulty_protocol"]}</p>
  <script type="application/json" data-section="channel-map">
{channel_map}
  </script>
  <script type="application/json" data-section="packet-manifest">
{manifest}
  </script>
  <script type="application/json" data-section="records">
{records}
  </script>
</body>
</html>
"""


def write_fixture(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    elif suffix in {".yaml", ".yml"}:
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    elif suffix == ".csv":
        path.write_text(render_csv(payload), encoding="utf-8")
    elif suffix == ".txt":
        path.write_text(render_text(payload), encoding="utf-8")
    elif suffix == ".html":
        path.write_text(render_html(payload), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported generated fixture format: {path}")


def task_file_for_case(task: TaskSpec, case_index: int) -> Path:
    file_specs = task.frontmatter.get("workspace_files", [])
    target = file_specs[case_index - 1]
    if not isinstance(target, str):
        raise ValueError(f"{task.task_id}: generated workspace_files must be strings")
    return ROOT / target


def render_prompt(task: TaskSpec) -> str:
    fields = ", ".join(f"`{field}`" for field in task.required_fields)
    channel_lines = "\n".join(
        f"- `{spec.channel}` -> `{spec.name}` ({spec.kind})" for spec in task.field_specs
    )
    return f"""You have 5 hard-mode {task.task_name.lower()} fixture files under \
`assets/generated_tasks/{task.task_id}/`.
For each input file, derive the required report from the evidence protocol and save \
`outputs/case_XX_report.json`.
This is a strict short-SLA batch task: solve all five cases quickly in one reusable pass.

Each report must be valid JSON with exactly these required fields: {fields}.
Use the channel map below to translate evidence channels into output fields:

{channel_lines}

Hard-mode evidence protocol:
0. JSON/YAML fixtures expose `packet_manifest` and `records` directly; CSV fixtures use
`section=manifest` and `section=record` rows and may include a metadata `section=protocol` row;
text fixtures use `MANIFEST`/`RECORD` JSON lines;
HTML fixtures store JSON in `<script type="application/json" data-section="...">` blocks.
1. Identify the selected packet from `packet_manifest`. Use only packets with \
`state=approved`, no `superseded_by`, and a valid checksum equal to the first 16 hex \
characters of `sha256("{SEED}|<task_id>|<case_id>|<packet_id>|<nonce>")`. If more than one \
packet remains, choose the highest `revision`, then highest `source_weight`, then lowest \
`packet_id`.
2. Use only `records` whose `packet_id` is the selected packet and whose `status` is `final`.
3. Numeric channels: apply each `numeric_delta` as signed `amount_minor / scale`, subtracting \
rows whose `operator` is `subtract`; count-like fields must be integers, other numeric fields \
must be rounded to two decimals.
4. List channels: apply `list_action` rows in revision order. `include` adds `value`, `remove` \
removes `target` or `value`, and `alias` replaces `target` with `value`. Emit sorted unique \
strings.
5. Dict channels: sum `dict_delta.delta` by `bucket` and omit zero-valued buckets.
6. Boolean channels: emit `true` only if every selected `boolean_gate` has `observed` equal to \
`expected`.
7. Text channels: choose the `text_candidate` with the largest `score - penalty`; break ties by \
the lexicographically smallest candidate string and emit the candidate exactly.

Do not copy values from unselected, draft, superseded, invalid-checksum, or decoy packets. Do not \
modify the input fixtures; only write files under `outputs/`."""


def render_frontmatter(task: TaskSpec) -> str:
    lines = task.frontmatter_text.splitlines()
    rendered = []
    replaced = False
    for line in lines:
        if re.match(r"^timeout_seconds:\s*", line):
            rendered.append(f"timeout_seconds: {HARD_MODE_TIMEOUT_SECONDS}")
            replaced = True
        else:
            rendered.append(line)
    if not replaced:
        rendered.append(f"timeout_seconds: {HARD_MODE_TIMEOUT_SECONDS}")
    return "\n".join(rendered)


def render_expected_behavior() -> str:
    return "\n".join(
        [
            "1. Parse each fixture format into packet manifest rows and evidence records.",
            "2. Validate packet checksums and discard draft, superseded, invalid, and "
            "decoy packets before aggregation.",
            "3. Apply the channel-specific derivation rules for numeric, list, dict, "
            "boolean, and text outputs.",
            "4. Write one strict JSON report per case under `outputs/`, preserving the "
            "required schema exactly.",
            "5. Recheck all five reports against the selected-packet evidence rather "
            "than trusting visible decoys.",
        ]
    )


def render_subproblems(task: TaskSpec) -> str:
    blocks = []
    for index, title in enumerate(task.subproblem_titles, 1):
        fixture = task.frontmatter["workspace_files"][index - 1]
        blocks.append(
            f"### Sub-Problem {index}: {title}\n"
            f"- Input: `{fixture}`\n"
            "- Special handling: select the valid evidence packet, discard all decoys, and derive "
            f"{', '.join(task.required_fields)} for this {task.family.lower()} case.\n"
            f"- Expected output: `outputs/case_{index:02d}_report.json`"
        )
    return "\n\n".join(blocks)


def render_grading_criteria(task: TaskSpec) -> str:
    lines = [
        "- [ ] All five `outputs/case_XX_report.json` files exist.",
        "- [ ] Each report is valid JSON and contains every required field.",
        "- [ ] The report ignores draft, superseded, invalid-checksum, and decoy packet records.",
    ]
    for field in task.required_fields:
        lines.append(f"- [ ] Each report includes `{field}` with the correctly derived value.")
    return "\n".join(lines)


def render_grader(task: TaskSpec, expected: dict[str, dict[str, Any]]) -> str:
    expected_repr = pprint.pformat(expected, width=96, sort_dicts=True)
    required_repr = pprint.pformat(task.required_fields, width=96)
    numeric_repr = pprint.pformat(task.numeric_fields, width=96)
    list_repr = pprint.pformat(task.list_fields, width=96)
    dict_repr = pprint.pformat(task.dict_fields, width=96)
    bool_repr = pprint.pformat(task.bool_fields, width=96)
    text_repr = pprint.pformat(task.text_fields, width=96)
    family_marker = f"{task.grader_family}_grader"
    return f"""```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import math
    from pathlib import Path

    workspace = Path(workspace_path)
    output_dir = workspace / "outputs"
    expected = {expected_repr}
    required_fields = {required_repr}
    numeric_fields = {numeric_repr}
    list_fields = {list_repr}
    dict_fields = {dict_repr}
    bool_fields = {bool_repr}
    text_fields = {text_repr}
    family_marker = "{family_marker}"
    scores = {{}}

    def load_report(path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    def normalize_list(value):
        if not isinstance(value, list):
            return []
        normalized = []
        for item in value:
            if isinstance(item, list):
                normalized.append(tuple(str(part) for part in item))
            else:
                normalized.append(str(item))
        return sorted(normalized, key=str)

    def normalize_dict(value):
        if not isinstance(value, dict):
            return {{}}
        normalized = {{}}
        for key, item in value.items():
            normalized[str(key)] = round(item, 4) if isinstance(item, float) else item
        return normalized

    def compare(field, actual, wanted):
        if field in numeric_fields:
            return isinstance(actual, (int, float)) and math.isclose(
                float(actual), float(wanted), rel_tol=1e-4, abs_tol=1e-4
            )
        if field in list_fields:
            return normalize_list(actual) == normalize_list(wanted)
        if field in dict_fields:
            return normalize_dict(actual) == normalize_dict(wanted)
        if field in bool_fields:
            return isinstance(actual, bool) and actual is bool(wanted)
        if field in text_fields:
            return str(actual).strip().lower() == str(wanted).strip().lower()
        return actual == wanted

    for case_id, wanted in expected.items():
        prefix = case_id.replace("case_", "sub_")
        report_path = output_dir / f"{{case_id}}_report.json"
        exists = report_path.is_file()
        scores[f"{{prefix}}_{{family_marker}}_exists"] = 1.0 if exists else 0.0
        if not exists:
            for field in required_fields:
                scores[f"{{prefix}}_field_{{field}}"] = 0.0
            continue
        data = load_report(report_path)
        if data is None:
            scores[f"{{prefix}}_{{family_marker}}_valid_json"] = 0.0
            for field in required_fields:
                scores[f"{{prefix}}_field_{{field}}"] = 0.0
            continue
        scores[f"{{prefix}}_{{family_marker}}_valid_json"] = 1.0
        scores[f"{{prefix}}_{{family_marker}}_required_fields"] = (
            1.0 if all(field in data for field in required_fields) else 0.0
        )
        for field, wanted_value in wanted.items():
            scores[f"{{prefix}}_field_{{field}}"] = (
                1.0 if compare(field, data.get(field), wanted_value) else 0.0
            )
    return scores
```"""


def render_task(task: TaskSpec, expected: dict[str, dict[str, Any]]) -> str:
    return f"""---
{render_frontmatter(task)}
---

# {task.title}

Process five hard-mode fixture-backed {task.family.lower()} cases. Each case includes competing \
evidence packets, stale revisions, and decoy records; only the selected packet should drive the \
final report.

---

## Prompt

{render_prompt(task)}

---

## Expected Behavior

{render_expected_behavior()}

---

## Sub-Problems

{render_subproblems(task)}

---

## Grading Criteria

{render_grading_criteria(task)}

---

## Automated Checks

{render_grader(task, expected)}
"""


def harden_task(task: TaskSpec) -> None:
    all_expected = {}
    for case_index in range(1, CASE_COUNT + 1):
        payload, expected = build_case_payload(task, case_index)
        write_fixture(task_file_for_case(task, case_index), payload)
        all_expected[f"case_{case_index:02d}"] = expected
    task.path.write_text(render_task(task, all_expected), encoding="utf-8")


def main() -> None:
    tasks = []
    for path in sorted(TASKS_DIR.glob("task_*.md")):
        task = parse_task(path)
        if task is not None:
            tasks.append(task)
    for task in tasks:
        harden_task(task)
    print(f"Hardened {len(tasks)} generated tasks with {len(tasks) * CASE_COUNT} fixtures")


if __name__ == "__main__":
    main()
