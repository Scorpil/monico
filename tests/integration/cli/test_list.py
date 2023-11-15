import logging
from unittest import mock
import click
from click.testing import CliRunner
from monic.core.app import App
from monic.core.monitor import Monitor
from monic.cli.list import list_monitors


def test_list():
    runner = CliRunner()
    test_args = []

    with mock.patch.object(logging, 'getLogger') as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, 'list_monitors') as list_monitors_mock:
            list_monitors_mock.return_value = [
                Monitor(
                    mid='test-id',
                    name='test-name',
                    endpoint='test-endpoint',
                    interval=120,
                    body_regexp='test-regexp',
                ),
                Monitor(
                    mid='test-id-2',
                    name='test-name-2',
                    endpoint='test-endpoint-2',
                    interval=60,
                    body_regexp='test-regexp-2',
                )
            ]

            result = runner.invoke(list_monitors, test_args)

            expected_output = """\
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID        ┃ Name        ┃ Endpoint                ┃ Interval  ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ test-id   │ test-name   │ https://test-endpoint   │ 2 minutes │
│ test-id-2 │ test-name-2 │ https://test-endpoint-2 │ 1 minute  │
└───────────┴─────────────┴─────────────────────────┴───────────┘
"""
            assert list_monitors_mock.called_once()
            #assert result.exit_code == 0
            assert result.output == expected_output
