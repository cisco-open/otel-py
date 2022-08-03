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
import logging

import grpc
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.test.test_base import TestBase

from telescope_instrumentor.configuration import Configuration
from telescope_instrumentation.grpc import (
    GrpcInstrumentorClientWrapper,
    GrpcInstrumentorServerWrapper,
)
from telescope_instrumentation.grpc.tests.unary_unary import server
from telescope_instrumentation.grpc.tests.unary_unary import hello_pb2_grpc, hello_pb2


class TestGrpcInstrumentationWrapper(TestBase):
    def setUp(self) -> None:
        super().setUp()
        GrpcInstrumentorClientWrapper().instrument()
        GrpcInstrumentorServerWrapper().instrument()
        self.server = server.create_server()

    def tearDown(self) -> None:
        super().tearDown()
        self.server.stop(None)
        GrpcInstrumentorClientWrapper().uninstrument()
        GrpcInstrumentorServerWrapper().uninstrument()
        Configuration().reset_to_default()

    def assert_captured_headers(self, span, prefix: str, headers: dict):
        for key, val in headers.items():
            self.assertEqual(span.attributes[f"{prefix}.{key}"], val)

    def test_grpc_instrumentation(self):
        Configuration().payloads_enabled = True
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = hello_pb2_grpc.GreeterStub(channel)
            response, call = stub.SayHello.with_call(
                hello_pb2.HelloRequest(name="Cisco"),
                metadata=(("initial-metadata-1", "some str data"),),
            )
            logging.debug(f"Greeter client received: {response.message}")
            for key, value in call.trailing_metadata():
                logging.debug(
                    f"Greeter client received trailing metadata: key={key} value={value}"
                )

            # Get all the in memory spans that were recorded for this iteration
            spans = self.memory_exporter.get_finished_spans()
            # Confirm something was returned.
            self.assertEqual(len(spans), 2)
            server_span: ReadableSpan = spans[0]

            self.assert_captured_headers(
                server_span,
                SemanticAttributes.RPC_RESPONSE_METADATA,
                {"key1": "val1", "key2": "val2"},
            )

            self.assertEqual(
                server_span.attributes[SemanticAttributes.RPC_RESPONSE_BODY],
                '{"message": "Hello, Cisco!"}',
            )

            client_span: ReadableSpan = spans[1]
            self.assertEqual(
                client_span.attributes[SemanticAttributes.RPC_REQUEST_BODY],
                'name: "Cisco"\n',
            )

            self.assert_captured_headers(
                client_span,
                SemanticAttributes.RPC_REQUEST_METADATA,
                {"initial-metadata-1": "some str data"},
            )

    def test_grpc_instrumentation_payloads_not_enabled(self):
        Configuration().payloads_enabled = False
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = hello_pb2_grpc.GreeterStub(channel)
            response, call = stub.SayHello.with_call(
                hello_pb2.HelloRequest(name="Cisco"),
                metadata=(("initial-metadata-1", "some str data"),),
            )
            logging.debug(f"Greeter client received: {response.message}")
            for key, value in call.trailing_metadata():
                logging.debug(
                    f"Greeter client received trailing metadata: key={key} value={value}"
                )

            # Get all the in memory spans that were recorded for this iteration
            spans = self.memory_exporter.get_finished_spans()
            # Confirm something was returned.
            self.assertEqual(len(spans), 2)
            empty_payloads = ""

            client_span: ReadableSpan = spans[1]
            self.assertNotIn(
                SemanticAttributes.RPC_REQUEST_BODY,
                client_span.attributes,
            )

            self.assertNotIn(  # payloads_enabled=False
                f"{SemanticAttributes.RPC_REQUEST_METADATA}.initial-metadata-1",
                client_span.attributes,
            )
