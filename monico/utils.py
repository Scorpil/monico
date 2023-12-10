import re
import time
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Performs a basic check to ensure the string is URL-shaped.
    Note: this is a relatively heavy operation, so it should be used sparingly.
    """
    result = urlparse(url)
    if not result.netloc:
        return False
    if result.scheme not in ["http", "https"]:
        return False
    # this is a very basic check, but it should be enough to catch typos
    return re.match(r"^([a-z0-9:-]+\.?)+$", result.netloc, re.IGNORECASE)


def _human_readible_seconds(seconds: int | float) -> str:
    postfix = "seconds"
    if seconds == 1:
        postfix = "second"

    if isinstance(seconds, float):
        # always show 2 decimal places
        return f"{seconds:.2f} {postfix}"
    return f"{seconds} {postfix}"


def seconds_to_human_readable_string(seconds: int | float) -> str:
    """
    Converts a number of seconds to a human-readable string.
    """
    if seconds < 0:
        raise ValueError("Seconds cannot be negative")

    if isinstance(seconds, float):
        seconds = round(seconds, 2)

    if seconds < 60:
        return _human_readible_seconds(seconds)

    minutes = seconds // 60
    seconds_remainder = seconds % 60

    minute_string = f"{minutes} minute"
    if minutes > 1:
        minute_string += "s"  # pluralize

    if seconds_remainder == 0:
        return minute_string
    return f"{minute_string} {_human_readible_seconds(seconds_remainder)}"


def timestamp_to_human_readable_string(timestamp: int) -> str:
    """
    Converts a timestamp to a human-readable string.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
