import tempfile
import os
from monico.config import Config


def test_repr():
    config = Config(postgres_uri="postgres://localhost/monico", log_level="DEBUG")
    assert (
        repr(config)
        == "<Config postgres_uri=postgres://localhost/monico log_level=DEBUG>"
    )


def test_from_config_file():
    # write config to temp dir
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'postgres_uri = "postgres://localhost/monico"\n')
        f.write(b'log_level = "DEBUG"\n')
        f.seek(0)

        config = Config.build()
        config.CONFIG_FILE_LOCATIONS = [f.name]
        config.load_from_config_file()
        assert config.postgres_uri == "postgres://localhost/monico"
        assert config.log_level == "DEBUG"


def test_load_from_env():
    config = Config.build()
    test_env = {
        "MONICO_POSTGRES_URI": "postgres://test",
        "MONICO_LOG_LEVEL": "DEBUG",
    }
    config.load_from_env(environment=test_env)
    assert config.postgres_uri == test_env["MONICO_POSTGRES_URI"]
    assert config.log_level == test_env["MONICO_LOG_LEVEL"]
