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
import grpc

from opentelemetry.test.test_base import TestBase
from opentelemetry.sdk.trace import ReadableSpan
from cisco_opentelemetry_specifications import SemanticAttributes

from . import server
from . import hello_pb2, hello_pb2_grpc

from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorClientWrapper
from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorServerWrapper


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

    def test_grpc_instrumentation(self):
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = hello_pb2_grpc.GreeterStub(channel)
            _ = stub.SayHello(hello_pb2.HelloRequest(name="Cisco"))

            # Get all the in memory spans that were recorded for this iteration
            spans = self.memory_exporter.get_finished_spans()
            # Confirm something was returned.
            self.assertEqual(len(spans), 2)
            server_span: ReadableSpan = spans[0]

            self.assertEqual(
                server_span.attributes[f"{SemanticAttributes.RPC_RESPONSE_METADATA.key}.key1"], "val1"
            )

            self.assertEqual(
                server_span.attributes[f"{SemanticAttributes.RPC_RESPONSE_METADATA.key}.key2"], "val2"
            )

            self.assertEqual(
                server_span.attributes[SemanticAttributes.RPC_RESPONSE_BODY.key],
                '{"message": "Hello, Cisco!"}'
            )
