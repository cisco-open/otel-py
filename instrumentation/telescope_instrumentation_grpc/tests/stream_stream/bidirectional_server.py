from concurrent import futures

import grpc

from instrumentation.telescope_instrumentation_grpc.tests.stream_stream import (
    bidirectional_pb2_grpc,
)


class BidirectionalService(bidirectional_pb2_grpc.BidirectionalServicer):
    def SendMessage(self, request_iterator, context):
        for key, value in context.invocation_metadata():
            print(
                "bidirectional. received initial metadata: key=%s value=%s"
                % (key, value)
            )
        context.set_trailing_metadata((("key1", "val1"), ("key2", "val2")))
        for message in request_iterator:
            yield message


def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bidirectional_pb2_grpc.add_BidirectionalServicer_to_server(
        BidirectionalService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    return server
