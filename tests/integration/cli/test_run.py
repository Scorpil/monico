import logging
from unittest import mock
from click.testing import CliRunner
from monico.core.app import App
from monico.cli.run import run


def test_run():
    runner = CliRunner()
    test_args = [
        "--worker-id",
        "test-worker-id",
    ]

    with mock.patch.object(logging, "getLogger") as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, "run") as run_mock:
            result = runner.invoke(run, test_args)
            assert run_mock.called_once_with("test-worker-id")
            assert result.exit_code == 0
            assert result.output == ""
