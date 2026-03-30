"""Validation utility functions."""

import re


def validate_email(email: str) -> bool:
    """Validate an email address format.

    Checks for:
    - Non-empty local part and domain
    - Valid characters in local part (alphanumeric, dots, underscores, hyphens, plus)
    - Domain has at least one dot
    - TLD is at least 2 characters
    - No consecutive dots in local part
    - Local part doesn't start or end with a dot

    This is a format check only, not a deliverability check.
    """
    if not isinstance(email, str) or not email:
        return False

    pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False

    local_part = email.split("@")[0]
    if ".." in local_part:
        return False

    return True


def validate_url(url: str) -> bool:
    """Validate a URL format.

    Checks for:
    - Scheme must be http or https
    - Host must be present
    - Valid characters in host
    - Port (if present) must be a valid number (1-65535)
    - Path, query, and fragment are optional

    This is a format check only, not a reachability check.
    """
    if not isinstance(url, str) or not url:
        return False

    pattern = (
        r"^https?://"                # scheme
        r"([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)*"  # subdomains
        r"[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"        # domain
        r"(\.[a-zA-Z]{2,})?"         # TLD (optional for localhost)
        r"(:\d{1,5})?"               # port
        r"(/[^\s]*)?"                 # path, query, fragment
        r"$"
    )

    if not re.match(pattern, url):
        return False

    # Validate port range if present
    port_match = re.search(r":(\d{1,5})(?=/|$|\?|#)", url.split("//", 1)[1] if "//" in url else url)
    if port_match:
        port = int(port_match.group(1))
        if port < 1 or port > 65535:
            return False

    return True


def validate_phone(phone: str, country: str = "US") -> bool:
    """Validate a phone number format for the given country.

    Supported countries and their formats:
    - US: +1XXXXXXXXXX, 1XXXXXXXXXX, (XXX) XXX-XXXX, XXX-XXX-XXXX
    - UK: +44XXXXXXXXXX, 0XXXXXXXXXXX (10-11 digits after 0)
    - DE: +49XXXXXXXXXXX (10-12 digits after +49)
    - IN: +91XXXXXXXXXX, 0XXXXXXXXXX (10 digits)

    Returns False for unsupported countries.
    """
    if not isinstance(phone, str) or not phone:
        return False

    # Remove spaces
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    country = country.upper()

    if country == "US":
        # Match: +1XXXXXXXXXX or 1XXXXXXXXXX or XXXXXXXXXX
        pattern = r"^(\+?1)?[2-9]\d{2}[2-9]\d{6}$"
        return bool(re.match(pattern, cleaned))

    elif country == "UK":
        # Match: +44... or 0...
        pattern = r"^(\+44|0)[1-9]\d{8,9}$"
        return bool(re.match(pattern, cleaned))

    elif country == "DE":
        # Match: +49... or 0...
        pattern = r"^(\+49|0)[1-9]\d{9,11}$"
        return bool(re.match(pattern, cleaned))

    elif country == "IN":
        # Match: +91... or 0...
        pattern = r"^(\+91|0)?[6-9]\d{9}$"
        return bool(re.match(pattern, cleaned))

    return False
