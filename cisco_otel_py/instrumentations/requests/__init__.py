from opentelemetry.instrumentation.requests import RequestsInstrumentor
from cisco_otel_py.instrumentations import BaseInstrumentorWrapper


def get_active_span_for_call_wrapper(requests_wrapper):
    def get_active_span_for_call(span, response) -> None:
        response_content = None
        if hasattr(response, "content"):
            response_content = response.content.decode()
        else:
            response_content = ""
        request_content = None
        if hasattr(response.request, "body"):
            request_content = response.request.body.decode()
        else:
            request_content = ""

        if span.is_recording():
            requests_wrapper.generic_request_handler(
                response.request.headers, request_content, span
            )
            requests_wrapper.generic_response_handler(
                response.headers, response_content, span
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
