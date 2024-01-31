PYTHON_VERSION := $(shell python -c "print(open('.python-version').read().strip())")
INSTALLED_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

.PHONY: \
  check_python_version \
  linters \
  setup_venv \
  start \
  build \
  down

# Checks if the installed Python version matches the required version
check_python_version:
	@if [ "$(PYTHON_VERSION)" != "$(INSTALLED_VERSION)" ]; then \
		echo "ERROR: Installed Python version $(INSTALLED_VERSION) does not match the required version $(PYTHON_VERSION)"; \
		exit 1; \
	fi

# Creates a virtual environment and installs dependencies
setup_venv:
	@make check_python_version
	@rm -rf .venv
	@poetry install

# Runs linters
linters:
	@if [ ! -d ".venv" ]; then \
		echo "Virtual environment not found. Creating one..."; \
		make setup_venv; \
	fi

	@poetry run python -m black --check --line-length=120 .
	@poetry run python -m flake8 --config .flake8
	@poetry run python -m pylint --rcfile=.pylintrc --recursive=y --ignore=.venv --disable=fixme .
	@poetry run python -m mypy --config-file mypy.ini .

build:
	@docker-compose build cumplo-orchestrator --build-arg CUMPLO_PYPI_BASE64_KEY=`base64 -i cumplo-pypi-credentials.json`

start:
	@docker-compose up -d cumplo-orchestrator

down:
	@docker-compose down