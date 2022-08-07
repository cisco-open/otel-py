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
import fastapi
import json
from fastapi.testclient import TestClient

from opentelemetry.test.test_base import TestBase
from cisco_telescope.configuration import Configuration
from instrumentation.telescope_instrumentaion_fastapi import FastApiInstrumentorWrapper
from instrumentation.telescope_instrumentation_utils.base_http_tests_util import (
    BaseHttpTest,
)


class TestFastApiWrapper(BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        FastApiInstrumentorWrapper().instrument()
        self.app = self.create_fastapi_app()
        self.client = TestClient(self.app)
        self.body = {"message": "hello world"}

    def tearDown(self) -> None:
        super().tearDown()
        FastApiInstrumentorWrapper().uninstrument()
        Configuration().reset_to_default()

    def create_fastapi_app(self):
        app = fastapi.FastAPI()

        @app.get("/test")
        async def _():
            return self.body

        return app

    @staticmethod
    def verify_captured_attributes(spans: list, attributes: dict):
        all_attribute_exist = False

        for span in spans:
            if attributes.items() <= span.attributes.items():
                all_attribute_exist = True

        return all_attribute_exist

    def test_fastapi_instrument(self):
        self.client.get("/test")
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 3)

        expected_request_body_string = json.dumps(self.body, separators=(",", ":"))

        expected_client_response_attributes = {
            "http.request.body": expected_request_body_string
        }

        expected_client_response2_attributes = {
            "http.response.header.content-length": str(
                len(expected_request_body_string)
            ),
            "http.response.header.content-type": "application/json",
        }

        expected_server_request_attributes = {
            "http.request.header.host": "testserver",
            "http.request.header.user-agent": self.client.headers["user-agent"],
            "http.request.header.accept-encoding": self.client.headers[
                "Accept-Encoding"
            ],
            "http.request.header.accept": self.client.headers["Accept"],
            "http.request.header.connection": self.client.headers["Connection"],
        }

        expected_traces_attributes_list = [
            expected_client_response_attributes,
            expected_client_response2_attributes,
            expected_server_request_attributes,
        ]

        for attributes in expected_traces_attributes_list:
            self.assertTrue(self.verify_captured_attributes(spans, attributes))
