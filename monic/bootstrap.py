from monic.core.app import App
from monic.storage.pg import PgStorage
from monic.config import Config


def build_app() -> App:
    """Builds main monic app."""
    config = Config.build()
    storage = PgStorage(config.postgres_uri)
    storage.connect()
    return App(storage)
