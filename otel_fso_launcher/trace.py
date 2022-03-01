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
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from pkg_resources import iter_entry_points
from otel_fso_launcher import consts


def init() -> TracerProvider:
    """Initiate and return an otel trace provider"""

    provider = _set_tracing()
    _auto_instrument()

    return provider


def _set_tracing() -> TracerProvider:
    service_name = os.environ.get("serviceName") or consts.SERVICE_NAME
    fso_endpoint = os.environ.get("FSOEndpoint") or consts.FSO_ENDPOINT
    fso_token = os.environ.get("FSOToken") or consts.FSO_TOKEN

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": service_name,
                "FSOEndpoint": fso_endpoint,
                "FSOToken": fso_token,
            }
        )
    )
    processor = BatchSpanProcessor(ConsoleSpanExporter())
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
