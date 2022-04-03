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
from concurrent import futures
import grpc
from . import hello_pb2
from . import hello_pb2_grpc
from opentelemetry.sdk.trace import ReadableSpan
from cisco_opentelemetry_specifications import SemanticAttributes
import logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)


class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.debug('Received request')
        metadata = (('key1', 'val1'), ('key2', 'val2'))
        logger.debug('Setting custom headers')
        context.set_trailing_metadata(metadata)
        logger.debug('Returning response')
        return hello_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    logger.debug('Creating server')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.debug('Adding GreeterServicer endpoint to server')
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    logger.debug('Adding insecure port')
    server.add_insecure_port('[::]:50051')
    logger.debug('Starting server')
    server.start()
    logger.debug('Waiting for termination')
    return server


def test_grpc(cisco_tracer, exporter):
    serve()

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(hello_pb2.HelloRequest(name='Cisco'))
        assert response.message == 'Hello, Cisco!'
        logger.debug("Greeter client received: " + response.message)
        # Get all the in memory spans that were recorded for this iteration
        spans = exporter.get_finished_spans()
        # Confirm something was returned.
        assert len(spans) == 2
        span: ReadableSpan = spans[0]
        assert span.attributes[f"{SemanticAttributes.RPC_RESPONSE_METADATA.key}.key1"] == "val1"
        assert span.attributes[f"{SemanticAttributes.RPC_RESPONSE_METADATA.key}.key2"] == "val2"
        assert span.attributes[SemanticAttributes.RPC_RESPONSE_BODY.key] == '{"message": "Hello, Cisco!"}'


if __name__ == "__main__":
    unittest.main()
