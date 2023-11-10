import click
from monic.core.monitor import MonitorAttributeError
from monic.core.storage import StorageSetupException


def adapt(func):
    """Adapts monic exceptions to click exceptions for CLI usage"""
    try:
        return func()
    except MonitorAttributeError as e:
        # MonitorAttributeError is a user facing error, so we can just print it
        raise click.ClickException(str(e))
    except StorageSetupException as e:
        # StorageSetupException is a user facing error, so we can just print it
        raise click.ClickException(str(e))
