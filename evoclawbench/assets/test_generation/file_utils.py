"""File utility functions."""

import hashlib
import json
import os
from fnmatch import fnmatch
from pathlib import Path


def safe_read_json(path: str, default=None) -> dict:
    """Safely read a JSON file, returning default on any failure.

    Returns the parsed JSON content (expected to be a dict).
    If the file doesn't exist, is not valid JSON, or any other error
    occurs, returns the default value (None if not specified).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError, PermissionError,
            IsADirectoryError, OSError, TypeError, UnicodeDecodeError):
        return default


def find_files(directory: str, pattern: str) -> list[str]:
    """Recursively find files matching a glob-like pattern in a directory.

    Args:
        directory: Root directory to search.
        pattern: Glob-like pattern (e.g., "*.py", "test_*", "*.json").

    Returns:
        A sorted list of absolute file paths matching the pattern.
        Returns an empty list if the directory doesn't exist.
    """
    result = []
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return result

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if fnmatch(filename, pattern):
                result.append(os.path.abspath(os.path.join(root, filename)))

    return sorted(result)


def file_checksum(path: str, algorithm: str = "sha256") -> str:
    """Compute the hex digest checksum of a file.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm to use (default: "sha256").
            Supported: "md5", "sha1", "sha256", "sha512".

    Returns:
        The hex digest string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the algorithm is not supported.
    """
    supported = {"md5", "sha1", "sha256", "sha512"}
    if algorithm not in supported:
        raise ValueError(
            f"Unsupported algorithm '{algorithm}'. Choose from: {supported}"
        )

    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
