import logging
from monic import bootstrap
from monic.storage.pg import PgStorage
from unittest import mock

def test_app_context():
    with mock.patch('monic.bootstrap.build_default_app') as build_default_app_mock:
        build_default_app_mock.return_value = mock.MagicMock()

        with bootstrap.AppContext.create() as app:
            build_default_app_mock.assert_called_once()
            assert app is build_default_app_mock.return_value
        assert app.shutdown.called_once()

def test_build_default_app():
    with mock.patch.object(PgStorage, 'connect') as pg_storage_connect_mock:
        with mock.patch.object(logging, 'getLogger') as get_logger_mock:
            get_logger_mock.return_value = mock.MagicMock()
            app = bootstrap.build_default_app()
            assert isinstance(app, bootstrap.App)
            get_logger_mock.assert_called_once_with('monic')
            assert app.log is get_logger_mock.return_value
            assert isinstance(app.storage, PgStorage)
            assert app.storage.connect.called_once()
