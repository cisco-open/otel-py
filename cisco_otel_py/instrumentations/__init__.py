import sys
import traceback
from opentelemetry.trace.span import Span
from cisco_opentelemetry_specifications import SemanticAttributes
from cisco_otel_py.consts import ALLOWED_CONTENT_TYPES
from .utils import lowercase_items, add_attributes_to_span


# This is a base class for all Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    def __init__(self):
        super().__init__()
        self._process_request_headers = False
        self._process_request_body = False
        self.max_payload_size: int = None

    def set_process_request_headers(self, process_request_headers) -> None:
        self._process_request_headers = process_request_headers

    def set_process_request_body(self, process_request_body, max_payload_size) -> None:
        self._process_request_body = process_request_body
        self.max_payload_size = max_payload_size

    # We need the content type to do some escaping
    # so if we return a content type, that indicates valid for capture,
    # otherwise don't capture
    def eligible_based_on_content_type(self, headers: dict):
        """find content-type in headers"""
        content_type = headers.get("content-type")
        return (
            content_type if content_type in ALLOWED_CONTENT_TYPES else None
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

            lowercase_headers = lowercase_items(headers)
            if record_headers:
                add_attributes_to_span(header_prefix, span, lowercase_headers)

            if record_body:
                content_type = self.eligible_based_on_content_type(lowercase_headers)
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

    # Check body size
    def check_body_size(self, body: str) -> bool:
        if body in (None, ""):
            return False
        body_len = len(body)
        max_body_size = self.max_payload_size
        if max_body_size and body_len > max_body_size:
            print(f"Truncating body to {max_body_size} length")
            return True
        return False

    def grab_first_n_bytes(self, body: str) -> str:
        if body in (None, ""):
            return ""
        if self.check_body_size(body):  # pylint: disable=R1705
            return body[0, self.max_payload_size]
        else:
            return body
