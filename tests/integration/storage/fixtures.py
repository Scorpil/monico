import pytest
from monico.core.monitor import Monitor


@pytest.fixture(scope="session", autouse=True)
def test_monitor():
    return Monitor(
        mid="test_id",
        name="test_monitor_name",
        endpoint="http://example.com",
        interval=60,
        body_regexp="[a-z]+",
    )
