import pytest
import tempfile
from monico.config import Config, ConfigLoader, ConfigurationError


def test_repr():
    config = Config(postgres_uri="postgres://localhost/monico", log_level="DEBUG")
    assert (
        repr(config)
        == "<Config: sqlite_uri=None, postgres_uri=postgres://localhost/monico, log_level=DEBUG>"
    )


def test_validate_single_storage_backend():
    """Config that only has one storage backend is validated"""
    loader = ConfigLoader()
    test_env = {
        "MONICO_POSTGRES_URI": "postgres://test",
    }
    loader.load_from_env(environment=test_env)
    assert loader.config.postgres_uri.value == test_env["MONICO_POSTGRES_URI"]


def test_validate_single_storage_backend_fail():
    """Config that has more than one storage backend is not validated"""
    loader = ConfigLoader()
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'postgres_uri = "postgres://localhost/monico"\n')
        f.seek(0)

        loader.CONFIG_FILE_LOCATIONS = [f.name]
        loader.load_from_config_file()

    test_env = {
        "MONICO_SQLITE_URI": "sqlite://test",
    }
    loader.load_from_env(environment=test_env)
    expected_error_msg = (
        "Only one storage backend can be used at a time. Found 2:\n"
        "- sqlite_uri: from environment variable MONICO_SQLITE_URI\n"
        f"- postgres_uri: from config file {f.name}, field: postgres_uri\n"
    )
    with pytest.raises(ConfigurationError, match=expected_error_msg):
        loader.validate_single_storage_backend()


def test_validate_log_level_fail():
    """Config that has invalid log level is not validated"""
    loader = ConfigLoader()
    test_env = {
        "MONICO_POSTGRES_URI": "postgres://test",
        "MONICO_LOG_LEVEL": "INVALID",
    }
    loader.load_from_env(environment=test_env)
    expected_error_msg = (
        "Invalid log level: INVALID. Valid values are: DEBUG, INFO, WARNING, ERROR, CRITICAL.\n"
        "Defined in: environment variable MONICO_LOG_LEVEL"
    )
    with pytest.raises(ConfigurationError, match=expected_error_msg):
        loader.validate_log_level()


def test_from_config_file():
    # write config to temp dir
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'postgres_uri = "postgres://localhost/monico"\n')
        f.write(b'log_level = "DEBUG"\n')
        f.seek(0)

        loader = ConfigLoader()
        loader.CONFIG_FILE_LOCATIONS = [f.name]
        loader.load_from_config_file()
        assert loader.config.postgres_uri.value == "postgres://localhost/monico"
        assert loader.config.log_level.value == "DEBUG"


def test_load_from_env():
    loader = ConfigLoader()
    test_env = {
        "MONICO_POSTGRES_URI": "postgres://test",
        "MONICO_LOG_LEVEL": "DEBUG",
    }
    loader.load_from_env(environment=test_env)
    assert loader.config.postgres_uri.value == test_env["MONICO_POSTGRES_URI"]
    assert loader.config.log_level.value == test_env["MONICO_LOG_LEVEL"]
