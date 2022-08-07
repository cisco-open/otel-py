from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from cisco_opentelemetry_specifications import SemanticAttributes
from instrumentation.telescope_instrumentation_utils import Utils


def server_request_hook_wrapper():
    def server_request_hook(span, request) -> None:
        if not span.is_recording():
            return

        headers = request.get("headers", list())  # List of key value tuple
        Utils.add_flattened_dict(
            span, SemanticAttributes.HTTP_REQUEST_HEADER, dict(headers)
        )

    return server_request_hook


def client_request_hook_wrapper():
    def client_request_hook(span, request) -> None:
        if not span.is_recording():
            return

        headers = request.get("headers", list())  # List of key value tuple
        Utils.add_flattened_dict(
            span, SemanticAttributes.HTTP_REQUEST_HEADER, dict(headers)
        )

    return client_request_hook


def client_response_hook_wrapper():
    def client_response_hook(span, response) -> None:
        if not span.is_recording():
            return

        if "body" in response:
            Utils.set_payload(
                span, SemanticAttributes.HTTP_REQUEST_BODY, response["body"]
            )

        headers = response.get("headers", list())  # List of key value tuple
        Utils.add_flattened_dict(
            span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            dict(headers),
        )

    return client_response_hook


class FastApiInstrumentorWrapper(FastAPIInstrumentor):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            server_request_hook=server_request_hook_wrapper(),
            client_request_hook=client_request_hook_wrapper(),
            client_response_hook=client_response_hook_wrapper(),
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()
