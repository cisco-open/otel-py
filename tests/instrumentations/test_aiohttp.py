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

    @classmethod
    def request_headers(cls) -> dict[str, str]:
        return {"test-header-key": "test-header-value"}

    async def test_get_request_sanity(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.http_url_sanity, headers=self.request_headers()
            ):
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

    @pytest.fixture
    async def client(self, db_path: Path) -> _TestClient:
        app = await init_app(db_path)
        return await aiohttp_client(app)

    async def test_list_empty(self) -> None:
        resp = await client.get(self.http_url_sanity)
        assert resp.status == 200, await resp.text()
        data = await resp.json()
        assert data == {"data": [], "status": "ok"}
        assert 2 == 1


if __name__ == "__main__":
    unittest.main()
