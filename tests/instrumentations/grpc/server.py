import grpc
from concurrent import futures

from . import hello_pb2
from . import hello_pb2_grpc


class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        metadata = (("key1", "val1"), ("key2", "val2"))
        context.set_trailing_metadata(metadata)
        return hello_pb2.HelloReply(message=f"Hello, {request.name}!")


def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    return server
