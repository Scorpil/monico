.PHONY: lint
fmt:
	python -m black ./monic ./tests

.PHONY: test
test:
	python -m pytest -v --cov=monic --cov-report=term-missing --cov-fail-under=80