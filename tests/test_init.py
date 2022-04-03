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

import unittest

import pytest

from cisco_otel_py import tracing, options
from opentelemetry import trace
import logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)


def test_happy_flow():
    tracer = trace.get_tracer("happy_flow")
    with tracer.start_as_current_span(
        "test span", kind=trace.SpanKind.INTERNAL
    ) as span:
        span.add_event("test_event", {"test_key": "test_value"})
        logger.debug("trigger span event")


def test_missing_token():
    with pytest.raises(ValueError) as exceptionInfo:
        tracing.init(cisco_token=None)

    assert "Can not initiate cisco-otel launcher without token" == str(
        exceptionInfo.value
    )


def test_exporter_type():

    with pytest.raises(ValueError) as exceptionInfo:
        tracing.init(
            exporters=[
                options.ExporterOptions(exporter_type="non_relevant_exporter_type")
            ]
        )

    assert "Unsupported exported type" == str(exceptionInfo.value)
