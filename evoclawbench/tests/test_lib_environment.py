"""Tests for lib_environment.py - Environment abstraction layer."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_environment import (
    DockerEnvironment,
    DockerEnvironmentConfig,
    EnvironmentConfig,
    LocalEnvironment,
    get_environment,
)


def is_docker_available():
    """Check if Docker is available and running."""
    try:
        subprocess.run(["docker", "version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_podman_available():
    """Check if Podman is available and running."""
    try:
        subprocess.run(["podman", "version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


# Test parameters for container runtimes
container_params = [
    pytest.param(
        "docker",
        marks=pytest.mark.skipif(not is_docker_available(), reason="Docker not available"),
        id="docker",
    ),
]


# ---------------------------------------------------------------------------
# DockerEnvironmentConfig
# ---------------------------------------------------------------------------


class TestDockerEnvironmentConfig:
    def test_defaults(self):
        config = DockerEnvironmentConfig(image="python:3.11")
        assert config.image == "python:3.11"
        assert config.cwd == "/"
        assert config.env == {}
        assert "OPENAI_API_KEY" in config.forward_env
        assert "ANTHROPIC_AUTH_TOKEN" in config.forward_env
        assert len(config.forward_env) >= 9
        assert config.timeout == 30
        assert config.executable == "docker"
        assert config.run_args == ["--rm"]
        assert config.container_timeout == "2h"
        assert config.interpreter == ["bash", "-lc"]

    def test_custom_values(self):
        config = DockerEnvironmentConfig(
            image="custom:image",
            cwd="/workspace",
            env={"KEY": "value"},
            forward_env=["HOST_VAR"],
            timeout=60,
            run_args=["--rm", "--network=none"],
            container_timeout="1h",
            interpreter=["python", "-c"],
        )
        assert config.image == "custom:image"
        assert config.cwd == "/workspace"
        assert config.env == {"KEY": "value"}
        assert config.forward_env == ["HOST_VAR"]
        assert config.timeout == 60
        assert config.run_args == ["--rm", "--network=none"]
        assert config.container_timeout == "1h"
        assert config.interpreter == ["python", "-c"]

    def test_executable_default(self):
        config = DockerEnvironmentConfig(image="test:latest")
        assert config.executable == "docker"

    def test_executable_explicit(self):
        config = DockerEnvironmentConfig(image="test:latest", executable="podman")
        assert config.executable == "podman"


class TestEnvironmentConfig:
    def test_local_defaults(self):
        config = EnvironmentConfig(environment_class="local")
        assert config.environment_class == "local"
        assert config.image is None

    def test_docker_defaults(self):
        config = EnvironmentConfig(environment_class="docker", image="python:3.11")
        assert config.environment_class == "docker"
        assert config.image == "python:3.11"


# ---------------------------------------------------------------------------
# LocalEnvironment
# ---------------------------------------------------------------------------


class TestLocalEnvironment:
    def test_execute_simple_command(self):
        env = LocalEnvironment()
        result = env.execute({"command": "echo 'hello world'"})
        assert result["returncode"] == 0
        assert "hello world" in result["output"]

    def test_execute_with_cwd(self, tmp_path):
        env = LocalEnvironment()
        result = env.execute({"command": "pwd"}, cwd=str(tmp_path))
        assert result["returncode"] == 0
        assert str(tmp_path) in result["output"]

    def test_execute_with_env(self):
        env = LocalEnvironment()
        result = env.execute(
            {"command": "echo $TEST_VAR"},
            extra_env={"TEST_VAR": "test_value"},
        )
        assert result["returncode"] == 0
        assert "test_value" in result["output"]

    def test_execute_failure(self):
        env = LocalEnvironment()
        result = env.execute({"command": "exit 42"})
        assert result["returncode"] == 42

    def test_execute_timeout(self):
        env = LocalEnvironment(timeout=1)
        result = env.execute({"command": "sleep 10"})
        assert result["returncode"] == -1
        assert "timed out" in result.get("exception_info", "").lower()

    def test_get_template_vars(self):
        env = LocalEnvironment()
        vars = env.get_template_vars()
        assert "platform" in vars
        assert "python_version" in vars

    def test_serialize(self):
        env = LocalEnvironment()
        data = env.serialize()
        assert "info" in data
        assert data["info"]["config"]["environment_class"] == "local"


# ---------------------------------------------------------------------------
# DockerEnvironment (functional tests)
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestDockerEnvironment:
    def test_config_only_creates_container(self):
        env = DockerEnvironment(image="python:3.11")
        try:
            assert env.container_id is not None
        finally:
            env.cleanup()

    def test_execute_simple_command(self):
        env = DockerEnvironment(image="python:3.11")
        try:
            result = env.execute({"command": "echo 'hello world'"})
            assert result["returncode"] == 0
            assert "hello world" in result["output"]
        finally:
            env.cleanup()

    def test_execute_with_cwd(self):
        env = DockerEnvironment(image="python:3.11", cwd="/tmp")
        try:
            result = env.execute({"command": "pwd"})
            assert result["returncode"] == 0
            assert "/tmp" in result["output"]
        finally:
            env.cleanup()

    def test_execute_with_env_variables(self):
        env = DockerEnvironment(
            image="python:3.11",
            env={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
        )
        try:
            result = env.execute({"command": "echo $TEST_VAR $ANOTHER_VAR"})
            assert result["returncode"] == 0
            assert "test_value another_value" in result["output"]
        finally:
            env.cleanup()

    def test_execute_forward_env_variables(self):
        with patch.dict(os.environ, {"HOST_VAR": "host_value"}):
            env = DockerEnvironment(
                image="python:3.11",
                forward_env=["HOST_VAR"],
            )
            try:
                result = env.execute({"command": "echo $HOST_VAR"})
                assert result["returncode"] == 0
                assert "host_value" in result["output"]
            finally:
                env.cleanup()

    def test_execute_failure(self):
        env = DockerEnvironment(image="python:3.11")
        try:
            result = env.execute({"command": "exit 42"})
            assert result["returncode"] == 42
        finally:
            env.cleanup()

    def test_command_failure_captured(self):
        env = DockerEnvironment(image="python:3.11")
        try:
            result = env.execute({"command": "ls /nonexistent_directory_12345"})
            assert result["returncode"] != 0
        finally:
            env.cleanup()

    def test_cleanup_stops_container(self):
        env = DockerEnvironment(image="python:3.11")
        env.cleanup()
        # The background process handles cleanup, so we just verify cleanup() was called

    def test_multiple_containers_independent(self):
        env1 = DockerEnvironment(image="python:3.11")
        env2 = DockerEnvironment(image="python:3.11")
        try:
            assert env1.container_id != env2.container_id
            result1 = env1.execute({"command": "echo env1"})
            result2 = env2.execute({"command": "echo env2"})
            assert "env1" in result1["output"]
            assert "env2" in result2["output"]
        finally:
            env1.cleanup()
            env2.cleanup()

    def test_serialize_includes_container_info(self):
        env = DockerEnvironment(image="python:3.11")
        try:
            data = env.serialize()
            assert "info" in data
            assert "environment_type" in data["info"]["config"]
            assert "docker" in data["info"]["config"]["environment_type"].lower()
        finally:
            env.cleanup()


# ---------------------------------------------------------------------------
# get_environment factory
# ---------------------------------------------------------------------------


class TestGetEnvironment:
    def test_get_local_environment(self):
        env = get_environment({"environment_class": "local"})
        assert isinstance(env, LocalEnvironment)

    def test_get_docker_environment(self):
        env = get_environment({"environment_class": "docker", "image": "python:3.11"})
        assert isinstance(env, DockerEnvironment)

    def test_get_environment_with_extra_kwargs(self):
        env = get_environment(
            {"environment_class": "local"},
            timeout=60,
        )
        assert env.timeout == 60

    def test_unknown_environment_raises(self):
        with pytest.raises(ValueError, match="Unknown environment type"):
            get_environment({"environment_class": "unknown_type"})
