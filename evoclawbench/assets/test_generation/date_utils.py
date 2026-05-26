"""Date and time utility functions."""

import re
from datetime import datetime, timedelta


def parse_relative_date(text: str) -> str:
    """Parse a relative date expression and return an ISO 8601 date string.

    Supported expressions (case-insensitive):
    - "today" -> today's date
    - "yesterday" -> yesterday's date
    - "tomorrow" -> tomorrow's date
    - "N days ago" -> N days before today
    - "N days from now" / "in N days" -> N days after today
    - "last week" -> 7 days ago
    - "next week" -> 7 days from now

    Returns the date as YYYY-MM-DD.
    Raises ValueError for unrecognized expressions.
    """
    text = text.strip().lower()
    today = datetime.now().date()

    if text == "today":
        return today.isoformat()
    elif text == "yesterday":
        return (today - timedelta(days=1)).isoformat()
    elif text == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    elif text == "last week":
        return (today - timedelta(weeks=1)).isoformat()
    elif text == "next week":
        return (today + timedelta(weeks=1)).isoformat()

    # "N days ago"
    match = re.match(r"(\d+)\s+days?\s+ago", text)
    if match:
        days = int(match.group(1))
        return (today - timedelta(days=days)).isoformat()

    # "in N days" or "N days from now"
    match = re.match(r"in\s+(\d+)\s+days?", text)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).isoformat()

    match = re.match(r"(\d+)\s+days?\s+from\s+now", text)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).isoformat()

    raise ValueError(f"Unrecognized relative date expression: '{text}'")


def business_days_between(start: str, end: str) -> int:
    """Count business days (Mon-Fri) between two dates, exclusive of both endpoints.

    Dates should be in YYYY-MM-DD format.
    If start == end, returns 0.
    If start > end, returns a negative count.

    Raises ValueError for invalid date formats.
    """
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    if start_date == end_date:
        return 0

    sign = 1
    if start_date > end_date:
        start_date, end_date = end_date, start_date
        sign = -1

    count = 0
    current = start_date + timedelta(days=1)
    while current < end_date:
        if current.weekday() < 5:  # Monday=0, Friday=4
            count += 1
        current += timedelta(days=1)

    return count * sign


def format_duration(seconds: int) -> str:
    """Format a duration in seconds into a human-readable string.

    Examples:
        0 -> "0 seconds"
        1 -> "1 second"
        65 -> "1 minute, 5 seconds"
        3661 -> "1 hour, 1 minute, 1 second"
        90061 -> "1 day, 1 hour, 1 minute, 1 second"

    Raises ValueError if seconds is negative.
    """
    if seconds < 0:
        raise ValueError("Duration cannot be negative")

    if seconds == 0:
        return "0 seconds"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if secs:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")

    return ", ".join(parts)
