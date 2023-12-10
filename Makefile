.PHONY: lint
fmt:
	python -m black ./monico ./tests

.PHONY: test
test: # run all tests
	python -m pytest -v --cov=monico --cov-report=term-missing --cov-fail-under=80 tests

.PHONY: test-unit
test-unit: # run unit tests only
	python -m pytest -v tests/unit

.PHONY: test-integration
test-integration: # run integration tests only
	python -m pytest -v tests/integration