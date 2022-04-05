import sys
import traceback
from opentelemetry.trace.span import Span
from cisco_opentelemetry_specifications import SemanticAttributes
from cisco_otel_py.consts import ALLOWED_CONTENT_TYPES
from .utils import lowercase_items, add_attributes_to_span
from cisco_otel_py import consts


# This is a base class for all Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    def __init__(self):
        super().__init__()
        self.max_payload_size: int = 0

    def set_payload_max_size(self, max_payload_size) -> None:
        print("Setting self.max_payload_size to %s." % max_payload_size)
        self.max_payload_size = max_payload_size

    # We need the content type to do some escaping
    # so if we return a content type, that indicates valid for capture,
    # otherwise don't capture
    def eligible_based_on_content_type(self, headers: dict):
        """find content-type in headers"""
        content_type = headers.get("content-type")
        return (
            content_type if content_type in ALLOWED_CONTENT_TYPES else None
        )

    def _generic_handler(
        self,
        header_prefix: str,
        body_prefix: str,
        span: Span,
        headers: dict,
        body,
    ):
        try:
            if not span.is_recording():
                return span

            # Add headers
            lowercase_headers = lowercase_items(headers)
            add_attributes_to_span(header_prefix, span, lowercase_headers)

            # Add body
            content_type = self.eligible_based_on_content_type(lowercase_headers)
            if content_type is None:
                return span

            if isinstance(body, bytes):
                body_str = body.decode(
                    consts.ENCODING_UTF8, consts.DECODE_RESPONSE_IN_CASE_OF_ERROR
                )
            else:
                body_str = body

            request_body_str = self.grab_first_n_bytes(body_str)
            span.set_attribute(body_prefix, request_body_str)

        except:
            print(
                "An error occurred in genericRequestHandler: exception=%s, stacktrace=%s"
                % (sys.exc_info()[0], traceback.format_exc())
            )
        finally:
            return span

    # Generic HTTP Request Handler
    def generic_request_handler(
            self, request_headers: dict, request_body, span: Span
    ) -> Span:
        return self._generic_handler(
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            SemanticAttributes.HTTP_REQUEST_BODY.key,
            span,
            request_headers,
            request_body,
        )

    def generic_response_handler(
            self, response_headers: dict, response_body, span: Span
    ) -> Span:
        return self._generic_handler(
            SemanticAttributes.HTTP_RESPONSE_HEADER.key,
            SemanticAttributes.HTTP_RESPONSE_BODY.key,
            span,
            response_headers,
            response_body,
        )

    # Generic RPC Request Handler
    def generic_rpc_request_handler(
            self, request_headers: dict, request_body, span: Span
    ) -> Span:
        """Add extended request rpc data to span."""
        print("Entering BaseInstrumentationWrapper.genericRpcRequestHandler().")
        try:
            # Is the span currently recording?
            if not span.is_recording():
                return span
            print("Span is Recording!")

            # Add rpc request metadata
            lowercased_headers = lowercase_items(request_headers)
            add_attributes_to_span(
                SemanticAttributes.RPC_REQUEST_METADATA.key, span, lowercased_headers
            )

            # Add rpc response body
            request_body_str = str(request_body)
            request_body_str = self.grab_first_n_bytes(request_body_str)
            span.set_attribute(
                SemanticAttributes.RPC_REQUEST_BODY.key, request_body_str
            )
        except:
            print(
                "An error occurred in genericRequestHandler: exception=%s, stacktrace=%s"
                % (sys.exc_info()[0], traceback.format_exc())
            )
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span

    # Generic RPC Response Handler
    def generic_rpc_response_handler(
            self, response_headers: dict, response_body, span: Span
    ) -> Span:
        """Add extended response rpc data to span"""
        print("Entering BaseInstrumentationWrapper.genericRpcResponseHandler().")
        try:
            # is the span currently recording?
            if not span.is_recording():
                return span
            print("Span is Recording!")

            # Add rpc metadata
            print("Add Response Headers:")
            lowercased_headers = lowercase_items(response_headers)
            add_attributes_to_span(
                SemanticAttributes.RPC_RESPONSE_METADATA.key, span, lowercased_headers
            )

            # Add rpc body
            response_body_str = str(response_body)
            print("Processing response body")
            response_body_str = self.grab_first_n_bytes(response_body_str)
            span.set_attribute(
                SemanticAttributes.RPC_RESPONSE_BODY.key, response_body_str
            )
        except:
            print(
                "An error occurred in genericResponseHandler: exception=%s, stacktrace=%s"
                % (sys.exc_info()[0], traceback.format_exc())
            )
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span

    # Check body size
    def check_body_size(self, body: str) -> bool:
        if body in (None, ""):
            return False
        body_len = len(body)
        if self.max_payload_size and body_len > self.max_payload_size:
            print(f"Truncating body to {self.max_payload_size} length")
            return True
        return False

    def grab_first_n_bytes(self, body: str) -> str:
        if body in (None, ""):
            return ""
        if self.check_body_size(body):
            return body[0, self.max_payload_size]
        else:
            return body
