"""Filter abstract base class for blocking"""
from abc import ABC, abstractmethod
from opentelemetry.trace.span import Span


class Filter(ABC):
    """
    Filter evaluates whether request should be blocked, True blocks the request and False
    continues it.
    """
    @abstractmethod
    def evaluate_url_and_headers(self, span: Span, url: str, headers: dict, request_type) -> bool:
        """evaluate_url_and_headers can be used to evaluate both URL and Header"""

    @abstractmethod
    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        """evaluate_body can be used to evaluate the body content"""


class NoopFilter(Filter):
    """NoopFilter is a filter that never blocks"""

    def evaluate_url_and_headers(self, span: Span, url: str, headers: dict, request_type) -> bool:
        return False

    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        return False
