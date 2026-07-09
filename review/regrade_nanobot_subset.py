"""Re-grade the already-executed nanobot DeepSeek-V4-Pro-Venus subset run using the fixed
``_summarize_transcript`` (see lib_grading.py fix for string-vs-list message content).

Re-uses the saved transcripts/execution results in
``evoclawbench/results/0084_openai-deepseek-v4-pro-venus_nanobot.json`` and only re-runs the
grading step (no new agent executions).
"""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "agent_res_y-sk-608581d717c1b3fd2c5473a057fc18d8")
os.environ.setdefault("OPENAI_BASE_URL", "http://21.139.195.158:18080/v1")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "evoclawbench" / "scripts"))

import lib_grading  # noqa: E402
import lib_tasks  # noqa: E402

RESULTS_PATH = (
    REPO_ROOT / "evoclawbench" / "results" / "0084_openai-deepseek-v4-pro-venus_nanobot.json"
)
JUDGE_MODEL = "openai/gpt-5.4-mini"


def regrade(task, exec_result):
    grade = lib_grading.grade_task(
        task=task,
        execution_result=exec_result,
        skill_dir=REPO_ROOT / "evoclawbench",
        judge_model=JUDGE_MODEL,
        runtime="nanobot",
    )
    return grade.score, grade.notes


def main():
    loader = lib_tasks.TaskLoader(REPO_ROOT / "evoclawbench" / "tasks")
    tasks = {t.task_id: t for t in loader.load_all_tasks()}

    data = json.loads(RESULTS_PATH.read_text())
    report = {"baseline": {}, "preskill": {}, "postskill_first": {}, "postskill_second": {}}

    for tid, entry in data.get("baseline_results", {}).items():
        task = tasks.get(tid)
        if not task or task.grading_type != "hybrid":
            continue
        exec_result = entry["results"][0]
        score, notes = regrade(task, exec_result)
        report["baseline"][tid] = {"old": entry.get("mean_score"), "new": score, "notes": notes[:150]}
        entry["mean_score"] = score

    for tid, entry in data.get("preskill_results", {}).items():
        task = tasks.get(tid)
        if not task or task.grading_type != "hybrid":
            continue
        exec_result = entry["results"][0]
        score, notes = regrade(task, exec_result)
        report["preskill"][tid] = {"old": entry.get("mean_score"), "new": score, "notes": notes[:150]}
        entry["mean_score"] = score

    for tid, entry in data.get("postskill_results", {}).items():
        task = tasks.get(tid)
        if not task or task.grading_type != "hybrid":
            continue
        first_exec = entry["first_pass_results"][0]
        second_exec = entry["results"][0]
        first_score, first_notes = regrade(task, first_exec)
        second_score, second_notes = regrade(task, second_exec)
        report["postskill_first"][tid] = {
            "old": entry.get("first_pass_mean_score"),
            "new": first_score,
            "notes": first_notes[:150],
        }
        report["postskill_second"][tid] = {
            "old": entry.get("second_pass_mean_score"),
            "new": second_score,
            "notes": second_notes[:150],
        }
        entry["first_pass_mean_score"] = first_score
        entry["second_pass_mean_score"] = second_score
        entry["mean_score"] = second_score
        entry["second_vs_first_delta"] = second_score - first_score
        entry["second_vs_first_ratio"] = (second_score / first_score) if first_score else None

    print(json.dumps(report, indent=2))

    def mean(d):
        vals = [v["new"] for v in d.values()]
        return sum(vals) / len(vals) if vals else None

    print("\n=== Hybrid-subset means (re-graded) ===")
    print("baseline:", mean(report["baseline"]))
    print("preskill:", mean(report["preskill"]))
    print("postskill_first:", mean(report["postskill_first"]))
    print("postskill_second:", mean(report["postskill_second"]))

    RESULTS_PATH.write_text(json.dumps(data, indent=2))
    print(f"\nRe-graded and saved back to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
