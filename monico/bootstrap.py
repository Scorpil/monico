import os
import logging
from monico.core.app import App
from monico.storage.pg import PgStorage
from monico.storage.sqlite import SqliteStorage
from monico.config import Config, ConfigLoader


class AppBootstrapException(EnvironmentError):
    """Exception raised when app bootstrap fails."""

    pass


class AppContext:
    """Context manager for monico app."""

    @staticmethod
    def create():
        return AppContext(build_default_app())

    def __init__(self, app: App):
        self.app = app

    def __enter__(self) -> App:
        return self.app

    def __exit__(self, *args):
        self.app.shutdown()


def build_storage(config: Config, log: logging.Logger) -> PgStorage:
    """Builds storage from config."""
    if config.postgres_uri is None and config.sqlite_uri is None:
        default_db_location = os.path.expanduser("~/.monic/monico.db")
        default_sqlite_uri = f"sqlite://{default_db_location}"
        log.debug(
            "no storage backend specified, "
            f"using default sqlite: {default_sqlite_uri}"
        )
        storage = SqliteStorage(default_sqlite_uri)
    elif config.sqlite_uri is not None:
        log.debug(f"using sqlite storage: {config.sqlite_uri.value}")
        storage = SqliteStorage(config.sqlite_uri.value)
    elif config.postgres_uri is not None:
        log.debug(f"using postgres storage: {config.postgres_uri.value}")
        storage = PgStorage(config.postgres_uri.value)
    return storage


def build_default_app() -> App:
    """Builds main monico app."""
    config = ConfigLoader().load()
    log = logging.getLogger("monico")
    log.setLevel(config.log_level.value)

    storage = build_storage(config, log)
    storage.connect()

    ch = logging.StreamHandler()
    ch.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    log.addHandler(ch)

    log.debug(f"log level set to {config.log_level.value}")

    storage.connect()
    return App(storage, log)
