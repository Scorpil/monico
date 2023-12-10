import time
from monico.core.probe import Probe


def test_probe_create():
    time_tolerance = 5

    test_monitor_id = "test_monitor_id"
    test_task_id = "test_task_id"
    test_response_time = 0.1
    test_response_code = 200
    test_response_error = "test_response_error"
    test_content_match = "test_content_match"

    now = int(time.time())
    probe = Probe.create(
        monitor_id=test_monitor_id,
        task_id=test_task_id,
        response_time=test_response_time,
        response_code=test_response_code,
        response_error=test_response_error,
        content_match=test_content_match,
    )

    assert isinstance(probe.id, str)
    assert abs(probe.timestamp - now) < time_tolerance
    assert probe.monitor_id == test_monitor_id
    assert probe.task_id == test_task_id
    assert probe.response_time == test_response_time
    assert probe.response_code == test_response_code
    assert probe.response_error == test_response_error
    assert probe.content_match == test_content_match
