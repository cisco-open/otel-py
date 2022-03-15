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
from cisco_otel_py import tracing, consts, options
from opentelemetry import trace

from . import utils


class TestInit(unittest.TestCase):
    def test_happy_flow(self):
        try:
            tracing.init(
                cisco_token=utils.TEST_TOKEN,
                exporters=[
                    options.ExporterOptions(
                        exporter_type=consts.TEST_EXPORTER_TYPE,
                        collector_endpoint=utils.LOCAL_COLLECTOR,
                    ),
                    options.ExporterOptions(
                        exporter_type=consts.GRPC_EXPORTER_TYPE,
                        collector_endpoint=utils.LOCAL_COLLECTOR,
                    ),
                ],
            )

            tracer = trace.get_tracer("happy_flow")
            with tracer.start_as_current_span(
                "test span", kind=trace.SpanKind.INTERNAL
            ) as span:
                span.add_event("test_event", {"test_key": "test_value"})
                print("trigger span event")

        except Exception:
            self.fail(
                "span event on tracing.init() happy flow resulted with unexpected exception!"
            )

    def test_missing_token(self):

        with self.assertRaises(ValueError) as context:
            tracing.init(cisco_token=None)

        self.assertTrue(
            "Can not initiate cisco-otel launcher without token", context.exception
        )

    def test_exporter_type(self):

        with self.assertRaises(ValueError) as context:
            tracing.init(
                exporters=[
                    options.ExporterOptions(exporter_type="non_relevant_exporter_type")
                ]
            )

        self.assertTrue("Unsupported exported type", context.exception)


if __name__ == "__main__":
    unittest.main()
