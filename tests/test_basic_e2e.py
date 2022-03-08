import unittest
from cisco_otel_py import tracing
from opentelemetry import trace


class TestE2E(unittest.TestCase):
    def test_happy_flow(self):
        try:
            tracing.init(collector_endpoint="localhost:4317")

            tracer = trace.get_tracer("happy_flow")
            with tracer.start_as_current_span(
                    "test span", kind=trace.SpanKind.INTERNAL
            ) as span:
                span.add_event("test_event", {"test_key": "test_value"})
                print("trigger span event")

        except Exception:
            self.fail("tracing.init() resulted with unexpected exception!")


if __name__ == '__main__':
    unittest.main()
