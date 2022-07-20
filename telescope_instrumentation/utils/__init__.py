"""
Copyright The Cisco Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import AnyStr
from opentelemetry.trace.span import Span
from cisco_opentelemetry_specifications.payload_attributes import PAYLOAD_ATTRIBUTES
from telescope_instrumentor.configuration import Configuration
from telescope_instrumentor import consts


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
    def lowercase_items(items: dict):
        return {k.lower(): v for k, v in items.items()}

    @staticmethod
    def add_flattened_dict(span: Span, prefix, attributes: dict):
        """Add Dictionary to Span as flattened labels with lower cased key values"""
        payloads_enabled = Configuration().payloads_enabled
        if payloads_enabled or (prefix not in PAYLOAD_ATTRIBUTES):
            for attribute_key, attribute_value in Utils.lowercase_items(
                attributes
            ).items():
                span.set_attribute(f"{prefix}.{attribute_key}", attribute_value)
