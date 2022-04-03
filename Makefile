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
	poetry run pytest --cov=cisco_otel_py tests/

.PHONY: pretty
pretty:
	python3 -m black cisco_otel_py/*.*
	python3 -m black tests/*.*

.PHONY: bootstrap
bootstrap:
	pip install opentelemetry-distro==0.29b0
	opentelemetry-bootstrap --action=install

.PHONY: all
all: install-poetry deps bootstrap build
