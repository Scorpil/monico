import pytest
import click
from monic.core.storage import (
    StorageSetupException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
)
from monic.core.monitor import MonitorAttributeError
from monic.cli.utils import _adapt


def test_adapt():
    def raise_exception(ExceptionClass):
        raise ExceptionClass("test")

    for ExceptionClass in [
        MonitorAttributeError,
        StorageSetupException,
        MonitorAlreadyExistsException,
        MonitorNotFoundException,
    ]:
        with pytest.raises(click.ClickException):
            _adapt(lambda: raise_exception(ExceptionClass))
