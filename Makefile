DEV_VENV?=""
VERSION?=""

.PHONY: all
all: install-poetry deps clean boot build test



install-poetry:
.PHONY: install-poetry
install-poetry:
	pip install poetry==1.1.12

.PHONY: install-tools
install-tools: install-poetry

deps:
.PHONY: deps
deps:
	poetry install

.PHONY: clean
clean:
	@rm -rf dist

.PHONY: boot
boot:
	otel-py-bootstrap

.PHONY: build
build:
	poetry build

.PHONY: test
test:
	poetry run pytest tests/

.PHONY: all
all: test
