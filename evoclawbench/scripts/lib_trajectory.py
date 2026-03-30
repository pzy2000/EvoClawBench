"""Trajectory recording for EvoClawBench agent execution.

Records the complete execution path of an agent, including:
- Transcript (agent-LLM conversation)
- Workspace file changes
- Grading execution details
- Errors and debugging information
"""

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ExecutionInfo:
    """Information about the execution environment."""

    agent_id: str
    model_id: str
    runtime: str
    workspace: str
    status: str  # success, error, timeout
    exit_code: int
    timed_out: bool
    execution_time: float


@dataclass
class WorkspaceFile:
    """Information about a file in the workspace."""

    path: str
    exists: bool
    size_bytes: Optional[int] = None
    content_preview: Optional[str] = None
    error: Optional[str] = None


@dataclass
class GradingInfo:
    """Information about the grading process."""

    function_executed: bool
    execution_time: float
    input_shape: Dict[str, Any]
    output: Dict[str, float]
    error: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ExecutionError:
    """An error that occurred during execution."""

    error_type: str
    message: str
    timestamp: float
    component: str  # "agent", "grading", "workspace", etc.


@dataclass
class Trajectory:
    """Complete execution trajectory for a task run."""

    task_id: str
    mode: str  # baseline, evolution, bench
    run_number: int
    start_time: float
    end_time: float
    execution: ExecutionInfo
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    workspace_files: List[WorkspaceFile] = field(default_factory=list)
    grading: Optional[GradingInfo] = None
    errors: List[ExecutionError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def duration_seconds(self) -> float:
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "mode": self.mode,
            "run_number": self.run_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds(),
            "execution": asdict(self.execution),
            "transcript": self.transcript,
            "workspace_files": [asdict(f) for f in self.workspace_files],
            "grading": asdict(self.grading) if self.grading else None,
            "errors": [asdict(e) for e in self.errors],
            "metadata": self.metadata,
        }


class TrajectoryRecorder:
    """Records execution trajectories for debugging and analysis."""

    def __init__(self):
        self.current_trajectory: Optional[Trajectory] = None
        self.trajectories: List[Trajectory] = []

    def start_recording(
        self,
        task_id: str,
        mode: str,
        run_number: int,
        agent_id: str,
        model_id: str,
        runtime: str,
        workspace: str,
    ) -> None:
        """Start recording a new trajectory."""
        self.current_trajectory = Trajectory(
            task_id=task_id,
            mode=mode,
            run_number=run_number,
            start_time=time.time(),
            end_time=0.0,
            execution=ExecutionInfo(
                agent_id=agent_id,
                model_id=model_id,
                runtime=runtime,
                workspace=workspace,
                status="pending",
                exit_code=-1,
                timed_out=False,
                execution_time=0.0,
            ),
        )
        logger.debug(f"Started recording trajectory: {task_id} (mode={mode}, run={run_number})")

    def end_recording(
        self, status: str, exit_code: int, timed_out: bool, execution_time: float
    ) -> Trajectory:
        """End recording and finalize the trajectory."""
        if not self.current_trajectory:
            raise RuntimeError("No trajectory currently being recorded")

        self.current_trajectory.end_time = time.time()
        self.current_trajectory.execution.status = status
        self.current_trajectory.execution.exit_code = exit_code
        self.current_trajectory.execution.timed_out = timed_out
        self.current_trajectory.execution.execution_time = execution_time

        self.trajectories.append(self.current_trajectory)
        trajectory = self.current_trajectory
        self.current_trajectory = None

        logger.debug(f"Ended recording: {trajectory.task_id} (status={status})")
        return trajectory

    def record_transcript(self, transcript: List[Dict[str, Any]]) -> None:
        """Record the full transcript."""
        if not self.current_trajectory:
            return
        self.current_trajectory.transcript = transcript
        logger.debug(f"Recorded {len(transcript)} transcript events")

    def record_workspace_files(self, workspace_path: str, files_to_check: List[str]) -> None:
        """Record files in the workspace."""
        if not self.current_trajectory:
            return

        workspace = Path(workspace_path)
        for file_path in files_to_check:
            full_path = workspace / file_path
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    # Read preview (first 500 chars)
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                    preview = content[:500] if content else ""
                    self.current_trajectory.workspace_files.append(
                        WorkspaceFile(
                            path=file_path,
                            exists=True,
                            size_bytes=size,
                            content_preview=preview,
                        )
                    )
                except Exception as e:
                    self.current_trajectory.workspace_files.append(
                        WorkspaceFile(
                            path=file_path,
                            exists=True,
                            error=f"Failed to read: {str(e)}",
                        )
                    )
            else:
                self.current_trajectory.workspace_files.append(
                    WorkspaceFile(path=file_path, exists=False)
                )

    def record_grading(
        self,
        executed: bool,
        execution_time: float,
        input_shape: Dict[str, Any],
        output: Dict[str, float],
        error: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Record the grading execution."""
        if not self.current_trajectory:
            return

        self.current_trajectory.grading = GradingInfo(
            function_executed=executed,
            execution_time=execution_time,
            input_shape=input_shape,
            output=output,
            error=error,
            notes=notes,
        )
        logger.debug(f"Recorded grading: executed={executed}, error={error}")

    def record_error(
        self,
        error_type: str,
        message: str,
        component: str = "unknown",
    ) -> None:
        """Record an error during execution."""
        if not self.current_trajectory:
            return

        self.current_trajectory.errors.append(
            ExecutionError(
                error_type=error_type,
                message=message,
                timestamp=time.time(),
                component=component,
            )
        )
        logger.debug(f"Recorded error: {error_type} in {component}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set arbitrary metadata."""
        if not self.current_trajectory:
            return
        self.current_trajectory.metadata[key] = value

    def get_current_trajectory(self) -> Optional[Trajectory]:
        """Get the current trajectory being recorded."""
        return self.current_trajectory

    def save_trajectories(self, output_file: Path) -> None:
        """Save all recorded trajectories to a JSON file."""
        data = [t.to_dict() for t in self.trajectories]
        output_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Saved {len(self.trajectories)} trajectories to {output_file}")


# Thread-local recorder storage
_thread_local = threading.local()


def get_recorder() -> TrajectoryRecorder:
    """Get or create a thread-local trajectory recorder."""
    if not hasattr(_thread_local, "recorder"):
        _thread_local.recorder = TrajectoryRecorder()
    return _thread_local.recorder


def start_recording(
    task_id: str,
    mode: str,
    run_number: int,
    agent_id: str,
    model_id: str,
    runtime: str,
    workspace: str,
) -> None:
    """Start recording a trajectory (convenience function)."""
    get_recorder().start_recording(
        task_id, mode, run_number, agent_id, model_id, runtime, workspace
    )


def end_recording(
    status: str, exit_code: int, timed_out: bool, execution_time: float
) -> Trajectory:
    """End recording and finalize (convenience function)."""
    return get_recorder().end_recording(status, exit_code, timed_out, execution_time)


def record_transcript(transcript: List[Dict[str, Any]]) -> None:
    """Record transcript (convenience function)."""
    get_recorder().record_transcript(transcript)


def record_workspace_files(workspace_path: str, files_to_check: List[str]) -> None:
    """Record workspace files (convenience function)."""
    get_recorder().record_workspace_files(workspace_path, files_to_check)


def record_grading(
    executed: bool,
    execution_time: float,
    input_shape: Dict[str, Any],
    output: Dict[str, float],
    error: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """Record grading (convenience function)."""
    get_recorder().record_grading(executed, execution_time, input_shape, output, error, notes)


def record_error(error_type: str, message: str, component: str = "unknown") -> None:
    """Record an error (convenience function)."""
    get_recorder().record_error(error_type, message, component)


def set_metadata(key: str, value: Any) -> None:
    """Set metadata (convenience function)."""
    get_recorder().set_metadata(key, value)


def save_trajectories(output_file: Path) -> None:
    """Save trajectories (convenience function)."""
    get_recorder().save_trajectories(output_file)
