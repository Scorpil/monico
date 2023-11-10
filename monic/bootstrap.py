from monic.core.app import App
from monic.storage.local import LocalStorage


def build_app() -> App:
    """Builds main monic app."""
    storage = LocalStorage()
    return App(storage)
