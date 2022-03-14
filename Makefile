DEV_VENV?=""
VERSION?=""

.PHONY: all
all: test

.PHONY: install-poetry
install-poetry:
	pip install poetry==1.1.12

.PHONY: install-tools
install-tools: install-poetry

.PHONY: deps
deps:
	poetry install

.PHONY: clean
clean:
	@rm -rf dist

.PHONY: build
build:
	poetry build

.PHONY: test
test:
	poetry run pytest tests/
