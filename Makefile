DEV_VENV?=""
VERSION?=""

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
