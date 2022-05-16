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
	make test

.PHONY: bootstrap
bootstrap:
	pip install opentelemetry-distro==0.29b0
	opentelemetry-bootstrap --action=install

.PHONY: all
all: install-poetry deps bootstrap build
