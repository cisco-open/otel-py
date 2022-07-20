import grpc
from concurrent import futures

from tests import hello_pb2_grpc, hello_pb2


class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        context.set_trailing_metadata((("key1", "val1"), ("key2", "val2")))
        return hello_pb2.HelloReply(message="Hello, %s!" % request.name)


def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    return server
