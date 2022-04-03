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
import json
import unittest

from opentelemetry.sdk.trace import ReadableSpan
from cisco_opentelemetry_specifications import SemanticAttributes

from requests import get, post


def test_http_request_headers(cisco_tracer, exporter):
    get(
        url="https://google.com/",
        headers={"test-header-key": "test-header-value"},
    )

    spans = exporter.get_finished_spans()
    assert len(spans) >= 1

    for span in spans:
        if (
            f"{SemanticAttributes.HTTP_REQUEST_HEADER.key}.test-header-key"
            not in span.attributes
        ):
            continue
        custom_attribute_value = span.attributes[
            f"{SemanticAttributes.HTTP_REQUEST_HEADER.key}.test-header-key"
        ]
        assert custom_attribute_value == "test-header-value"
        return
    assert 1 == 0  # fail if loop hasn't reach relevant span


def test_http_request_body(cisco_tracer, exporter):
    post("https://google.com/", json={"test-key": "test-value"})

    spans = exporter.get_finished_spans()
    assert len(spans) >= 1

    for span in spans:
        if f"{SemanticAttributes.HTTP_REQUEST_BODY.key}" not in span.attributes:
            continue
        assert f"{SemanticAttributes.HTTP_REQUEST_BODY.key}" in span.attributes

        request_body = json.loads(
            span.attributes[f"{SemanticAttributes.HTTP_REQUEST_BODY.key}"]
        )

        assert request_body["test-key"] == "test-value"
        return
    assert 1 == 0  # fail if loop hasn't reach relevant span


if __name__ == "__main__":
    unittest.main()
