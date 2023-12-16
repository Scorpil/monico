import os
import logging
from monico.core.app import App
from monico.core.storage import StorageInterface
from monico.config import ConfigurationError
from monico.storage.sqlite import SqliteStorage
from monico.config import Config, ConfigLoader
try:
    from monico.storage.pg import PgStorage
    postgres_support = True
except ImportError:
    # optional dependency
    # this will fail unless monico[postgres] is installed
    postgres_support = False



class AppBootstrapException(EnvironmentError):
    """Exception raised when app bootstrap fails."""

    pass


class AppContext:
    """Context manager for monico app."""

    @staticmethod
    def create():
        return AppContext(build_default_app(postgres_support))

    def __init__(self, app: App):
        self.app = app

    def __enter__(self) -> App:
        return self.app

    def __exit__(self, *args):
        self.app.shutdown()


def build_storage(config: Config, log: logging.Logger, postgres_support: bool) -> StorageInterface:
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
        if not postgres_support:
            raise ConfigurationError(
                "PostgreSQL storage is configured, "
                "but PostgreSQL dependencies are not found.\n"
                "This can be fixed by installing optional monitco "
                "PostgreSQL dependencies:\n\n"
                "\tpip install 'monico[postgres]'\n"
                #"Detailed instructions can be found at:\n"
                #"https://monico.io/docs/installation/postgres.html"
            )
        log.debug(f"using postgres storage: {config.postgres_uri.value}")
        storage = PgStorage(config.postgres_uri.value)
    return storage


def build_default_app(postgres_support) -> App:
    """Builds main monico app."""
    config = ConfigLoader().load()
    log = logging.getLogger("monico")
    log.setLevel(config.log_level.value)

    storage = build_storage(config, log, postgres_support)
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
