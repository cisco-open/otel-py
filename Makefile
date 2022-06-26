DEV_VENV?=""
VERSION?=""

.PHONY: install-poetry
install-poetry:
	pip install poetry

.PHONY: deps
deps:
	poetry install
	poetry run toml-sort pyproject.toml --all --in-place
	pip list --format=freeze > requirements.txt

.PHONY: clean
clean:
	@rm -rf dist

.PHONY: build
build:
	poetry build

.PHONY: test
test:
	poetry run pytest --forked --cov=cisco_telescope --cov-report=xml

.PHONY: proto
proto:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tests/instrumentations/grpc/hello.proto
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tests/instrumentations/streamed_grpc/bidirectional.proto

.PHONY: pretty
pretty:
	black .

.PHONY: prep
prep:
	make pretty
	make deps
	make test

.PHONY: bootstrap
bootstrap:
	make deps
	opentelemetry-bootstrap --action=install

.PHONY: all
all: install-poetry deps build
