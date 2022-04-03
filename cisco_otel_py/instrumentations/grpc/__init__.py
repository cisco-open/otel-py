import json
import logging
import traceback
import grpc
from google.protobuf.json_format import MessageToDict
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorServer,
    GrpcInstrumentorClient,
    _server,
    _client,
)
from opentelemetry.instrumentation.grpc.version import __version__
from opentelemetry.instrumentation.grpc.grpcext import intercept_channel
from cisco_otel_py.instrumentations import BaseInstrumentorWrapper
from cisco_otel_py.instrumentations.registry import Registry, TYPE_RPC

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)


class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
    """wrapper around OTel grpc:server instrumentor class"""

    def __init__(self):
        print('Entering GrpcInstrumentorServerWrapper constructor.')
        super().__init__()
        self._original_wrapper_func = None

    def instrument(self, **kwargs) -> None:
        """instrument grpc:server"""
        print('Entering GrpcInstrumentorServerWrapper.instrument().')
        super().instrument()

    def uninstrument(self, **kwargs) -> None:
        """disable grpc:server instrumentation."""
        print('Entering GrpcInstrumentorServerWrapper.uninstrument()')
        super().uninstrument()

    # Internal enable wrapper instrumentation
    def _instrument(self, **kwargs) -> None:
        """Enable wrapper instrumentation internal call"""
        print('Entering GrpcInstrumentorServerWrapper._instument().')
        super()._instrument(**kwargs)
        self._original_wrapper_func = grpc.server

        def server_wrapper(*args, **kwargs) -> None:
            print('Entering wrapper interceptors set')
            print('Setting server_interceptor_wrapper() as interceptor.')
            kwargs["interceptors"] = [server_interceptor_wrapper(self)]
            return self._original_wrapper_func(*args, **kwargs)

        grpc.server = server_wrapper

    # Internal disable wrapper instrumentation
    def _uninstrument(self, **kwargs) -> None:
        """Disable wrapper instrumentation internal call"""
        print('Entering GrpcInstrumentorServerWrapper._uninstrument()')
        super()._uninstrument(**kwargs)


# The main entry point for a wrapper around the OTel grpc:client instrumentation module
class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
    def __init__(self):
        print('Entering GrpcInstrumentorClientWrapper constructor.')
        super().__init__()

    # Internal initialize instrumentation
    def _instrument(self, **kwargs) -> None:
        print('Entering GrpcInstrumentorClientWrapper._instrument().')
        super()._instrument(**kwargs)

    # Internal disable instrumentation
    def _uninstrument(self, **kwargs) -> None:
        """Internal disable instrumentation"""
        print('Entering GrpcInstrumentorClientWrapper._uninstrument().')
        super()._uninstrument(**kwargs)

    # Wrap function for initializing the request handler
    def wrapper_fn_wrapper(self, original_func, instance, args, kwargs) -> None:  # pylint: disable=W0613,R0201
        """Wrap function for initializing the request handler"""
        channel = original_func(*args, **kwargs)
        tracer_provider = kwargs.get("tracer_provider")
        return intercept_channel(
            channel, client_interceptor_wrapper(
                tracer_provider=tracer_provider),
        )


# Initialize the server handler
def server_interceptor_wrapper(gisw, tracer_provider=None) -> None:
    """Helper function to set interceptor."""
    print('Entering server_interceptor_wrapper().')
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryServerInterceptorWrapper(tracer, gisw)


# Initialize the client handler
def client_interceptor_wrapper(tracer_provider) -> None:
    """Helper function to set interceptor."""
    print('Entering client_interceptor_wrapper().')
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryClientInterceptorWrapper(tracer)


# Wrapper around Server-side telemetry context
class _OpenTelemetryWrapperServicerContext(_server._OpenTelemetryServicerContext):  # pylint: disable=W0212,W0223
    """grpc:server telemetry context"""
    def __init__(self, servicer_context, active_span):
        print('Entering _OpenTelemetryWrapperServicerContext.__init__().')
        super().__init__(servicer_context, active_span)
        self._response_headers = ()

    def set_trailing_metadata(self, *args, **kwargs) -> None:
        """Override trailing metadata(response headers) method.
        Allows us to capture the response headers"""
        print('Entering _OpenTelemetryWrapperServicerContext.set_trailing_metadata().')
        self._response_headers = args
        return self._servicer_context.set_trailing_metadata(*args, **kwargs)

    def get_trailing_metadata(self) -> tuple:
        """Return response headers"""
        return self._response_headers


# Wrapper around server-side interceptor
class OpenTelemetryServerInterceptorWrapper(_server.OpenTelemetryServerInterceptor):  # pylint: disable=R0903

    def __init__(self, tracer, gisw):
        super().__init__(tracer)
        self._gisw = gisw

    def intercept_service(self, continuation, handler_call_details):
        print('Entering OpenTelemetryServerInterceptorWrapper.intercept_service().')

        def telemetry_wrapper(behavior, request_streaming, response_streaming):  # pylint: disable=W0613
            print('Entering OpenTelemetryServerInterceptorWrapper.telemetry_wrapper().')

            def telemetry_interceptor(request_or_iterator, context) -> None:
                print('Entering OpenTelemetryServerInterceptorWrapper.telemetry_interceptor().')
                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(
                        behavior,
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )

                span = context._active_span  # pylint: disable=W0212

                invocation_metadata = dict(handler_call_details.invocation_metadata)
                req_dict = MessageToDict(request_or_iterator)
                self._gisw.generic_rpc_request_handler(
                    invocation_metadata, json.dumps(req_dict), span)
                try:
                    block_result = Registry().apply_filters(span,
                                                            '',
                                                            invocation_metadata,
                                                            request_or_iterator,
                                                            TYPE_RPC)
                    if block_result:
                        print('should block evaluated to true, aborting with 403')
                        return context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Permission Denied')

                    # Capture response
                    context = _OpenTelemetryWrapperServicerContext(
                        context, span)
                    response = behavior(request_or_iterator, context)
                    trailing_metadata = context.get_trailing_metadata()
                    if len(trailing_metadata) > 0:
                        trailing_metadata = dict(trailing_metadata[0])
                    else:
                        trailing_metadata = {}

                    response_dict = MessageToDict(response)
                    self._gisw.generic_rpc_response_handler(
                        trailing_metadata, json.dumps(response_dict), span)

                    return response
                except Exception as error:  # pylint: disable=W0703
                    # Bare exceptions are likely to be gRPC aborts, which
                    # we handle in our context wrapper.
                    # Here, we're interested in uncaught exceptions.
                    # pylint:disable=unidiomatic-typecheck
                    if type(error) != Exception:
                        span.record_exception(error)
                        raise error
                    return None

            return telemetry_interceptor

        return _server._wrap_rpc_behavior(continuation(handler_call_details),
                                          telemetry_wrapper)  # pylint: disable=W0212

    def _intercept_server_stream(
            self,
            behavior,
            handler_call_details,
            request_or_iterator,
            context) -> None:
        """Setup interceptor helper for streaming requests."""
        print('Entering OpenTelemetryServerInterceptorWrapper.intercept_server_stream().')
        # TODO: -- need to implement this


# Wrapper around client-side interceptor
class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):

    def __init__(self, tracer):
        print('Entering OpenTelemetryClientInterceptorWrapper.__init__().')
        super().__init__(tracer)

    def intercept_unary(self, request, metadata, client_info, invoker) -> None:
        print('Entering OpenTelemetryClientInterceptorWrapper.intercept_unary().')
        try:
            # TODO: find how to obtain span object here
            # TODO" find how to obtain trailing metadata here
            result = invoker(request, metadata)  # pylint:disable=W0612
        except grpc.RpcError as err:
            logger.error('An error occurred in %s: exception=%s, stacktrace=%s',
                         'processing client request',
                         err,
                         traceback.format_exc())
            raise err

    #        return self._trace_result(result)

    def intercept_stream(
            self,
            request_or_iterator,
            metadata,
            client_info,
            invoker
    ) -> None:
        print('Entering OpenTelemetryClientInterceptorWrapper.intercept_stream().')
        # TODO: need to implement this
