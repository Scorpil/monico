import time
from monic.core.task import Task, TaskStatus


def test_task_create():
    time_tolerance = 5
    test_monitor_id = "test_monitor_id"
    now = int(time.time())
    task = Task.create(test_monitor_id)
    assert isinstance(task.id, str)
    assert abs(task.timestamp - now) < time_tolerance
    assert task.monitor_id == test_monitor_id
    assert task.status is TaskStatus.PENDING
    assert task.completed_at is None


def test_task_abandon():
    task = Task.create("test_monitor_id")
    task.abandon()
    assert task.status is TaskStatus.ABANDONED
