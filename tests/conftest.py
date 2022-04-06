import pytest
from opentelemetry.sdk.trace import TracerProvider

from cisco_otel_py import tracing, consts, options
from cisco_otel_py.instrumentations.wrappers import InstrumentationWrapper
from tests import utils


@pytest.fixture(scope="session")
def cisco_tracer():
    InstrumentationWrapper.uninstrument_all()
    provider = tracing.init(
        cisco_token=utils.TEST_TOKEN,
        exporters=[
            options.ExporterOptions(
                exporter_type=consts.TEST_EXPORTER_TYPE,
                collector_endpoint=utils.LOCAL_COLLECTOR,
            ),
        ],
    )

    return provider


@pytest.fixture(scope="function")
def exporter(cisco_tracer: TracerProvider):
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    exporter = InMemorySpanExporter()
    cisco_tracer.add_span_processor(SimpleSpanProcessor(exporter))

    yield exporter

    exporter.clear()
