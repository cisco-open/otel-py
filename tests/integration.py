from cisco_otel_py import tracing, configurations
from opentelemetry import trace as otel_trace


def main():
    tracing.init(configurations.Options(cisco_token="mock_token"))
    tracer = otel_trace.get_tracer("basic", "0.1")
    with tracer.start_as_current_span(
        "custom span", kind=otel_trace.SpanKind.INTERNAL
    ) as span:
        span.add_event("event1", {"k1": "v1"})


if __name__ == "__main__":
    main()
