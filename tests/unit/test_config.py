import tempfile
import os
from monic.config import Config


def test_repr():
    config = Config(postgres_uri="postgres://localhost/monic", log_level="DEBUG")
    assert (
        repr(config)
        == "<Config postgres_uri=postgres://localhost/monic log_level=DEBUG>"
    )


def test_from_config_file():
    # write config to temp dir
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'postgres_uri = "postgres://localhost/monic"\n')
        f.write(b'log_level = "DEBUG"\n')
        f.seek(0)

        config = Config.build()
        config.CONFIG_FILE_LOCATIONS = [f.name]
        config.load_from_config_file()
        assert config.postgres_uri == "postgres://localhost/monic"
        assert config.log_level == "DEBUG"


def test_load_from_env():
    config = Config.build()
    test_env = {
        "MONIC_POSTGRES_URI": "postgres://test",
        "MONIC_LOG_LEVEL": "DEBUG",
    }
    config.load_from_env(environment=test_env)
    assert config.postgres_uri == test_env["MONIC_POSTGRES_URI"]
    assert config.log_level == test_env["MONIC_LOG_LEVEL"]
