from opentelemetry.instrumentation.requests import RequestsInstrumentor
from cisco_otel_py.instrumentations import BaseInstrumentorWrapper


def get_active_span_for_call_wrapper(requests_wrapper):
    def get_active_span_for_call(span, response) -> None:
        request_headers = dict()
        request_body = ""
        if hasattr(response, 'request'):
            request_headers = getattr(response.request, 'headers', dict())
            request_body = getattr(response.request, 'body', '')

        if span.is_recording():
            requests_wrapper.generic_request_handler(
                request_headers, request_body, span
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
            span_callback=get_active_span_for_call_wrapper(self),
            name_callback=name_callback,
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()
