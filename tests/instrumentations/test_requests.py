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
import unittest
import requests


from opentelemetry.test.test_base import TestBase

from cisco_opentelemetry_specifications import SemanticAttributes
from cisco_otel_py.instrumentations.requests import RequestsInstrumentorWrapper
from .base_http_test import BaseHttpTest


class TestRequestsWrapper(BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        RequestsInstrumentorWrapper().instrument()

    def tearDown(self) -> None:
        super().tearDown()
        RequestsInstrumentorWrapper().uninstrument()

    def test_get_request_sanity(self):
        _ = requests.get(self.http_url_sanity, headers=self.request_headers())
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            self.request_headers(),
        )
        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_RESPONSE_HEADER.key,
            self.response_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY.key],
            self.response_body(),
        )

    def test_post_request_sanity(self):
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
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            self.request_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_REQUEST_BODY.key],
            self.request_body(),
        )
        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_RESPONSE_HEADER.key,
            self.response_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY.key],
            self.response_body(),
        )

    def test_get_request_error_response(self):
        _ = requests.get(self.http_url_error, headers=self.request_headers())
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            self.request_headers(),
        )

    def test_post_request_error_response(self):
        requests.post(
            self.http_url_error,
            headers=self.request_headers(),
            data=self.request_body(),
        ).close()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        request_span = spans[0]

        self.assert_captured_headers(
            request_span,
            SemanticAttributes.HTTP_REQUEST_HEADER.key,
            self.request_headers(),
        )
        self.assertEqual(
            request_span.attributes[SemanticAttributes.HTTP_REQUEST_BODY.key],
            self.request_body(),
        )
