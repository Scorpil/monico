import click
from monic.core.monitor import MonitorAttributeError
from monic.core.storage import (
    StorageSetupException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
    StorageConnectionException,
)


def _adapt(func):
    """Adapts monic exceptions to click exceptions for CLI usage"""
    try:
        return func()
    except (
        MonitorAttributeError,
        StorageSetupException,
        MonitorAlreadyExistsException,
        MonitorNotFoundException,
    ) as e:
        # these are predictable user facing exceptions, so we can just print them
        raise click.ClickException(str(e))
    except StorageConnectionException as e:
        raise click.ClickException(
            "Failed to connect to storage backend. Please check your configuration."
        )


def adapt_exceptions_for_cli(func):
    def wrapper(*args, **kwargs):
        return _adapt(lambda: func(*args, **kwargs))

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
