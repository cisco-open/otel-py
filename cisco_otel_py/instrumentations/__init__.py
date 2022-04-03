import sys
import traceback
from opentelemetry.trace.span import Span
from cisco_opentelemetry_specifications import SemanticAttributes
from cisco_otel_py.consts import ALLOWED_CONTENT_TYPES
from .utils import lowercase_items, add_attributes_to_span


# This is a base class for all Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    RPC_REQUEST_METADATA_PREFIX = 'rpc.request.metadata.'
    RPC_REQUEST_BODY_PREFIX = 'rpc.request.body'
    RPC_RESPONSE_METADATA_PREFIX = 'rpc.response.metadata.'
    RPC_RESPONSE_BODY_PREFIX = 'rpc.response.body'

    def __init__(self):
        super().__init__()
        self.max_payload_size: int = None

    def set_payload_max_size(self, max_payload_size) -> None:
        print('Setting self.body_max_size to %s.' % max_payload_size)
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
        header_prefix: str,  # pylint:disable=R0913
        body_prefix: str,
        span: Span,
        headers: dict,
        body,
    ):
        try:  # pylint: disable=R1702
            if not span.is_recording():
                return span

            # Add headers
            lowercase_headers = lowercase_items(headers)
            add_attributes_to_span(header_prefix, span, lowercase_headers)

            # Add body
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
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            SemanticAttributes.HTTP_REQUEST_BODY.key,
            span,
            request_headers,
            request_body,
        )

    # Generic RPC Request Handler
    def generic_rpc_request_handler(self,
                                    request_headers: dict,
                                    request_body,
                                    span: Span) -> Span:
        """Add extended request rpc data to span."""
        print('Entering BaseInstrumentationWrapper.genericRpcRequestHandler().')
        try:
            # Is the span currently recording?
            if not span.is_recording():
                return span

            print('Span is Recording!')
            lowercased_headers = lowercase_items(request_headers)

            # Add rpc request metadata
            add_attributes_to_span(self.RPC_REQUEST_METADATA_PREFIX, span, lowercased_headers)
            # Add rpc response body
            request_body_str = str(request_body)
            request_body_str = self.grab_first_n_bytes(request_body_str)
            span.set_attribute(self.RPC_REQUEST_BODY_PREFIX, request_body_str)
        except:  # pylint: disable=W0702
            print('An error occurred in genericRequestHandler: exception=%s, stacktrace=%s',
                  sys.exc_info()[0],
                  traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span  # pylint: disable=W0150

    # Generic RPC Response Handler
    def generic_rpc_response_handler(self,
                                     response_headers: dict,
                                     response_body,
                                     span: Span) -> Span:
        """Add extended response rpc data to span"""
        print('Entering BaseInstrumentationWrapper.genericRpcResponseHandler().')
        try:
            # is the span currently recording?
            if not span.is_recording():
                return span

            print('Span is Recording!')
            # Add rpc metadata
            print('Add Response Headers:')
            lowercased_headers = lowercase_items(response_headers)
            add_attributes_to_span(self.RPC_RESPONSE_METADATA_PREFIX, span, lowercased_headers)

            # Add rpc body
            response_body_str = str(response_body)
            print('Processing response body')
            response_body_str = self.grab_first_n_bytes(response_body_str)
            span.set_attribute(self.RPC_RESPONSE_BODY_PREFIX, response_body_str)
        except:  # pylint: disable=W0702
            print('An error occurred in genericResponseHandler: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors
        finally:
            return span  # pylint: disable=W0150


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
