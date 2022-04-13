from concurrent import futures

import grpc
from tests.instrumentations.streamed_grpc import bidirectional_pb2_grpc
from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorServerWrapper


class BidirectionalService(bidirectional_pb2_grpc.BidirectionalServicer):

    def SendMessage(self, request_iterator, context):
        for key, value in context.invocation_metadata():
            print("bidirectional. received initial metadata: key=%s value=%s" % (key, value))
        context.set_trailing_metadata((("key1", "val1"), ("key2", "val2")))
        for message in request_iterator:
            yield message


def serve():
    GrpcInstrumentorServerWrapper().instrument()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bidirectional_pb2_grpc.add_BidirectionalServicer_to_server(BidirectionalService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
