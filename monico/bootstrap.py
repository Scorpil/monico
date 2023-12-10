import logging
from monico.core.app import App
from monico.storage.pg import PgStorage
from monico.config import Config


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


def build_default_app() -> App:
    """Builds main monico app."""
    config = Config.build()

    storage = PgStorage(config.postgres_uri)

    log = logging.getLogger("monico")
    log.setLevel(config.log_level)

    ch = logging.StreamHandler()
    ch.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    log.addHandler(ch)

    log.debug(f"log level set to {config.log_level}")

    storage.connect()
    return App(storage, log)
