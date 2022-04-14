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

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from pkg_resources import iter_entry_points, get_distribution

from .instrumentations.instrumentation_wrapper import InstrumentationWrapper
from . import consts
from . import options
from . import exporter_factory


def init(
    service_name: str = None,
    cisco_token: str = None,
    max_payload_size: int = None,
    exporters: [options.ExporterOptions] = None,
) -> TracerProvider:
    opt = options.Options(service_name, cisco_token, max_payload_size, exporters)

    provider = _set_tracing(opt)
    _auto_instrument()

    return provider


def _get_sdk_version():
    sdk_distribution = get_distribution(__package__)

    if hasattr(sdk_distribution, 'version'):
        return sdk_distribution.version

    return consts.DEFAULT_SDK_VERSION


def _set_tracing(opt: options.Options) -> TracerProvider:
    provider = TracerProvider(
        resource=Resource.create(
            {
                "application": opt.service_name,
                "cisco.sdk.version": _get_sdk_version(),
                ResourceAttributes.SERVICE_NAME: opt.service_name,
            }
        )
    )
    exporters = exporter_factory.init_exporters(opt)

    for exporter in exporters:
        processor = BatchSpanProcessor(exporter)
        trace.set_tracer_provider(provider)
        provider.add_span_processor(processor)

    return provider


def _auto_instrument():
    for entry_point in iter_entry_points("opentelemetry_instrumentor"):
        try:
            wrapped_instrument = InstrumentationWrapper.get_instrumentation_wrapper(
                entry_point.name
            )
            if wrapped_instrument:
                wrapped_instrument.instrument()
                print("Instrumented %s" % entry_point.name)
            else:
                entry_point.load()().instrument()  # type: ignore
                print("Instrumented %s" % entry_point.name)
        except Exception:
            print("Instrumenting of %s failed" % entry_point.name)
