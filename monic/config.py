import os
import toml
from typing import Optional


class Config:
    CONFIG_FILE_LOCATIONS = [
        "/etc/monic/.monic.toml",  # System-wide
        "~/.monic.toml",  # User's home directory
        "./.monic.toml",  # Current working directory
    ]
    postgres_uri: Optional[str] = None

    @staticmethod
    def build():
        config = Config()
        config.load_from_config_file()
        config.load_from_env()
        return config

    def __init__(self, postgres_uri: Optional[str] = None):
        self.postgres_uri = postgres_uri

    def __repr__(self):
        return f"<Config postgres_uri={self.postgres_uri}>"

    def load_from_config_file(self):
        """Builds config from config file"""
        for location in Config.CONFIG_FILE_LOCATIONS:
            try:
                with open(os.path.expanduser(location)) as f:
                    file_config = toml.load(f)
                    self.postgres_uri = (
                        file_config.get("postgres_uri", None) or self.postgres_uri
                    )
            except FileNotFoundError:
                pass

    def load_from_env(self, environment: dict = os.environ):
        """Builds config from environment variables"""
        if not self.postgres_uri:
            self.postgres_uri = environment.get("MONIC_POSTGRES_URI", None)
