"""
EvoClawBench Task Library

Extended from PinchBench to support sub-problems for skill evolution evaluation.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class SubProblem:
    """Represents a single sub-problem within a task."""

    def __init__(
        self,
        index: int,
        title: str,
        description: str,
        expected_output: str = "",
    ):
        self.index = index
        self.title = title
        self.description = description
        self.expected_output = expected_output

    def __repr__(self) -> str:
        return f"SubProblem(index={self.index}, title={self.title})"


class Task:
    """Represents a single benchmark task with optional sub-problems."""

    def __init__(
        self,
        task_id: str,
        name: str,
        category: str,
        grading_type: str,
        timeout_seconds: int,
        workspace_files: List[Dict[str, str]],
        prompt: str,
        expected_behavior: str,
        grading_criteria: List[str],
        automated_checks: Optional[str] = None,
        llm_judge_rubric: Optional[str] = None,
        grading_weights: Optional[Dict[str, float]] = None,
        file_path: Optional[Path] = None,
        frontmatter: Optional[Dict[str, Any]] = None,
        sub_problems: Optional[List[SubProblem]] = None,
        skill_category: Optional[str] = None,
    ):
        self.task_id = task_id
        self.name = name
        self.category = category
        self.grading_type = grading_type
        self.timeout_seconds = timeout_seconds
        self.workspace_files = workspace_files
        self.prompt = prompt
        self.expected_behavior = expected_behavior
        self.grading_criteria = grading_criteria
        self.automated_checks = automated_checks
        self.llm_judge_rubric = llm_judge_rubric
        self.grading_weights = grading_weights
        self.file_path = file_path
        self.frontmatter = frontmatter or {}
        self.sub_problems = sub_problems or []
        self.skill_category = skill_category

    @property
    def num_sub_problems(self) -> int:
        return len(self.sub_problems)

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, name={self.name}, sub_problems={self.num_sub_problems})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "category": self.category,
            "grading_type": self.grading_type,
            "timeout_seconds": self.timeout_seconds,
            "workspace_files": self.workspace_files,
            "prompt": self.prompt,
            "expected_behavior": self.expected_behavior,
            "grading_criteria": self.grading_criteria,
            "has_automated_checks": self.automated_checks is not None,
            "has_llm_judge_rubric": self.llm_judge_rubric is not None,
            "grading_weights": self.grading_weights,
            "frontmatter": self.frontmatter,
            "num_sub_problems": self.num_sub_problems,
            "skill_category": self.skill_category,
        }


class TaskLoader:
    """Loads and parses task files from the tasks directory."""

    def __init__(self, tasks_dir: Path):
        self.tasks_dir = tasks_dir
        logger.info(f"Initialized TaskLoader with directory: {tasks_dir}")

    def load_all_tasks(self) -> List[Task]:
        tasks = []
        task_files = sorted(self.tasks_dir.glob("task_*.md"))
        logger.info(f"Found {len(task_files)} task files")

        for task_file in task_files:
            try:
                task = self.load_task(task_file)
                tasks.append(task)
                logger.info(f"Loaded task: {task.task_id} ({task.num_sub_problems} sub-problems)")
            except Exception as e:
                logger.error(f"Failed to load task from {task_file}: {e}", exc_info=True)

        logger.info(f"Successfully loaded {len(tasks)} tasks")
        return tasks

    def load_task(self, task_file: Path) -> Task:
        content = task_file.read_text(encoding="utf-8")

        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError(f"No YAML frontmatter found in {task_file}")

        frontmatter_text = frontmatter_match.group(1)
        body_text = frontmatter_match.group(2)

        try:
            metadata = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter in {task_file}: {e}")

        sections = self._parse_sections(body_text)
        grading_criteria = self._extract_grading_criteria(sections.get("Grading Criteria", ""))
        sub_problems = self._extract_sub_problems(sections.get("Sub-Problems", ""))

        task = Task(
            task_id=metadata.get("id", ""),
            name=metadata.get("name", ""),
            category=metadata.get("category", ""),
            grading_type=metadata.get("grading_type", "automated"),
            timeout_seconds=metadata.get("timeout_seconds", 120),
            workspace_files=metadata.get("workspace_files", []),
            prompt=sections.get("Prompt", "").strip(),
            expected_behavior=sections.get("Expected Behavior", "").strip(),
            grading_criteria=grading_criteria,
            automated_checks=sections.get("Automated Checks", None),
            llm_judge_rubric=sections.get("LLM Judge Rubric", None),
            grading_weights=metadata.get("grading_weights", None),
            file_path=task_file,
            frontmatter=metadata,
            sub_problems=sub_problems,
            skill_category=metadata.get("skill_category", None),
        )

        return task

    def _parse_sections(self, body: str) -> Dict[str, str]:
        sections = {}
        current_section = None
        current_content = []

        for line in body.split("\n"):
            header_match = re.match(r"^##\s+(.+)$", line)
            if header_match:
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = header_match.group(1)
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _extract_grading_criteria(self, criteria_text: str) -> List[str]:
        criteria = []
        for line in criteria_text.split("\n"):
            match = re.match(r"^-\s+\[[ x]\]\s+(.+)$", line.strip())
            if match:
                criteria.append(match.group(1))
        return criteria

    def _extract_sub_problems(self, sub_problems_text: str) -> List[SubProblem]:
        if not sub_problems_text.strip():
            return []

        sub_problems = []
        current_title = None
        current_content = []
        current_index = 0

        for line in sub_problems_text.split("\n"):
            header_match = re.match(r"^###\s+Sub-Problem\s+(\d+):\s*(.+)$", line)
            if header_match:
                if current_title is not None:
                    sub_problems.append(
                        SubProblem(
                            index=current_index,
                            title=current_title,
                            description="\n".join(current_content).strip(),
                        )
                    )
                current_index = int(header_match.group(1))
                current_title = header_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        if current_title is not None:
            sub_problems.append(
                SubProblem(
                    index=current_index,
                    title=current_title,
                    description="\n".join(current_content).strip(),
                )
            )

        return sub_problems
