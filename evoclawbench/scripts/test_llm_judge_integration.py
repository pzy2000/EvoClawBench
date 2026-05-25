"""
End-to-end integration test for LLM judge in hybrid grading mode.

Tests that:
1. _grade_llm_judge makes a real LLM API call (via local proxy)
2. grade_task correctly dispatches to hybrid mode for task_02/06/07
3. Final score is a weighted combination of automated + LLM judge scores
4. Breakdown contains both 'automated.*' and 'llm_judge.*' keys

Run from the scripts/ directory:
    OPENAI_BASE_URL=http://localhost:16666/v1 OPENAI_API_KEY=dummy \
    python test_llm_judge_integration.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Allow running from scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))

from lib_grading import (
    _call_llm,
    _parse_judge_response,
    _parse_model_name,
    grade_task,
)
from lib_tasks import TaskLoader

TASKS_DIR = Path(__file__).parent.parent / "tasks"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "openai/qwen3.5-plus")

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
INFO = "\033[94m·\033[0m"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print(symbol: str, msg: str) -> None:
    print(f"  {symbol} {msg}")


def _assert(condition: bool, msg: str) -> None:
    if condition:
        _print(PASS, msg)
    else:
        _print(FAIL, f"FAILED: {msg}")
        sys.exit(1)


def _load_task(task_id: str):
    loader = TaskLoader(TASKS_DIR)
    for t in loader.load_all_tasks():
        if t.task_id == task_id:
            return t
    raise ValueError(f"Task not found: {task_id}")


def _build_minimal_execution_result(workspace: Path) -> dict:
    return {
        "transcript": [
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Task completed."}],
                },
            }
        ],
        "workspace": str(workspace),
        "status": "success",
    }


def _write_mock_code_review_outputs(workspace: Path) -> None:
    """Write minimal but valid security review JSONs for task_06."""
    outputs = workspace / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    reviews = [
        ("login_handler_review.json", "login_handler.py", "python"),
        ("user_profile_review.json", "user_profile.js", "javascript"),
        ("file_manager_review.json", "file_manager.py", "python"),
        ("api_handler_review.json", "api_handler.go", "go"),
        ("admin_panel_review.json", "admin_panel.py", "python"),
    ]
    for fname, source, lang in reviews:
        report = {
            "file": source,
            "language": lang,
            "vulnerabilities": [
                {
                    "line": 10,
                    "type": "SQL Injection",
                    "severity": "critical",
                    "description": "User input directly concatenated into SQL query.",
                    "fix_suggestion": "Use parameterized queries.",
                },
                {
                    "line": 25,
                    "type": "Hardcoded Secret",
                    "severity": "high",
                    "description": "Secret key hardcoded in source.",
                    "fix_suggestion": "Use environment variables.",
                },
                {
                    "line": 40,
                    "type": "Missing Input Validation",
                    "severity": "medium",
                    "description": "No validation on user-supplied data.",
                    "fix_suggestion": "Validate and sanitize all inputs.",
                },
            ],
            "risk_score": 8.5,
            "summary": "Critical SQL injection and hardcoded credentials found.",
        }
        (outputs / fname).write_text(json.dumps(report, indent=2))


def _write_mock_doc_extraction_outputs(workspace: Path) -> None:
    """Write minimal but valid extraction JSONs for task_07."""
    outputs = workspace / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    (outputs / "invoice_001.json").write_text(
        json.dumps(
            {
                "vendor": {
                    "name": "TechVision Solutions",
                    "address": "123 Tech St",
                    "phone": "555-0100",
                    "email": "billing@techvision.com",
                    "tax_id": "12-3456789",
                },
                "client": {
                    "name": "DataFlow Corp",
                    "address": "456 Data Ave",
                    "contact_person": "Jane Smith",
                },
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15",
                "due_date": "2024-02-14",
                "payment_terms": "Net 30",
                "purchase_order": "PO-2024-0042",
                "line_items": [
                    {
                        "description": "Software License",
                        "quantity": 1,
                        "unit_price": 2500.0,
                        "total": 2500.0,
                    },
                    {
                        "description": "Support Services",
                        "quantity": 40,
                        "unit_price": 150.0,
                        "total": 6000.0,
                    },
                    {
                        "description": "Training",
                        "quantity": 8,
                        "unit_price": 200.0,
                        "total": 1600.0,
                    },
                ],
                "subtotal": 10100.0,
                "tax_rate": "8.5%",
                "tax_amount": 858.5,
                "grand_total": 10958.5,
                "bank_details": {
                    "bank": "First National Bank",
                    "account_name": "TechVision",
                    "routing_number": "021000021",
                    "account_number": "1234567890",
                },
            },
            indent=2,
        )
    )

    (outputs / "resume_001.json").write_text(
        json.dumps(
            {
                "name": "Alex Johnson",
                "title": "Senior Software Engineer",
                "contact": {
                    "email": "alex@email.com",
                    "phone": "555-0200",
                    "location": "San Francisco, CA",
                    "linkedin": "linkedin.com/in/alex",
                    "github": "github.com/alex",
                },
                "summary": "Experienced engineer with 8 years in distributed systems.",
                "work_experience": [
                    {
                        "title": "Senior Engineer",
                        "company": "TechCorp",
                        "start_date": "2020-01",
                        "end_date": "Present",
                        "highlights": ["Led migration to microservices"],
                    },
                    {
                        "title": "Engineer",
                        "company": "StartupX",
                        "start_date": "2017-06",
                        "end_date": "2019-12",
                        "highlights": ["Built real-time analytics"],
                    },
                ],
                "education": [
                    {
                        "degree": "BS Computer Science",
                        "institution": "UC Berkeley",
                        "year": "2017",
                        "details": "GPA 3.8",
                    }
                ],
                "skills": {
                    "languages": ["Python", "Go", "Java"],
                    "frameworks": ["Django", "FastAPI"],
                    "cloud": ["AWS", "GCP"],
                    "data": ["PostgreSQL", "Redis"],
                    "tools": ["Docker", "Kubernetes"],
                },
                "certifications": ["AWS Solutions Architect"],
            },
            indent=2,
        )
    )

    (outputs / "contract_001.json").write_text(
        json.dumps(
            {
                "title": "Software Development Services Agreement",
                "effective_date": "2024-01-01",
                "parties": [
                    {
                        "name": "DevShop LLC",
                        "address": "789 Dev Rd",
                        "contact_person": "Bob Dev",
                        "role": "Service Provider",
                    },
                    {
                        "name": "ClientCo",
                        "address": "321 Client Ave",
                        "contact_person": "Alice Client",
                        "role": "Client",
                    },
                ],
                "scope_of_work": ["Develop web application", "Provide 6 months support"],
                "total_value": 150000.0,
                "payment_schedule": [
                    {
                        "milestone": "Project kickoff",
                        "percentage": "25%",
                        "amount": 37500.0,
                        "due_date": "2024-01-15",
                    },
                    {
                        "milestone": "MVP delivery",
                        "percentage": "50%",
                        "amount": 75000.0,
                        "due_date": "2024-04-01",
                    },
                    {
                        "milestone": "Final delivery",
                        "percentage": "25%",
                        "amount": 37500.0,
                        "due_date": "2024-06-30",
                    },
                ],
                "duration": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                    "support_period": "6 months",
                },
                "termination_notice_days": 30,
                "governing_law": "California",
                "dispute_resolution": "Arbitration",
            },
            indent=2,
        )
    )

    (outputs / "meeting_notes_001.json").write_text(
        json.dumps(
            {
                "project": "Platform Redesign",
                "meeting_type": "Sprint Planning",
                "date": "2024-01-10",
                "time": "14:00",
                "location": "Conference Room A",
                "attendees": {"present": ["Alice", "Bob", "Carol"], "absent": ["Dave"]},
                "agenda": ["Sprint review", "Planning next sprint", "Blockers"],
                "discussion_points": [
                    {"topic": "Performance issues", "summary": "API latency above threshold"},
                    {
                        "topic": "New features",
                        "summary": "User dashboard requested by stakeholders",
                    },
                ],
                "action_items": [
                    {"assignee": "Alice", "task": "Optimize DB queries", "deadline": "2024-01-17"},
                    {
                        "assignee": "Bob",
                        "task": "Design dashboard mockup",
                        "deadline": "2024-01-15",
                    },
                    {"assignee": "Carol", "task": "Update documentation", "deadline": "2024-01-19"},
                ],
                "decisions": ["Use Redis for caching", "Delay mobile app to Q2"],
                "next_meeting": {
                    "date": "2024-01-17",
                    "time": "14:00",
                    "location": "Conference Room A",
                },
            },
            indent=2,
        )
    )

    (outputs / "expense_report_001.json").write_text(
        json.dumps(
            {
                "employee": {
                    "name": "John Doe",
                    "employee_id": "EMP-042",
                    "department": "Engineering",
                    "manager": "Jane Manager",
                },
                "period": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
                "purpose": "Q1 Client Visit - San Francisco",
                "line_items": [
                    {
                        "date": "2024-01-15",
                        "category": "Airfare",
                        "description": "Round trip NYC-SFO",
                        "amount": 450.0,
                    },
                    {
                        "date": "2024-01-15",
                        "category": "Hotel",
                        "description": "Marriott 3 nights",
                        "amount": 675.0,
                    },
                    {
                        "date": "2024-01-16",
                        "category": "Meals",
                        "description": "Client dinner",
                        "amount": 185.0,
                    },
                    {
                        "date": "2024-01-17",
                        "category": "Transport",
                        "description": "Uber to client office",
                        "amount": 45.0,
                    },
                    {
                        "date": "2024-01-17",
                        "category": "Meals",
                        "description": "Team lunch",
                        "amount": 120.0,
                    },
                ],
                "category_totals": {
                    "Airfare": 450.0,
                    "Hotel": 675.0,
                    "Meals": 305.0,
                    "Transport": 45.0,
                },
                "total": 1475.0,
                "approval_status": "Pending",
                "receipts_count": 5,
            },
            indent=2,
        )
    )


def _write_mock_log_analysis_outputs(workspace: Path) -> None:
    """Write minimal log analysis reports for task_02."""
    outputs = workspace / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    services = [
        "auth_service",
        "payment_service",
        "api_gateway",
        "notification_service",
        "scheduler_service",
    ]
    for service in services:
        report = {
            "service_name": service,
            "total_entries": 20,
            "error_count": 3,
            "warn_count": 5,
            "info_count": 12,
            "errors": [
                {
                    "timestamp": "2024-03-15T10:23:45",
                    "message": "Connection timeout",
                    "context": "req-001",
                },
                {
                    "timestamp": "2024-03-15T10:45:12",
                    "message": "Auth failure",
                    "context": "req-042",
                },
                {
                    "timestamp": "2024-03-15T11:02:33",
                    "message": "DB query error",
                    "context": "req-099",
                },
            ],
            "time_range": {"start": "2024-03-15T10:00:00", "end": "2024-03-15T12:00:00"},
            "summary": (
                f"Service {service} shows 3 errors including connection timeouts and auth "
                "failures; overall health is degraded."
            ),
        }
        (outputs / f"{service}_report.json").write_text(json.dumps(report, indent=2))


# ---------------------------------------------------------------------------
# Test 1: Unit tests for helper functions
# ---------------------------------------------------------------------------


def test_helpers() -> None:
    print("\n[Test 1] Helper functions")

    # _parse_model_name
    _assert(_parse_model_name("openai/gpt-4o") == ("openai", "gpt-4o"), "_parse_model_name openai/")
    _assert(
        _parse_model_name("openrouter/anthropic/claude-3") == ("openrouter", "anthropic/claude-3"),
        "_parse_model_name openrouter/",
    )
    _assert(_parse_model_name("gpt-4o") == ("openai", "gpt-4o"), "_parse_model_name bare")

    # _parse_judge_response - normal
    r = _parse_judge_response(
        '{"scores": {"recall": 0.8, "accuracy": 0.7}, "total": 0.75, "notes": "ok"}'
    )
    _assert(r.get("recall") == 0.8, "_parse_judge_response: recall=0.8")
    _assert(r.get("total") == 0.75, "_parse_judge_response: total=0.75")
    _assert(r.get("notes") == "ok", "_parse_judge_response: notes")

    # _parse_judge_response - code fence stripping
    r2 = _parse_judge_response('```json\n{"scores": {"val": 0.9}, "total": 0.9}\n```')
    _assert(r2.get("total") == 0.9, "_parse_judge_response: code fence stripped")

    # _parse_judge_response - flat format
    r3 = _parse_judge_response('{"recall": 0.6, "accuracy": 0.7, "total": 0.65}')
    _assert(r3.get("recall") == 0.6, "_parse_judge_response: flat format")

    # _parse_judge_response - error fallback
    r4 = _parse_judge_response("not json at all")
    _assert(r4.get("total") == 0.0, "_parse_judge_response: error fallback → 0.0")


# ---------------------------------------------------------------------------
# Test 2: Real LLM call via proxy
# ---------------------------------------------------------------------------


def test_llm_api_call() -> None:
    print("\n[Test 2] Real LLM API call via proxy")
    base_url = os.environ.get("OPENAI_BASE_URL", "http://localhost:16666/v1")
    _print(INFO, f"Using OPENAI_BASE_URL={base_url}, model={JUDGE_MODEL}")

    prompt = (
        "You are a grading function. Respond with ONLY this JSON (no markdown):\n"
        '{"scores": {"test_criterion": 0.8}, "total": 0.8, "notes": "test ok"}'
    )
    try:
        response = _call_llm(JUDGE_MODEL, prompt, timeout=60.0)
        _print(INFO, f"Raw response (first 200 chars): {response[:200]}")
        parsed = _parse_judge_response(response)
        _assert(
            isinstance(parsed.get("total"), (int, float)),
            "LLM returned parseable JSON with 'total'",
        )
        _assert(0.0 <= float(parsed["total"]) <= 1.0, f"total={parsed['total']} is in [0,1]")
        _print(
            PASS,
            (
                f"LLM judge API call succeeded: total={parsed['total']}, "
                f"notes={parsed.get('notes', '')!r}"
            ),
        )
    except Exception as e:
        _print(FAIL, f"LLM API call failed: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Test 3: Full hybrid grading — task_06 (Security Code Review)
# ---------------------------------------------------------------------------


def test_hybrid_task06() -> None:
    print("\n[Test 3] Hybrid grading – task_06_code_review (auto=0.6 / llm=0.4)")
    task = _load_task("task_06_code_review")
    _assert(task.grading_type == "hybrid", f"task grading_type={task.grading_type!r} == 'hybrid'")
    _assert(task.grading_weights is not None, "grading_weights set")
    _assert(task.llm_judge_rubric is not None, "llm_judge_rubric is set")
    _print(INFO, f"weights={task.grading_weights}")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        _write_mock_code_review_outputs(workspace)
        # Copy source files so context builder can read them
        for src_file in task.workspace_files:
            src = ASSETS_DIR / src_file.replace("assets/", "")
            dst = workspace / src_file
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                dst.write_bytes(src.read_bytes())

        exec_result = _build_minimal_execution_result(workspace)
        result = grade_task(
            task=task,
            execution_result=exec_result,
            skill_dir=Path(__file__).parent.parent,
            judge_model=JUDGE_MODEL,
            judge_timeout_seconds=90.0,
            verbose=True,
        )

    _print(INFO, f"grading_type={result.grading_type}, score={result.score:.4f}")
    _print(INFO, f"breakdown keys: {sorted(result.breakdown.keys())}")
    _assert(result.grading_type == "hybrid", "result.grading_type == 'hybrid'")
    _assert(result.score > 0.0, f"score={result.score:.4f} > 0 (LLM judge contributed)")
    automated_keys = [k for k in result.breakdown if k.startswith("automated.")]
    llm_keys = [k for k in result.breakdown if k.startswith("llm_judge.")]
    _assert(len(automated_keys) > 0, f"{len(automated_keys)} automated.* keys in breakdown")
    _assert(len(llm_keys) > 0, f"{len(llm_keys)} llm_judge.* keys in breakdown")
    _print(PASS, f"task_06 hybrid score={result.score:.4f}, notes={result.notes!r}")


# ---------------------------------------------------------------------------
# Test 4: Full hybrid grading — task_07 (Document Data Extraction)
# ---------------------------------------------------------------------------


def test_hybrid_task07() -> None:
    print("\n[Test 4] Hybrid grading – task_07_doc_extraction (auto=0.5 / llm=0.5)")
    task = _load_task("task_07_doc_extraction")
    _assert(task.grading_type == "hybrid", f"task grading_type={task.grading_type!r} == 'hybrid'")
    _assert(task.llm_judge_rubric is not None, "llm_judge_rubric is set")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        _write_mock_doc_extraction_outputs(workspace)
        for src_file in task.workspace_files:
            src = ASSETS_DIR / src_file.replace("assets/", "")
            dst = workspace / src_file
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                dst.write_bytes(src.read_bytes())

        exec_result = _build_minimal_execution_result(workspace)
        result = grade_task(
            task=task,
            execution_result=exec_result,
            skill_dir=Path(__file__).parent.parent,
            judge_model=JUDGE_MODEL,
            judge_timeout_seconds=90.0,
            verbose=True,
        )

    _print(INFO, f"grading_type={result.grading_type}, score={result.score:.4f}")
    _print(INFO, f"breakdown keys: {sorted(result.breakdown.keys())}")
    _assert(result.grading_type == "hybrid", "result.grading_type == 'hybrid'")
    _assert(result.score > 0.0, f"score={result.score:.4f} > 0")
    llm_keys = [k for k in result.breakdown if k.startswith("llm_judge.")]
    _assert(len(llm_keys) > 0, f"{len(llm_keys)} llm_judge.* keys in breakdown")
    _print(PASS, f"task_07 hybrid score={result.score:.4f}, notes={result.notes!r}")


# ---------------------------------------------------------------------------
# Test 5: Full hybrid grading — task_02 (Log Analysis, summary-only)
# ---------------------------------------------------------------------------


def test_hybrid_task02() -> None:
    print("\n[Test 5] Hybrid grading – task_02_log_analysis (auto=0.85 / llm=0.15)")
    task = _load_task("task_02_log_analysis")
    _assert(task.grading_type == "hybrid", f"task grading_type={task.grading_type!r} == 'hybrid'")
    _assert(task.llm_judge_rubric is not None, "llm_judge_rubric is set")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        _write_mock_log_analysis_outputs(workspace)

        exec_result = _build_minimal_execution_result(workspace)
        result = grade_task(
            task=task,
            execution_result=exec_result,
            skill_dir=Path(__file__).parent.parent,
            judge_model=JUDGE_MODEL,
            judge_timeout_seconds=60.0,
            verbose=True,
        )

    _print(INFO, f"grading_type={result.grading_type}, score={result.score:.4f}")
    _print(INFO, f"breakdown keys: {sorted(result.breakdown.keys())}")
    _assert(result.grading_type == "hybrid", "result.grading_type == 'hybrid'")
    _assert(result.score > 0.0, f"score={result.score:.4f} > 0")
    llm_keys = [k for k in result.breakdown if k.startswith("llm_judge.")]
    _assert(len(llm_keys) > 0, f"{len(llm_keys)} llm_judge.* keys in breakdown")
    _print(PASS, f"task_02 hybrid score={result.score:.4f}, notes={result.notes!r}")


# ---------------------------------------------------------------------------
# Test 6: Score weighting math
# ---------------------------------------------------------------------------


def test_score_weighting() -> None:
    print("\n[Test 6] Score weighting math")
    from lib_grading import GradeResult, _combine_grades

    task = _load_task("task_06_code_review")
    auto = GradeResult(
        task_id=task.task_id,
        score=1.0,
        max_score=1.0,
        grading_type="automated",
        breakdown={"sub_1_exists": 1.0},
        notes="",
    )
    llm = GradeResult(
        task_id=task.task_id,
        score=0.0,
        max_score=1.0,
        grading_type="llm_judge",
        breakdown={"recall": 0.0},
        notes="",
    )

    combined = _combine_grades(task, auto, llm)
    expected = 1.0 * 0.6 + 0.0 * 0.4  # = 0.6
    _assert(
        abs(combined.score - expected) < 1e-6,
        f"combined score={combined.score:.4f} == {expected} (0.6*auto + 0.4*llm)",
    )
    _assert(combined.grading_type == "hybrid", "combined.grading_type == 'hybrid'")
    _assert(
        "automated.sub_1_exists" in combined.breakdown,
        "breakdown contains 'automated.sub_1_exists'",
    )
    _assert("llm_judge.recall" in combined.breakdown, "breakdown contains 'llm_judge.recall'")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  LLM Judge Integration Tests")
    print(f"  Judge model: {JUDGE_MODEL}")
    print(f"  OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', '(not set, using default)')}")
    print("=" * 60)

    test_helpers()
    test_score_weighting()
    test_llm_api_call()
    test_hybrid_task06()
    test_hybrid_task07()
    test_hybrid_task02()

    print("\n" + "=" * 60)
    print("  All tests passed!")
    print("=" * 60)
