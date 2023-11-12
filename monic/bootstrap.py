import logging
from monic.core.app import App
from monic.storage.pg import PgStorage
from monic.config import Config


def build_app() -> App:
    """Builds main monic app."""
    config = Config.build()
    storage = PgStorage(config.postgres_uri)

    log = logging.getLogger("monic")
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
