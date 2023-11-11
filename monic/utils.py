import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Performs a basic check to ensure the string is URL-shaped.
    Note: this is a relatively heavy operation, so it should be used sparingly.
    """
    try:
        result = urlparse(url)
        if result.scheme not in ["http", "https"]:
            return False

        # this is a very basic check, but it should be enough to catch typos
        return re.match(r"^([a-z0-9-]+\.?)+$", result.netloc, re.IGNORECASE)
    except ValueError:
        return False


def seconds_to_human_readable_string(seconds: int) -> str:
    """
    Converts a number of seconds to a human-readable string.
    """
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    seconds_remainder = seconds % 60

    minute_string = f"{minutes} minute"
    if minutes > 1:
        minute_string += "s"  # pluralize

    if seconds_remainder == 0:
        return minute_string
    return f"{minute_string} {seconds_remainder} seconds"
