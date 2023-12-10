import os
import pytest


def setup_module(module):
    test_postgres_uri = os.environ.get("MONICO_TEST_POSTGRES_URI", None)
    if not test_postgres_uri:
        pytest.skip("Set MONICO_TEST_POSTGRES_URI to enable integration tests")
