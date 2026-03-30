"""Data structure utility functions."""

from copy import deepcopy


def flatten_dict(d: dict, prefix: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary into a single-level dictionary.

    Keys are joined with the separator. For example:
        {"a": {"b": 1, "c": {"d": 2}}} -> {"a.b": 1, "a.c.d": 2}

    Non-dict values are kept as-is (including lists).
    """
    items = {}
    for key, value in d.items():
        new_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep))
        else:
            items[new_key] = value
    return items


def chunk_list(lst: list, size: int) -> list[list]:
    """Split a list into chunks of the given size.

    The last chunk may be smaller than size.
    Raises ValueError if size is less than 1.
    Returns an empty list if the input list is empty.
    """
    if size < 1:
        raise ValueError("Chunk size must be at least 1")
    if not lst:
        return []
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Deep merge dict2 into dict1, returning a new dictionary.

    - If both values for a key are dicts, merge them recursively.
    - Otherwise, dict2's value takes precedence.
    - Neither input dict is modified.
    """
    result = deepcopy(dict1)
    for key, value in dict2.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result
