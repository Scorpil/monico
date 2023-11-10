import click
from monic.core.monitor import MonitorAttributeError


def adapt(func):
    """Adapts monic exceptions to click exceptions for CLI usage"""
    try:
        return func()
    except MonitorAttributeError as e:
        # MonitorAttributeError is a user facing error, so we can just print it
        raise click.ClickException(str(e))
