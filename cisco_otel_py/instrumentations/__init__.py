import sys
import traceback
from opentelemetry.trace.span import Span
from cisco_opentelemetry_specifications import SemanticAttributes


# This is a base class for all Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    def __init__(self):
        super().__init__()
        self._process_request_headers = False
        self._process_response_headers = False
        self._process_request_body = False
        self._process_response_body = False
        self._max_body_size = 128 * 1024

    def set_process_request_headers(self, process_request_headers) -> None:
        self._process_request_headers = process_request_headers

    def set_process_request_body(self, process_request_body) -> None:
        self._process_request_body = process_request_body

    # Set max body size
    def set_body_max_size(self, max_body_size) -> None:
        self._max_body_size = max_body_size

    # we need the headers lowercased multiple times
    # just do it once upfront
    def lowercase_headers(self, headers):  # pylint:disable=R0201
        return {k.lower(): v for k, v in headers.items()}

    def add_headers_to_span(
        self, prefix: str, span: Span, headers: dict
    ):  # pylint:disable=R0201
        """set header attributes on the span"""
        for header_key, header_value in headers.items():
            span.set_attribute(f"{prefix}{header_key}", header_value)

    _ALLOWED_CONTENT_TYPES = [
        "application/json",
        "application/graphql",
        "application/x-www-form-urlencoded",
    ]

    # We need the content type to do some escaping
    # so if we return a content type, that indicates valid for capture,
    # otherwise don't capture
    def eligible_based_on_content_type(self, headers: dict):
        """find content-type in headers"""
        content_type = headers.get("content-type")
        return (
            content_type if content_type in self._ALLOWED_CONTENT_TYPES else None
        )  # plyint:disable=R1710

    def _generic_handler(
        self,
        record_headers: bool,
        header_prefix: str,  # pylint:disable=R0913
        record_body: bool,
        body_prefix: str,
        span: Span,
        headers: dict,
        body,
    ):
        try:  # pylint: disable=R1702
            if not span.is_recording():
                return span

            lowercased_headers = self.lowercase_headers(headers)
            if record_headers:
                self.add_headers_to_span(header_prefix, span, lowercased_headers)

            if record_body:
                content_type = self.eligible_based_on_content_type(lowercased_headers)
                if content_type is None:
                    return span

                body_str = None
                if isinstance(body, bytes):
                    body_str = body.decode("UTF8", "backslashreplace")
                else:
                    body_str = body

                request_body_str = self.grab_first_n_bytes(body_str)
                span.set_attribute(body_prefix, request_body_str)

        except:  # pylint: disable=W0702
            print(
                "An error occurred in genericRequestHandler: exception=%s, stacktrace=%s",
                sys.exc_info()[0],
                traceback.format_exc(),
            )
        finally:
            return span  # pylint: disable=W0150

    # Generic HTTP Request Handler
    def generic_request_handler(
        self, request_headers: dict, request_body, span: Span  # pylint: disable=R0912
    ) -> Span:
        return self._generic_handler(
            self._process_request_headers,
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            self._process_request_body,
            SemanticAttributes.HTTP_REQUEST_BODY.key,
            span,
            request_headers,
            request_body,
        )

    # Generic HTTP Response Handler
    def generic_response_handler(
        self, response_headers: dict, response_body, span: Span  # pylint: disable=R0912
    ) -> Span:  # pylint: disable=R0912
        return self._generic_handler(
            self._process_response_headers,
            SemanticAttributes.HTTP_RESPONSE_HEADER.key,
            self._process_response_body,
            SemanticAttributes.HTTP_RESPONSE_BODY.key,
            span,
            response_headers,
            response_body,
        )

    # Check body size
    def check_body_size(self, body: str) -> bool:
        if body in (None, ""):
            return False
        body_len = len(body)
        max_body_size = self._max_body_size
        if max_body_size and body_len > max_body_size:
            print("message body size is greater than max size.")
            return True
        return False

    def grab_first_n_bytes(self, body: str) -> str:
        if body in (None, ""):
            return ""
        if self.check_body_size(body):  # pylint: disable=R1705
            return body[0, self._max_body_size]
        else:
            return body
