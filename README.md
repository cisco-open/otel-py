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

One-time script run to install opentelemetry dependencies:

```shell
otel-py-bootstrap
```

```python
from cisco_otel_py import tracing, options

tracing.init(
    service_name="my-service-name",
    cisco_token="my-cisco-token",
    exporters=[options.ExporterOptions(
        collector_endpoint="http://localhost:4317",
        exporter_type="otlp-grpc"
    )]
)
```

## Configuration

Advanced options can be configured as a parameter to the init() method:

| Parameter          | Env                     | Type    | Default                 | Description                                                       |
| ------------------ | ------------------------| ------- | ----------------------- | ----------------------------------------------------------------- |
| cisco_token        | CISCO_TOKEN             | string  | -                       | Cisco account token                                               |
| service_name       | OTEL_SERVICE_NAME       | string  | `application`           | Application name that will be set for traces                      |
| collector_endpoint | OTEL_COLLECTOR_ENDPOINT | string  | `http://localhost:4317` | The address of the trace collector to send traces to                                                                                                |
| type               | OTEL_EXPORTER_TYPE      | string  | `otlp-grpc`             | The exporter type to use (Currently `otlp-grpc`, `otlp-http` are supported). Multiple exporter option available via init function see example below |

Exporter options | Parameter | Env | Type | Default | Description | | ------------------ | ----------------------- |
------ | ----------------------- |
----------------------------------------------------------------------------------------------------------------------------------------------------
| | collector_endpoint | OTEL_COLLECTOR_ENDPOINT | string | `http://localhost:4317` | The address of the trace collector
to send traces to | | exporter_type | OTEL_EXPORTER_TYPE | string | `otlp-grpc`             | The exporter type to use (
Currently `otlp-grpc`, `otlp-http` are supported). Multiple exporter option available via init function see example
bellow |

## Multi-exporter initiation

```python
from cisco_otel_py import tracing, options

tracing.init(
    service_name="my-service-name",
    cisco_token="my-cisco-token",
    exporters=[
        options.ExporterOptions(
            collector_endpoint="http://localhost:4317",
            exporter_type="otlp-grpc"),
        options.ExporterOptions(
            collector_endpoint="remote-http-collector-endpoint",
            exporter_type="otlp-http"
        )]
)
```