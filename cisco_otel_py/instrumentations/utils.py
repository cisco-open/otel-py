from typing import AnyStr
from opentelemetry.trace.span import Span

from .. import consts


class Utils(object):
    @staticmethod
    def set_payload(
        span: Span,
        attr_key: str,
        attr_sampling_relevant: bool,
        payload: AnyStr,
        payloads_enabled: bool,
        max_payload_size: int,
    ):
        payload_decoded = ""

        if payloads_enabled or attr_sampling_relevant:
            if isinstance(payload, bytes):
                payload_decoded = payload.decode(
                    consts.ENCODING_UTF8, consts.DECODE_PAYLOAD_IN_CASE_OF_ERROR
                )
            else:
                payload_decoded = payload or ""

        span.set_attribute(attr_key, payload_decoded[:max_payload_size])

    @staticmethod
    def lowercase_items(items: dict):
        return {k.lower(): v for k, v in items.items()}

    @staticmethod
    def add_flattened_dict(span: Span, prefix, attributes: dict):
        """Add Dictionary to Span as flattened labels with lower cased key values"""
        for attribute_key, attribute_value in Utils.lowercase_items(attributes).items():
            span.set_attribute(f"{prefix}.{attribute_key}", attribute_value)
