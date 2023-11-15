import logging
from unittest import mock
import click
from click.testing import CliRunner
from monic.core.app import App
from monic.core.monitor import Monitor
from monic.cli.create import create

def test_create():
    runner = CliRunner()
    test_args = [
        '--id', 'test-id',
        '--name', 'test-name',
        '--endpoint', 'test-endpoint',
        '--interval', '120',
        '--body-regexp', 'test-regexp',
    ]

    with mock.patch.object(logging, 'getLogger') as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, 'create_monitor') as create_monitor_mock:
            create_monitor_mock.return_value = Monitor(
                mid='test-id',
                name='test-name',
                endpoint='test-endpoint',
                interval=120,
                body_regexp='test-regexp',
            )

            result = runner.invoke(create, test_args)
            assert create_monitor_mock.called_once()
            assert result.exit_code == 0
            assert result.output == "Added monitor test-name for \"https://test-endpoint\" every 120 seconds\n"
