import os
import toml
from dataclasses import dataclass, field
from typing import Optional, TypeVar, Generic


T = TypeVar("T")


class ConfigurationError(Exception):
    pass


@dataclass
class EnvironmentVariableConfigSource:
    name: str

    def __str__(self):
        return f"environment variable {self.name}"


@dataclass
class ConfigFileConfigSource:
    location: str
    field: str

    def __str__(self):
        return f"config file {self.location}, field: {self.field}"


@dataclass
class DefaultConfigSource:
    def __str__(self):
        return "default value"


@dataclass
class ConfigValue(Generic[T]):
    value: T
    source: EnvironmentVariableConfigSource | ConfigFileConfigSource


@dataclass
class Config:
    sqlite_uri: Optional[ConfigValue[str]] = None
    postgres_uri: Optional[ConfigValue[str]] = None
    log_level: ConfigValue[str] = field(
        default_factory=lambda: ConfigValue(
            value="WARNING", source=DefaultConfigSource()
        )
    )

    def __repr__(self):
        value_strings = [
            f"{k}={self.__getattribute__(k)}"
            for (k, _) in Config.__annotations__.items()
        ]
        return f"<Config: {', '.join(value_strings)}>"


class ConfigLoader:
    CONFIG_FILE_LOCATIONS = [
        "/etc/monico/.monico.toml",  # System-wide
        "~/.monico/.monico.toml",  # User's home directory
        "./.monico.toml",  # Current working directory
    ]

    # names of fields that are storage backends
    # used to validate that only one storage backend is used
    STORAGE_BACKEND_FIELD_NAMES = [
        "sqlite_uri",
        "postgres_uri",
    ]

    config: Config

    def __init__(self):
        self.config = Config()

    def load(self) -> Config:
        self.load_from_config_file()
        self.load_from_env()
        self.validate_single_storage_backend()
        self.validate_log_level()
        return self.config

    def validate_single_storage_backend(self):
        non_empty_storage_backend_field_names = list(
            filter(
                lambda f: self.config.__getattribute__(f) is not None,
                self.STORAGE_BACKEND_FIELD_NAMES,
            )
        )
        if len(non_empty_storage_backend_field_names) > 1:
            msg = (
                "Only one storage backend can be used at a time. "
                f"Found {len(non_empty_storage_backend_field_names)}:\n"
            )
            for field_name in non_empty_storage_backend_field_names:
                field = self.config.__getattribute__(field_name)
                msg += f"- {field_name}: from {field.source}\n"
            raise ConfigurationError(msg)

    def validate_log_level(self):
        valid_values = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level.value not in valid_values:
            raise ConfigurationError(
                f"Invalid log level: {self.config.log_level.value}. "
                f"Valid values are: {', '.join(valid_values)}.\n"
                f"Defined in: {self.config.log_level.source}"
            )

    def load_from_config_file(self):
        """Builds config from config file"""
        for location in self.CONFIG_FILE_LOCATIONS:
            try:
                expanded_location = os.path.expanduser(location)
                with open(expanded_location) as f:
                    file_config = toml.load(f)

                for field in Config.__annotations__:
                    if field in file_config:
                        value = ConfigValue(
                            value=file_config[field],
                            source=ConfigFileConfigSource(
                                location=expanded_location,
                                field=field,
                            ),
                        )
                        self.config.__setattr__(field, value)
            except FileNotFoundError:
                pass

    def load_from_env(self, environment: dict = os.environ):
        """Builds config from environment variables"""
        for field in Config.__annotations__:
            env_var_name = f"MONICO_{field.upper()}"
            env_value = environment.get(env_var_name)
            if env_value is not None:
                value = ConfigValue(
                    value=env_value,
                    source=EnvironmentVariableConfigSource(
                        name=env_var_name,
                    ),
                )
                self.config.__setattr__(field, value)

        postgres_test_uri = environment.get("MONICO_TEST_POSTGRES_URI")
        if postgres_test_uri is not None:
            value = ConfigValue(
                value=postgres_test_uri,
                source=EnvironmentVariableConfigSource(
                    name="MONICO_TEST_POSTGRES_URI",
                ),
            )
            self.config.postgres_uri = value
