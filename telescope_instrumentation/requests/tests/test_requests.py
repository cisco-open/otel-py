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
import requests

from opentelemetry.test.test_base import TestBase

from cisco_opentelemetry_specifications import SemanticAttributes
from telescope_instrumentor.src.configuration import Configuration
from telescope_instrumentation.requests import RequestsInstrumentorWrapper
from telescope_instrumentation.utils.tests.base_http_test import BaseHttpTest


class TestRequestsWrapper(BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        RequestsInstrumentorWrapper().instrument()

    def tearDown(self) -> None:
        super().tearDown()
        RequestsInstrumentorWrapper().uninstrument()
        Configuration().reset_to_default()

    def test_get_request_sanity(self):
        Configuration().payloads_enabled = True
        _ = requests.get(self.http_url_sanity, headers=self.request_headers())
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )
        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            self.response_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY],
            self.response_body(),
        )

    def test_post_request_sanity(self):
        Configuration().payloads_enabled = True
        requests.get(
            self.http_url_sanity,
            headers=self.request_headers(),
            data=self.request_body(),
        ).close()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]
        empty_payload = ""

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_REQUEST_BODY],
            self.request_body(),
        )
        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            self.response_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY],
            self.response_body(),
        )

    def test_get_request_error_response(self):
        Configuration().payloads_enabled = True
        _ = requests.get(self.http_url_error, headers=self.request_headers())
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )

    def test_post_request_error_response(self):
        Configuration().payloads_enabled = True
        requests.post(
            self.http_url_error,
            headers=self.request_headers(),
            data=self.request_body(),
        ).close()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]
        empty_payload = ""

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_REQUEST_BODY],
            self.request_body(),
        )

    def test_post_request_attribute_payloads_enabled(self):
        Configuration().payloads_enabled = True
        requests.get(
            self.http_url_sanity,
            headers=self.request_headers(),
            data=self.request_body(),
        ).close()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_REQUEST_BODY],
            self.request_body(),
        )

    def test_post_request_attribute_payloads_not_enabled(self):
        Configuration().payloads_enabled = False
        requests.get(
            self.http_url_sanity,
            headers=self.request_headers(),
            data=self.request_body(),
        ).close()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]
        empty_payloads = ""

        self.assertNotIn(
            f"{SemanticAttributes.HTTP_REQUEST_HEADER}.test-header-key",
            request_span.attributes,
        )
        self.assertNotIn(
            SemanticAttributes.HTTP_REQUEST_BODY,
            request_span.attributes,
        )
        self.assertNotIn(
            f"{SemanticAttributes.HTTP_RESPONSE_HEADER}.server-response-header",
            request_span.attributes,
        )
        self.assertNotIn(
            SemanticAttributes.HTTP_RESPONSE_BODY,
            request_span.attributes,
        )
