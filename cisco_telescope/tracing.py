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

import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from pkg_resources import iter_entry_points
from importlib_metadata import version, PackageNotFoundError
from cisco_opentelemetry_specifications import Consts

from .instrumentations.instrumentation_wrapper import InstrumentationWrapper
from . import options
from . import exporter_factory
from . import configuration


def init(
    service_name: str = None,
    cisco_token: str = None,
    debug: bool = None,
    payloads_enabled: bool = None,
    max_payload_size: int = None,
    disable_instrumentations: bool = None,
    exporters: [options.ExporterOptions] = None,
) -> TracerProvider:
    opt = options.Options(
        service_name,
        cisco_token,
        debug,
        payloads_enabled,
        max_payload_size,
        disable_instrumentations,
        exporters,
    )
    configuration.Configuration().set_options(opt)
    logging.debug(f"Configuration: {opt}")

    if opt.disable_instrumentations:
        provider = None
    else:
        provider = _set_tracing(opt)
        _auto_instrument(opt)

    return provider


def _get_sdk_version():
    try:
        sdk_version = version(__package__)
    except PackageNotFoundError:
        sdk_version = Consts.CISCO_SDK_VERSION_NOT_SUPPORTED

    return sdk_version


def _set_tracing(opt: options.Options) -> TracerProvider:
    trace_attributes = {Consts.CISCO_SDK_VERSION: _get_sdk_version()}
    if opt.service_name:
        trace_attributes.update({ResourceAttributes.SERVICE_NAME: opt.service_name})

    provider = TracerProvider(resource=Resource.create(trace_attributes))

    trace.set_tracer_provider(provider)

    exporters = exporter_factory.init_exporters(opt)
    for exporter in exporters:
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

    return provider


def _auto_instrument(opt: options.Options):
    for entry_point in iter_entry_points("opentelemetry_instrumentor"):
        try:
            wrapped_instrument = InstrumentationWrapper.get_instrumentation_wrapper(
                opt, entry_point.name
            )
            if wrapped_instrument:
                wrapped_instrument.instrument()
            else:
                entry_point.load()().instrument()
            logging.debug(f"Instrumented {entry_point.name}")
        except Exception:
            logging.debug(f"Could not instrument {entry_point.name}")
