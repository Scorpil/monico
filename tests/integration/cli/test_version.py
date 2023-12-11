import toml
from click.testing import CliRunner
from monico.cli import cli


def test_version_matches_pyproject_toml():
    with open("./pyproject.toml") as f:
        file_config = toml.load(f)
        version_in_pyproject_toml = file_config["project"]["version"]

    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == version_in_pyproject_toml
