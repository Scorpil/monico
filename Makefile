.PHONY: lint
fmt:
	python -m black ./monic ./tests

.PHONY: test
test:
	python -m pytest -v --cov=monic --cov-report=term-missing --cov-fail-under=80 tests

.PHONY: test-unit
test-unit:
	python -m pytest -v tests/unit

.PHONY: test-integration
test-integration:
	python -m pytest -v tests/integration