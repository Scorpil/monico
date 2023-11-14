import pytest
from monic.core.monitor import Monitor, MonitorAttributeError


def test_repr():
    monitor = Monitor("foo", "Foo", "https://example.com")
    assert repr(monitor) == "<Monitor foo (Foo)>"


def test_create_task():
    task = Monitor("foo", "Foo", "https://example.com").create_task()
    assert task.monitor_id == "foo"


def test_preprocess_id():
    assert Monitor.preprocess_id("foo") == "foo"
    assert Monitor.preprocess_id("a" * 128) == "a" * 128


def test_preprocess_id_raises():
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_id("")
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_id("a" * 129)


def test_preprocess_name():
    assert Monitor.preprocess_name("Foo") == "Foo"


def test_preprocess_name_raises():
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_name("")
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_name("a" * 65)


def test_preprocess_preprocess_endpoint():
    assert Monitor.preprocess_endpoint("https://example.com") == "https://example.com"
    assert Monitor.preprocess_endpoint("https://example.com/") == "https://example.com/"
    assert (
        Monitor.preprocess_endpoint("https://example.com/foo")
        == "https://example.com/foo"
    )
    assert (
        Monitor.preprocess_endpoint("https://example.com:1313/foo")
        == "https://example.com:1313/foo"
    )


def test_preprocess_endpoint_raises_for_invalid_url():
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_endpoint("https://cannot contain spaces.com")
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_endpoint("https://!-not-allowed.com")
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_endpoint("")


def test_preprocess_interval():
    assert Monitor.preprocess_interval(5) == 5
    assert Monitor.preprocess_interval(300) == 300


def test_preprocess_interval_raises():
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_interval(-1)
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_interval(0)
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_interval(4)
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_interval(301)


def test_preprocess_body_regexp():
    assert Monitor.preprocess_body_regexp(None) is None
    assert Monitor.preprocess_body_regexp("") == ""
    assert Monitor.preprocess_body_regexp(".*") == ".*"


def test_preprocess_body_regexp_raises_for_invalid_regexp():
    with pytest.raises(MonitorAttributeError):
        Monitor.preprocess_body_regexp("[")
