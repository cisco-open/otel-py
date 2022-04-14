import grpc
from concurrent import futures

from tests.instrumentations.grpc.unary_unary import hello_pb2_grpc, hello_pb2


class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print("Received request")
        for key, value in context.invocation_metadata():
            print("Received initial metadata: key=%s value=%s" % (key, value))
        print("Setting custom headers")
        context.set_trailing_metadata((("key1", "val1"), ("key2", "val2")))
        print("Returning response")
        return hello_pb2.HelloReply(message="Hello, %s!" % request.name)


def create_server():
    print("Creating server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    print("Adding GreeterServicer endpoint to server")
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    print("Adding insecure port")
    server.add_insecure_port("[::]:50051")
    print("Starting server")
    server.start()
    print("Waiting for termination")
    return server
