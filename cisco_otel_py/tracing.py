"""
Copyright The Cisco Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pkg_resources import iter_entry_points
from cisco_otel_py import consts, configurations
from cisco_otel_py.exporter_factory import SpanExporterFactory


def init(
        service_name: str = None,
        cisco_token: str = None,
        collector_endpoint: str = None,
        exporter_type: str = None,
    ) -> TracerProvider:

    options = configurations.Options(
        service_name,
        cisco_token,
        collector_endpoint,
        exporter_type
    )

    provider = set_tracing(options)
    _auto_instrument()

    return provider


def set_tracing(options: configurations.Options) -> TracerProvider:
    service_name = os.environ.get("serviceName") or consts.SERVICE_NAME

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": service_name,
            }
        )
    )
    exporter = SpanExporterFactory(options)
    processor = BatchSpanProcessor(exporter)
    trace.set_tracer_provider(provider)
    provider.add_span_processor(processor)

    return provider


def _auto_instrument():
    for entry_point in iter_entry_points("opentelemetry_instrumentor"):
        try:
            entry_point.load()().instrument()  # type: ignore
            print("Instrumented %s", entry_point.name)
        except Exception:  # pylint: disable=broad-except
            print("Instrumenting of %s failed", entry_point.name)
