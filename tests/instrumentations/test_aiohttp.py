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

import aiohttp

from opentelemetry.test.test_base import TestBase
from unittest import IsolatedAsyncioTestCase

from cisco_opentelemetry_specifications import SemanticAttributes
from cisco_otel_py.instrumentations.aiohttp import AiohttpInstrumentorWrapper
from .base_http_test import BaseHttpTest


class TestRequestsWrapper(IsolatedAsyncioTestCase, BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        AiohttpInstrumentorWrapper().instrument()

    def tearDown(self) -> None:
        super().tearDown()
        AiohttpInstrumentorWrapper().uninstrument()

    async def test_get_request_sanity(self):
        async with aiohttp.client.request(
            method="GET", url=self.http_url_sanity, headers=self.request_headers()
        ) as resp:
            self.assertEqual(resp.status, 200)
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

    async def test_post_request_sanity(self):
        async with aiohttp.client.request(
            method="POST",
            url=self.http_url_sanity,
            headers=self.request_headers(),
            data=self.request_body(),
        ) as resp:
            self.assertEqual(resp.status, 200)
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

    async def test_get_request_error(self):
        async with aiohttp.client.request(
            method="GET", url=self.http_url_error, headers=self.request_headers()
        ) as resp:
            self.assertEqual(resp.status, 404)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            request_span = spans[0]
            self.assert_captured_headers(
                request_span,
                SemanticAttributes.HTTP_REQUEST_HEADER.key,
                self.request_headers(),
            )

    async def test_post_request_error(self):
        async with aiohttp.client.request(
            method="POST", url=self.http_url_error, headers=self.request_headers()
        ) as resp:
            self.assertEqual(resp.status, 404)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            request_span = spans[0]
            self.assert_captured_headers(
                request_span,
                SemanticAttributes.HTTP_REQUEST_HEADER.key,
                self.request_headers(),
            )


if __name__ == "__main__":
    unittest.main()