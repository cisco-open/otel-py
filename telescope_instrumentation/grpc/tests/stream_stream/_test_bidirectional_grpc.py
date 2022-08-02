# from __future__ import print_function
#
# import grpc
#
# from tests.telescope_instrumentation.grpc.stream_stream import (
#     bidirectional_pb2_grpc,
#     bidirectional_pb2,
#     bidirectional_server,
# )
# from telescope_instrumentor.telescope_instrumentation.grpc import GrpcInstrumentorClientWrapper
# from telescope_instrumentor.telescope_instrumentation.grpc import GrpcInstrumentorServerWrapper
#
# from opentelemetry.test.test_base import TestBase
#
#
# def make_message(message):
#     return bidirectional_pb2.Message(message=message)
#
#
# def generate_messages():
#     messages = [
#         make_message("First message"),
#         make_message("Second message"),
#         make_message("Third message"),
#         make_message("Fourth message"),
#         make_message("Fifth message"),
#     ]
#     for msg in messages:
#         print("Hello Server Sending you the %s" % msg.message)
#         yield msg
#
#
# def send_message(stub):
#     responses = stub.SendMessage(
#         generate_messages(),
#         metadata=(("initial-metadata-1", "some str data"),),
#     )
#     for response in responses:
#         print("Hello from the server received your %s" % response.message)
#
#
# class TestGrpcStreamInstrumentationWrapper(TestBase):
#     def setUp(self) -> None:
#         super().setUp()
#         GrpcInstrumentorClientWrapper().instrument()
#         GrpcInstrumentorServerWrapper().instrument()
#         self.server = bidirectional_server.create_server()
#
#     def tearDown(self) -> None:
#         super().tearDown()
#         self.server.stop(None)
#         GrpcInstrumentorClientWrapper().uninstrument()
#         GrpcInstrumentorServerWrapper().uninstrument()
#
#     def test_grpc_stream_instrumentation(self):
#         with grpc.insecure_channel("localhost:50051") as channel:
#             stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
#             send_message(stub)
#         spans = self.memory_exporter.get_finished_spans()
#         print(len(spans))
#         # TODO: finish the instrumentation so that the body and metadata will be seen in the span
#         # and then add "assert" to check if the required attributes are in the span
