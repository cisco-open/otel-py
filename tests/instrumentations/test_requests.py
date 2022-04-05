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
from opentelemetry.test.httptest import HttpTestBase

from cisco_opentelemetry_specifications import SemanticAttributes

from cisco_otel_py.instrumentations.requests import RequestsInstrumentorWrapper
from .base_http_test import BaseHttpTest


class TestRequestsWrapper(BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        self.assert_ip = self.server.server_address[0]
        self.http_host = ":".join(map(str, self.server.server_address[:2]))
        self.http_url_base = "http://" + self.http_host
        self.http_url = self.http_url_base + "/status/200"
        temp_shit = RequestsInstrumentorWrapper()
        temp_shit.instrument()

    def tearDown(self) -> None:
        super().tearDown()
        RequestsInstrumentorWrapper().uninstrument()

    @classmethod
    def request_headers(cls) -> dict[str, str]:
        return {"test-header-key": "test-header-value"}

    @staticmethod
    def perform_request(url: str) -> requests.Response:
        return requests.get(url, stream=True)

    def test_get_request(self):
        response = self.perform_request(self.http_url)
        spans = self.memory_exporter.get_finished_spans()
        print(spans[0].to_json())


if __name__ == "__main__":
    unittest.main()
