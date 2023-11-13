import pytest
from monic.utils import (
    is_valid_url,
    seconds_to_human_readable_string,
    timestamp_to_human_readable_string,
)


def test_is_valid_returns_true_for_valid_url():
    assert is_valid_url("https://example.com")
    assert is_valid_url("https://example.com/")
    assert is_valid_url("https://example.com:1313/foo")
    assert is_valid_url("https://example.com/foo")


def test_is_valid_returns_false_for_invalid_url():
    assert not is_valid_url("https://cannot contain spaces.com")
    assert not is_valid_url("https://!-not-allowed.com")
    assert not is_valid_url("ftp://example.com/")
    assert not is_valid_url("example.com")
    assert not is_valid_url("example")


def test_seconds_to_human_readable_string_raises_for_negative_seconds():
    with pytest.raises(ValueError):
        seconds_to_human_readable_string(-1)


def test_seconds_to_human_readable_string_ints():
    assert seconds_to_human_readable_string(0) == "0 seconds"
    assert seconds_to_human_readable_string(1) == "1 second"
    assert seconds_to_human_readable_string(2) == "2 seconds"
    assert seconds_to_human_readable_string(59) == "59 seconds"
    assert seconds_to_human_readable_string(60) == "1 minute"
    assert seconds_to_human_readable_string(61) == "1 minute 1 second"
    assert seconds_to_human_readable_string(122) == "2 minutes 2 seconds"


def test_seconds_to_human_readable_string_floats():
    assert seconds_to_human_readable_string(0.0) == "0.00 seconds"
    assert seconds_to_human_readable_string(1.0) == "1.00 second"
    assert seconds_to_human_readable_string(1.1) == "1.10 seconds"
    assert seconds_to_human_readable_string(1.12) == "1.12 seconds"


def test_timestamp_to_human_readable_string():
    assert timestamp_to_human_readable_string(1620000000) == "2021-05-03 02:00:00"
