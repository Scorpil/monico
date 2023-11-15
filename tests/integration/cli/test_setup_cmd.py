import logging
from unittest import mock
from click.testing import CliRunner
from monic.core.app import App
from monic.cli.setup import setup as setup_cmd


def test_cli_command():
    runner = CliRunner()

    with mock.patch.object(logging, 'getLogger') as get_logger_mock:
        get_logger_mock.return_value = mock.MagicMock()
        with mock.patch.object(App, 'setup') as setup_mock:
            # Test with --force
            result = runner.invoke(setup_cmd, ["--force"])
            assert setup_mock.call_args_list[0][1]['force']
            assert result.exit_code == 0
            assert result.output == "Initialized the database\n"

            # Test without --force (default)
            result = runner.invoke(setup_cmd, [])
            assert setup_mock.call_args_list[1][1]['force'] is False
            assert result.exit_code == 0
            assert result.output == "Initialized the database\n"
