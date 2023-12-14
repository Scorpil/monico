H1="\n\n\033[0;32m\#\#\# "
H1END=" \#\#\# \033[0m\n"

# which python to use for creating the venv
SYSTEM_PYTHON=python3
VENV_ROOT=venv
VENV_BIN=$(VENV_ROOT)/bin

.PHONY: install
install: venv install-venv

venv:
	@echo $(H1)Creating venv in ./${VENV_ROOT} $(H1END)

	$(SYSTEM_PYTHON) -m venv --prompt monico $(VENV_ROOT)

	@echo
	@echo venv created in $(VENV_ROOT)
	@echo
	@echo Active it with:
	@echo
	@echo "    source $(VENV_BIN)/activate"
	@echo
	@echo '(documentation: https://docs.python.org/3/library/venv.html)'

.PHONY: install-venv
install-venv: # install all dependencies
	@echo $(H1)Updating package tools$(H1END)
	$(VENV_BIN)/pip install --upgrade pip wheel build

	@echo $(H1)Installing dev dependencies$(H1END)
	$(VENV_BIN)/pip install '.[dev]'

	@echo $(H1)Installing postgres dependencies$(H1END)
	$(VENV_BIN)/pip install '.[postgres]'

	@echo $(H1)Installing package in editable mode$(H1END)
	$(VENV_BIN)/pip install -e '.'

.PHONY: build
build: # build the package
	@echo $(H1)Building package$(H1END)
	$(VENV_BIN)/python -m build .

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