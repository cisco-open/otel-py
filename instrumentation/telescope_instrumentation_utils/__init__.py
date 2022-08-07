from typing import AnyStr

from opentelemetry.trace.span import Span

from cisco_telescope import consts
from cisco_telescope.configuration import Configuration
from cisco_opentelemetry_specifications.payload_attributes import PAYLOAD_ATTRIBUTES


class Utils(object):
    @staticmethod
    def set_payload(
        span: Span,
        attr: str,
        payload: AnyStr,
    ):
        payload_decoded = payload or ""
        payloads_enabled = Configuration().payloads_enabled
        max_payload_size = Configuration().max_payload_size

        if payloads_enabled or (attr not in PAYLOAD_ATTRIBUTES):
            if isinstance(payload, bytes):
                payload_decoded = payload.decode(
                    consts.ENCODING_UTF8, consts.DECODE_PAYLOAD_IN_CASE_OF_ERROR
                )

            span.set_attribute(attr, payload_decoded[:max_payload_size])

    @staticmethod
    def add_flattened_dict(span: Span, prefix, attributes: dict):
        """Add Dictionary to Span as flattened labels with lower cased key
        values."""
        payloads_enabled = Configuration().payloads_enabled
        if payloads_enabled or (prefix not in PAYLOAD_ATTRIBUTES):
            for attribute_key, attribute_value in attributes.items():

                attribute_key = attribute_key.lower()

                if isinstance(attribute_key, bytes):
                    attribute_key = attribute_key.decode(
                        consts.ENCODING_UTF8, consts.DECODE_PAYLOAD_IN_CASE_OF_ERROR
                    )

                if isinstance(attribute_value, bytes):
                    attribute_value = attribute_value.decode(
                        consts.ENCODING_UTF8, consts.DECODE_PAYLOAD_IN_CASE_OF_ERROR
                    )

                span.set_attribute(f"{prefix}.{attribute_key}", attribute_value)
