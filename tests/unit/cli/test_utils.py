import pytest
import click
from monico.core.storage import (
    StorageSetupException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
    StorageConnectionException,
)
from monico.core.monitor import MonitorAttributeError
from monico.cli.utils import _adapt
from monico.config import ConfigurationError


def test_adapt():
    def raise_exception(ExceptionClass):
        raise ExceptionClass("test")

    for ExceptionClass in [
        MonitorAttributeError,
        StorageSetupException,
        MonitorAlreadyExistsException,
        MonitorNotFoundException,
        ConfigurationError,
    ]:
        with pytest.raises(click.ClickException):
            _adapt(lambda: raise_exception(ExceptionClass))

    with pytest.raises(
        click.ClickException,
        match="Failed to connect to storage backend. Please check your configuration.",
    ):
        _adapt(lambda: raise_exception(StorageConnectionException))
