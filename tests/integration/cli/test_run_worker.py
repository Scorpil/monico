import logging
from unittest import mock
from click.testing import CliRunner
from monic.core.app import App
from monic.cli.run_worker import run_worker

def test_run_worker():
    runner = CliRunner()
    test_args = [
        "--id", "test-worker-id",
    ]

    with mock.patch.object(logging, 'getLogger') as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, 'run_worker') as run_worker_mock:
            result = runner.invoke(run_worker, test_args)
            assert run_worker_mock.called_once_with("test-worker-id")
            assert result.exit_code == 0
            assert result.output == ""
