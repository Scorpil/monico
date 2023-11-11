import click
from monic.core.monitor import MonitorAttributeError
from monic.core.storage import (
    StorageSetupException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
)


def adapt(func):
    """Adapts monic exceptions to click exceptions for CLI usage"""
    try:
        return func()
    except (
        MonitorAttributeError,
        StorageSetupException,
        MonitorAlreadyExistsException,
        MonitorNotFoundException,
    ) as e:
        # MonitorAttributeError is a user facing error, so we can just print it
        raise click.ClickException(str(e))
