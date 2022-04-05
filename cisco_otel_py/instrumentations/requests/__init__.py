from opentelemetry.instrumentation.requests import RequestsInstrumentor
from cisco_otel_py.instrumentations import BaseInstrumentorWrapper


def get_active_span_for_call_wrapper(requests_wrapper, stream):
    def get_active_span_for_call(span, response) -> None:
        import ipdb;ipdb.set_trace()
        request_headers = dict()
        request_body = ""
        if hasattr(response, "request"):
            request_headers = getattr(response.request, "headers", dict())
            request_body = getattr(response.request, "body", str())

        response_headers = getattr(response, "headers", dict())
        response_body = getattr(response, "content", str())

        if span.is_recording():
            requests_wrapper.generic_request_handler(
                request_headers, request_body, span
            )

            requests_wrapper.generic_response_handler(
                response_headers, response_body, span
            )

    return get_active_span_for_call


def name_callback(method, url) -> str:
    return method + " " + url


class RequestsInstrumentorWrapper(RequestsInstrumentor, BaseInstrumentorWrapper):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            span_callback=get_active_span_for_call_wrapper(self, kwargs.get("stream")),
            name_callback=name_callback,
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()
