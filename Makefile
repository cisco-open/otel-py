DEV_VENV?=""
VERSION?=""

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

.PHONY: build
build:
	poetry build

.PHONY: test
test:
	poetry run pytest tests/

.PHONY: boot
boot:
	opentelemetry-bootstrap --action=install

.PHONY: all
all: install-poetry deps boot build test clean