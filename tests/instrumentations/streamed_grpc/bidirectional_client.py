# from __future__ import print_function
#
# import grpc
# from tests.instrumentations.streamed_grpc import bidirectional_pb2_grpc
# from tests.instrumentations.streamed_grpc import bidirectional_pb2
# from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorClientWrapper
# from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
#     InMemorySpanExporter,
# )
# from opentelemetry.sdk.trace import TracerProvider, export
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
# def run():
#     GrpcInstrumentorClientWrapper().instrument()
#     tracer_provider = TracerProvider()
#     memory_exporter = InMemorySpanExporter()
#     span_processor = export.SimpleSpanProcessor(memory_exporter)
#     tracer_provider.add_span_processor(span_processor)
#
#     with grpc.insecure_channel("localhost:50051") as channel:
#         stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
#         send_message(stub)
#     spans = memory_exporter.get_finished_spans()
#     print(len(spans))
#
#
# if __name__ == "__main__":
#     run()
