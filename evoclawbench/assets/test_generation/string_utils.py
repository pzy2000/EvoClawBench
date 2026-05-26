"""String utility functions."""

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    - Converts to lowercase
    - Replaces spaces and special characters with hyphens
    - Removes non-alphanumeric characters (except hyphens)
    - Collapses multiple hyphens into one
    - Strips leading/trailing hyphens
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    return text


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """Truncate text to max_len characters, appending suffix if truncated.

    - If text is shorter than or equal to max_len, return as-is.
    - If max_len is less than len(suffix), return suffix truncated to max_len.
    - Otherwise, truncate and append suffix so total length equals max_len.
    """
    if len(text) <= max_len:
        return text
    if max_len <= len(suffix):
        return suffix[:max_len]
    return text[: max_len - len(suffix)] + suffix


def extract_emails(text: str) -> list[str]:
    """Extract all email addresses from the given text.

    Returns a list of unique email addresses found, in order of first
    appearance. Uses a simple but practical regex pattern.
    """
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    seen = set()
    result = []
    for match in re.finditer(pattern, text):
        email = match.group().lower()
        if email not in seen:
            seen.add(email)
            result.append(email)
    return result
