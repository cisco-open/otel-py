# otel-py

Alpha version

This package provides a Cisco Launcher for OpenTelemetry python

## Installation

pip

```sh
pip install cisco-otel-py
```

poetry

```sh
poetry add cisco-otel-py
```

## Usage

```python
from cisco_otel_py import tracing

tracing.init()
```

## Configuration

Advanced options can be configured as a parameter to the init() method:

| Parameter          | Env                     | Type    | Default                 | Description                                                       |
| ------------------ | ------------------------| ------- | ----------------------- | ----------------------------------------------------------------- |
| cisco_token        | CISCO_TOKEN             | string  | -                       | Cisco account token                                               |
| service_name       | OTEL_SERVICE_NAME       | string  | `application`           | Application name that will be set for traces                      |
| collector_endpoint | OTEL_COLLECTOR_ENDPOINT | string  | `http://localhost:4317` | The address of the trace collector to send traces to                                                                                                |
| type               | OTEL_EXPORTER_TYPE      | string  | `otlp-grpc`             | The exporter type to use (Currently `otlp-grpc`, `otlp-http` are supported). Multiple exporter option available via init function see example below |


