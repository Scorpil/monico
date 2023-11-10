from monic.utils import is_valid_url


def test_is_valid_returns_true_for_valid_url():
    assert is_valid_url("https://example.com")
    assert is_valid_url("https://example.com/")
    assert is_valid_url("https://example.com/foo")


def test_is_valid_returns_false_for_invalid_url():
    assert not is_valid_url("https://cannot contain spaces.com")
    assert not is_valid_url("https://!-not-allowed.com")
    assert not is_valid_url("ftp://example.com/")
    assert not is_valid_url("example.com")
