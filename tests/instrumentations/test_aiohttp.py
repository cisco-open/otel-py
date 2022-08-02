"""Copyright The Cisco Authors.

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
from __future__ import annotations

import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase

import aiohttp
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.test.test_base import TestBase

from cisco_telescope.configuration import Configuration
from cisco_telescope.instrumentations.aiohttp import AiohttpInstrumentorWrapper
from tests.instrumentations.base_http_tests_util import BaseHttpTest


class TestAiohttpWrapper(IsolatedAsyncioTestCase, BaseHttpTest, TestBase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        AiohttpInstrumentorWrapper().instrument()
        await asyncio.sleep(3)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        AiohttpInstrumentorWrapper().uninstrument()
        Configuration().reset_to_default()

    async def test_get_request_sanity(self):
        async with aiohttp.client.request(
            method="GET",
            url=self.http_url_sanity,
            headers=self.request_headers(),
            chunked=True,
        ) as resp:
            self._assert_basic_attributes_and_headers(resp)

    async def test_post_request_sanity(self):
        Configuration().payloads_enabled = True
        async with aiohttp.client.request(
            method="POST",
            url=self.http_url_sanity,
            headers=self.request_headers(),
            chunked=True,
            data=self.request_body(),
        ) as resp:
            self._assert_basic_attributes_and_headers(resp)
            spans = self.memory_exporter.get_finished_spans()
            span = spans[0]

            self.assertEqual(
                span.attributes[SemanticAttributes.HTTP_REQUEST_BODY],
                self.request_body(),
            )
            self.assertEqual(
                span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY],
                self.response_body(),
            )

    async def test_post_request_invalid_utf8(self):
        Configuration().payloads_enabled = True
        with self.assertLogs() as logs_written:
            data_to_send = b'/">Miso\xdfNoContinuation'
            async with aiohttp.client.request(
                method="POST",
                url=self.http_url_sanity,
                headers=self.request_headers(),
                chunked=True,
                data=data_to_send,
            ) as resp:
                self._assert_basic_attributes_and_headers(resp)
                spans = self.memory_exporter.get_finished_spans()
                span = spans[0]

                self.assertEqual(
                    span.attributes[SemanticAttributes.HTTP_REQUEST_BODY],
                    str(data_to_send),
                )
                self.assertEqual(
                    span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY],
                    self.response_body(),
                )
                self.assertEqual(len(logs_written.records), 1)

    async def test_get_request_error(self):
        Configuration().payloads_enabled = True
        async with aiohttp.client.request(
            method="GET", url=self.http_url_error, headers=self.request_headers()
        ) as resp:
            self.assertEqual(resp.status, 404)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            request_span = spans[0]
            self.assert_captured_headers(
                request_span,
                SemanticAttributes.HTTP_REQUEST_HEADER,
                self.request_headers(),
            )

    async def test_post_request_error(self):
        Configuration().payloads_enabled = True
        async with aiohttp.client.request(
            method="POST", url=self.http_url_error, headers=self.request_headers()
        ) as resp:
            self.assertEqual(resp.status, 404)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            request_span = spans[0]
            self.assert_captured_headers(
                request_span,
                SemanticAttributes.HTTP_REQUEST_HEADER,
                self.request_headers(),
            )

    async def test_post_request_payloads_not_enabled(self):
        Configuration().payloads_enabled = False
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
            self.assertNotIn(
                f"{SemanticAttributes.HTTP_REQUEST_HEADER}.test-header-key",
                request_span.attributes,
            )
            self.assertNotIn(
                f"{SemanticAttributes.HTTP_RESPONSE_HEADER}.server-response-header",
                request_span.attributes,
            )

    async def test_response_content_unharmed(self):
        Configuration().payloads_enabled = True
        async with aiohttp.client.request(
            method="POST",
            url=self.http_url_sanity,
            headers=self.request_headers(),
            chunked=True,
            data=self.request_body(),
        ) as resp:
            self.assertEqual(resp.status, 200)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[0]
            self.assertEqual(hasattr(resp, "content"), True)
            self.assertIsNotNone(resp.content)
            resp_body = ""
            while not resp.content.at_eof():
                response_chunk = b""
                response_chunk = await asyncio.wait_for(resp.content.read(), 0.1)
                resp_body += response_chunk.decode()
            self.assertEqual(self.response_body(), resp_body)
            self.assertEqual(
                span.attributes[SemanticAttributes.HTTP_RESPONSE_BODY],
                resp_body,
            )

    def _assert_basic_attributes_and_headers(self, resp):
        self.assertEqual(resp.status, 200)
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        span = spans[0]
        self.assertEqual(span.attributes[SpanAttributes.HTTP_METHOD], resp.method)
        self.assertEqual(span.attributes[SpanAttributes.HTTP_URL], str(resp.url))
        self.assert_captured_headers(
            span,
            SemanticAttributes.HTTP_REQUEST_HEADER,
            self.request_headers(),
        )
        self.assert_captured_headers(
            span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            self.response_headers(),
        )
