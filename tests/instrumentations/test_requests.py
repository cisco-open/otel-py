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

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from cisco_otel_py import tracing
from cisco_opentelemetry_specifications import SemanticAttributes

from requests import get


class TestRequests(unittest.TestCase):
    async def test_http_request_headers(self):
        try:
            provider = TracerProvider(
                resource=Resource.create({"application": "Test_App"})
            )

            exporter = InMemorySpanExporter()
            trace.set_tracer_provider(provider)
            provider.add_span_processor(SimpleSpanProcessor(exporter))

            tracing._auto_instrument()

            get(
                url="https://google.com/",
                headers={"test-header-key": "test-header-value"},
            )

            spans = exporter.get_finished_spans()

            self.assertEqual(len(spans), 1)

            span: ReadableSpan = spans[0]

            self.assertEqual(
                span.attributes[
                    f"{SemanticAttributes.HTTP_REQUEST_HEADER.key}.test-header-key"
                ],
                "test-header-value",
            )

        except Exception as err:
            self.fail(f"unexpected exception: {err}")


if __name__ == "__main__":
    unittest.main()
