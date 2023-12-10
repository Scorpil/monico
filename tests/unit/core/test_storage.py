import pytest
from unittest import mock
from monico.core.storage import StorageInterface


class TestStorageInterface:
    @mock.patch.multiple(StorageInterface, __abstractmethods__=set())
    def test_empty_methods(self):
        # these methods are empty by default. Verify they don't raise exceptions
        si = StorageInterface()
        si.connect()
        si.disconnect()
        si.setup()
        si.teardown()

    @mock.patch.multiple(StorageInterface, __abstractmethods__=set())
    def test_abstract_methods(self):
        # these methods are abstract and must be implemented by subclasses
        si = StorageInterface()
        with pytest.raises(NotImplementedError):
            si.create_monitor(None)
        with pytest.raises(NotImplementedError):
            si.list_monitors()
        with pytest.raises(NotImplementedError):
            si.read_monitor(None)
        with pytest.raises(NotImplementedError):
            si.delete_monitor(None)
        with pytest.raises(NotImplementedError):
            si.create_task(None)
        with pytest.raises(NotImplementedError):
            si.lock_tasks(None, None)
        with pytest.raises(NotImplementedError):
            si.update_task(None)
        with pytest.raises(NotImplementedError):
            si.record_probe(None)
        with pytest.raises(NotImplementedError):
            si.list_probes(None)
