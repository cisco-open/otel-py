# import asyncio
#
# from grpclib.client import Channel
#
# # generated by protoc
# from hello_pb2 import HelloRequest, HelloReply
# from hello_grpc import GreeterStub
# import sys
#
#
# async def main():
#     async with Channel('127.0.0.1', 50051) as channel:
#         greeter = GreeterStub(channel)
#
#         for line in sys.stdin:
#             reply = await greeter.SayHello(HelloRequest(name=line.strip()))
#             print(reply.message)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
