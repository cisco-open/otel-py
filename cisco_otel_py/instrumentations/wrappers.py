from cisco_otel_py.instrumentations.requests import RequestsInstrumentorWrapper
from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorServerWrapper
from cisco_otel_py.instrumentations.grpc import GrpcInstrumentorClientWrapper
from cisco_otel_py import consts


class Wrapper:
    @classmethod
    def get_wrappers(cls):
        return {
            consts.REQUESTS_KEY: RequestsInstrumentorWrapper,
            consts.GRPC_SERVER_KEY: GrpcInstrumentorServerWrapper,
            consts.GRPC_CLIENT_KEY: GrpcInstrumentorClientWrapper,
        }
