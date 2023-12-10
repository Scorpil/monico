import os
import toml
from typing import Optional


class Config:
    CONFIG_FILE_LOCATIONS = [
        "/etc/monico/.monico.toml",  # System-wide
        "~/.monico.toml",  # User's home directory
        "./.monico.toml",  # Current working directory
    ]
    postgres_uri: Optional[str] = None
    log_level: str = "INFO"

    @staticmethod
    def build():
        config = Config()
        config.load_from_config_file()
        config.load_from_env()
        return config

    def __init__(self, postgres_uri: Optional[str] = None, log_level: str = "WARNING"):
        self.postgres_uri = postgres_uri
        self.log_level = log_level

    def __repr__(self):
        return f"<Config postgres_uri={self.postgres_uri} log_level={self.log_level}>"

    def load_from_config_file(self):
        """Builds config from config file"""
        for location in self.CONFIG_FILE_LOCATIONS:
            try:
                with open(os.path.expanduser(location)) as f:
                    file_config = toml.load(f)
                self.postgres_uri = file_config.get("postgres_uri", self.postgres_uri)
                self.log_level = file_config.get("log_level", self.log_level)
            except FileNotFoundError:
                pass

    def load_from_env(self, environment: dict = os.environ):
        """Builds config from environment variables"""
        self.postgres_uri = environment.get(
            "MONICO_TEST_POSTGRES_URI",
            environment.get("MONICO_POSTGRES_URI", self.postgres_uri),
        )
        self.log_level = environment.get("MONICO_LOG_LEVEL", self.log_level)
