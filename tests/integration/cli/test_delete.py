import logging
from unittest import mock
import click
from click.testing import CliRunner
from monic.core.app import App
from monic.core.monitor import Monitor
from monic.cli.delete import delete

def test_delete():
    runner = CliRunner()
    test_args = [
        '--id', 'test-id',
    ]

    with mock.patch.object(logging, 'getLogger') as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, 'delete_monitor') as delete_monitor_mock:
            delete_monitor_mock.return_value = Monitor(
                mid='test-id',
                name='test-name',
                endpoint='test-endpoint',
                interval=120,
                body_regexp='test-regexp',
            )

            result = runner.invoke(delete, test_args)
            assert delete_monitor_mock.called_once()
            assert result.exit_code == 0
            assert result.output == "Removed monitor test-id\n"
