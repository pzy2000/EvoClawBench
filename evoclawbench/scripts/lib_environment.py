"""
Environment abstraction layer for EvoClawBench.

Provides isolated execution environments (Local, Docker) for running agent tasks.
Following the mini-swe-agent patterns for containerized evaluation.
"""

from __future__ import annotations

import os
import platform
import shlex
import subprocess
import uuid
from typing import Any

from pydantic import BaseModel


COMMON_API_ENV_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_BASE_URL",
    "ANTHROPIC_BASE_URL",
    "OPENROUTER_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
]


class EnvironmentConfig(BaseModel):
    environment_class: str = "local"
    image: str | None = None


class DockerEnvironmentConfig(BaseModel):
    image: str
    cwd: str = "/"
    env: dict[str, str] = {}
    forward_env: list[str] = list(COMMON_API_ENV_VARS)
    timeout: int = 30
    executable: str = os.getenv("EVOCLAW_DOCKER_EXECUTABLE", "docker")
    run_args: list[str] = ["--rm"]
    container_timeout: str = "2h"
    pull_timeout: int = 120
    interpreter: list[str] = ["bash", "-lc"]


class LocalEnvironmentConfig(BaseModel):
    pass


class Environment:
    config: Any
    container_id: str | None = None

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        raise NotImplementedError

    def serialize(self) -> dict:
        raise NotImplementedError

    def cleanup(self) -> None:
        pass


class LocalEnvironment(Environment):
    def __init__(
        self,
        *,
        cwd: str = "",
        env: dict[str, str] | None = None,
        forward_env: list[str] | None = None,
        timeout: int = 30,
        **kwargs,
    ):
        self.config = LocalEnvironmentConfig()
        self.cwd = cwd
        self.env = env or {}
        self.forward_env = forward_env or []
        self.timeout = timeout

    def execute(
        self,
        action: dict,
        cwd: str | None = None,
        *,
        timeout: int | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        command = action.get("command", "")
        resolved_cwd = cwd if cwd is not None else self.cwd
        resolved_cwd = resolved_cwd if resolved_cwd else None
        timeout = timeout or self.timeout

        cmd = ["/bin/bash", "-c", command]

        merged_env = os.environ.copy()
        for key in self.forward_env:
            if (value := os.getenv(key)) is not None:
                merged_env[key] = value
        for key, value in self.env.items():
            merged_env[key] = value
        if extra_env:
            for key, value in extra_env.items():
                merged_env[key] = value

        try:
            result = subprocess.run(
                cmd,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=resolved_cwd,
                env=merged_env,
            )
            return {
                "output": result.stdout,
                "returncode": result.returncode,
                "exception_info": "",
            }
        except subprocess.TimeoutExpired as exc:
            raw_output = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
            return {
                "output": raw_output,
                "returncode": -1,
                "exception_info": f"Command timed out after {timeout} seconds",
            }
        except Exception as exc:
            return {
                "output": "",
                "returncode": -1,
                "exception_info": f"An error occurred while executing the command: {exc}",
            }

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return {
            "platform": platform.uname()._asdict(),
            "python_version": platform.python_version(),
            **kwargs,
        }

    def serialize(self) -> dict:
        return {
            "info": {
                "config": {
                    "environment_class": "local",
                    "cwd": self.cwd,
                    "env": self.env,
                    "timeout": self.timeout,
                }
            }
        }


class DockerEnvironment(Environment):
    def __init__(
        self,
        *,
        config_class: type = DockerEnvironmentConfig,
        logger: Any = None,
        **kwargs,
    ):
        self.logger = logger or __import__("logging").getLogger("evoclawbench.environment")
        self.container_id: str | None = None
        self.config = config_class(**kwargs)
        self._start_container()

    def _start_container(self):
        container_name = f"evoclawbench-{uuid.uuid4().hex[:8]}"
        cmd = [
            self.config.executable,
            "run",
            "-d",
            "--name",
            container_name,
            "-w",
            self.config.cwd,
            *self.config.run_args,
            self.config.image,
            "sleep",
            self.config.container_timeout,
        ]
        self.logger.debug(f"Starting container with command: {shlex.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.config.pull_timeout,
            check=True,
        )
        self.logger.info(f"Started container {container_name} with ID {result.stdout.strip()}")
        self.container_id = result.stdout.strip()

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        command = action.get("command", "")
        cwd = cwd or self.config.cwd
        assert self.container_id, "Container not started"

        cmd = [self.config.executable, "exec", "-w", cwd]
        for key in self.config.forward_env:
            if (value := os.getenv(key)) is not None:
                cmd.extend(["-e", f"{key}={value}"])
        for key, value in self.config.env.items():
            cmd.extend(["-e", f"{key}={value}"])
        cmd.extend([self.container_id, *self.config.interpreter, command])

        try:
            result = subprocess.run(
                cmd,
                text=True,
                timeout=timeout or self.config.timeout,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            return {
                "output": result.stdout,
                "returncode": result.returncode,
                "exception_info": "",
            }
        except subprocess.TimeoutExpired as exc:
            raw_output = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
            timeout_val = timeout or self.config.timeout
            return {
                "output": raw_output,
                "returncode": -1,
                "exception_info": f"Command timed out after {timeout_val} seconds",
            }
        except Exception as exc:
            raw_output = getattr(exc, "output", None)
            raw_output = (
                raw_output.decode("utf-8", errors="replace")
                if isinstance(raw_output, bytes)
                else (raw_output or "")
            )
            return {
                "output": raw_output,
                "returncode": -1,
                "exception_info": f"An error occurred while executing the command: {exc}",
                "extra": {"exception_type": type(exc).__name__, "exception": str(exc)},
            }

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return {
            "platform": platform.uname()._asdict(),
            "python_version": platform.python_version(),
            **kwargs,
        }

    def serialize(self) -> dict:
        return {
            "info": {
                "config": {
                    "environment": self.config.model_dump(mode="json"),
                    "environment_type": f"{self.__class__.__module__}.{self.__class__.__name__}",
                }
            }
        }

    def cleanup(self):
        if getattr(self, "container_id", None) is not None:
            cid = self.container_id
            exe = self.config.executable
            cmd = f"(timeout 60 {exe} stop {cid} || {exe} rm -f {cid}) >/dev/null 2>&1 &"
            subprocess.Popen(cmd, shell=True)

    def __del__(self):
        self.cleanup()


_ENVIRONMENT_MAPPING = {
    "local": "evoclawbench.scripts.lib_environment.LocalEnvironment",
    "docker": "evoclawbench.scripts.lib_environment.DockerEnvironment",
}


def get_environment_class(spec: str):
    full_path = _ENVIRONMENT_MAPPING.get(spec, spec)
    try:
        module_name, class_name = full_path.rsplit(".", 1)
        if module_name.startswith("evoclawbench.scripts."):
            module_name = module_name.replace("evoclawbench.scripts.", "")
            module = __import__(module_name, fromlist=[class_name])
        else:
            module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as e:
        available = list(_ENVIRONMENT_MAPPING.keys())
        msg = f"Unknown environment type: {spec} (resolved to {full_path}, available: {available})"
        raise ValueError(msg) from e


def get_environment(config: dict, **kwargs) -> Environment:
    import copy

    config = copy.deepcopy(config)
    environment_class = config.pop("environment_class", "local")
    env_class = get_environment_class(environment_class)
    return env_class(**config, **kwargs)
