import logging
from unittest import mock
from click.testing import CliRunner
from monico.core.app import App
from monico.cli.run_manager import run_manager


def test_run_manager():
    runner = CliRunner()
    test_args = []

    with mock.patch.object(logging, "getLogger") as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, "run_manager") as run_manager_mock:
            result = runner.invoke(run_manager, test_args)
            assert run_manager_mock.called_once()
            assert result.exit_code == 0
            assert result.output == ""
