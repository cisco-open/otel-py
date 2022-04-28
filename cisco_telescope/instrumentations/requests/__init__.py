from opentelemetry.instrumentation.requests import RequestsInstrumentor
from cisco_telescope.instrumentations import BaseInstrumentorWrapper

from ..utils import Utils

from cisco_opentelemetry_specifications import SemanticAttributes


def get_active_span_for_call_wrapper(requests_wrapper):
    def get_active_span_for_call(span, response) -> None:
        if not span.is_recording():
            return

        if hasattr(response, "request"):
            Utils.add_flattened_dict(
                span,
                SemanticAttributes.HTTP_REQUEST_HEADER,
                getattr(response.request, "headers", dict()),
            )

            Utils.set_payload(
                span,
                SemanticAttributes.HTTP_REQUEST_BODY,
                getattr(response.request, "body", str()),
                requests_wrapper.payloads_enabled,
                requests_wrapper.max_payload_size,
            )

        Utils.add_flattened_dict(
            span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            getattr(response, "headers", dict()),
        )

        Utils.set_payload(
            span,
            SemanticAttributes.HTTP_RESPONSE_BODY,
            getattr(response, "content", bytes()),
            requests_wrapper.payloads_enabled,
            requests_wrapper.max_payload_size,
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
