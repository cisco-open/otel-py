import grpc
import json
import logging
from typing import Any
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
from ..utils import Utils

from cisco_opentelemetry_specifications import SemanticAttributes


class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
    """wrapper around OTel grpc:server instrumentor class"""

    def __init__(self):
        super().__init__()
        self._original_wrapper_func = None

    def instrument(self, **kwargs) -> None:
        """instrument grpc:server"""
        super().instrument()

    def uninstrument(self, **kwargs) -> None:
        """disable grpc:server instrumentation."""
        super().uninstrument()

    # Internal enable wrapper instrumentation
    def _instrument(self, **kwargs) -> None:
        """Enable wrapper instrumentation internal call"""
        super()._instrument(**kwargs)
        self._original_wrapper_func = grpc.server

        def server_wrapper(*args, **kwargs) -> None:
            kwargs["interceptors"] = [server_interceptor_wrapper(self)]
            return self._original_wrapper_func(*args, **kwargs)

        grpc.server = server_wrapper

    # Internal disable wrapper instrumentation
    def _uninstrument(self, **kwargs) -> None:
        """Disable wrapper instrumentation internal call"""
        super()._uninstrument(**kwargs)


# The main entry point for a wrapper around the OTel grpc:client instrumentation module
class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        """Internal initialize instrumentation"""
        super()._instrument(**kwargs)

    def _uninstrument(self, **kwargs) -> None:
        """Internal disable instrumentation"""
        super()._uninstrument(**kwargs)

    def wrapper_fn_wrapper(self, original_func, instance, args, kwargs) -> None:
        """Wrap function for initializing the request handler"""
        channel = original_func(*args, **kwargs)
        tracer_provider = kwargs.get("tracer_provider")
        return intercept_channel(
            channel,
            client_interceptor_wrapper(tracer_provider=tracer_provider),
        )


def server_interceptor_wrapper(gisw, tracer_provider=None):
    """Helper function to set interceptor."""
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryServerInterceptorWrapper(tracer, gisw)


def client_interceptor_wrapper(tracer_provider):
    """Helper function to set interceptor."""
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryClientInterceptorWrapper(tracer)


class _OpenTelemetryWrapperServicerContext(_server._OpenTelemetryServicerContext):
    """
    Wrapper around Server-side telemetry context
    grpc:server telemetry context
    """

    def __init__(self, servicer_context, active_span):
        super().__init__(servicer_context, active_span)
        self._response_headers = ()

    def set_trailing_metadata(self, *args, **kwargs) -> None:
        """Override trailing metadata(response headers) method.
        Allows us to capture the response headers"""
        self._response_headers = args
        return self._servicer_context.set_trailing_metadata(*args, **kwargs)

    def get_trailing_metadata(self) -> tuple:
        """Return response headers"""
        return self._response_headers


class OpenTelemetryServerInterceptorWrapper(_server.OpenTelemetryServerInterceptor):
    """Wrapper around server-side interceptor"""

    def __init__(self, tracer, gisw):
        super().__init__(tracer)
        self._gisw = gisw

    def intercept_service(self, continuation, handler_call_details):
        logging.debug("Intercepting")

        def telemetry_wrapper(behavior, request_streaming, response_streaming):
            def telemetry_interceptor(request_or_iterator, context) -> Any:
                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(
                        behavior,
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )

                span = context._active_span

                Utils.set_payload(
                    span,
                    SemanticAttributes.RPC_REQUEST_BODY.key,
                    json.dumps(MessageToDict(request_or_iterator)),
                    self._gisw._max_payload_size,
                )

                Utils.add_flattened_dict(
                    span,
                    SemanticAttributes.RPC_REQUEST_METADATA.key,
                    dict(handler_call_details.invocation_metadata),
                )

                try:
                    context = _OpenTelemetryWrapperServicerContext(context, span)
                    # Capture response
                    response = behavior(request_or_iterator, context)

                except Exception as error:
                    # Bare exceptions are likely to be gRPC aborts, which
                    # we handle in our context wrapper.
                    # Here, we're interested in uncaught exceptions.
                    # pylint:disable=unidiomatic-typecheck
                    logging.exception("Exception in user context call")
                    if type(error) != Exception:
                        span.record_exception(error)
                        raise error

                else:
                    trailing_metadata = context.get_trailing_metadata()
                    if len(trailing_metadata) > 0:
                        trailing_metadata = dict(trailing_metadata[0])
                    else:
                        trailing_metadata = {}

                    response_dict = MessageToDict(response)

                    Utils.set_payload(
                        span,
                        SemanticAttributes.RPC_RESPONSE_BODY.key,
                        json.dumps(response_dict),
                        self._gisw._max_payload_size,
                    )

                    Utils.add_flattened_dict(
                        span,
                        SemanticAttributes.RPC_RESPONSE_METADATA.key,
                        trailing_metadata,
                    )

                    return response

            return telemetry_interceptor

        return _server._wrap_rpc_behavior(
            continuation(handler_call_details), telemetry_wrapper
        )  # pylint: disable=W0212

    def _intercept_server_stream(
        self, behavior, handler_call_details, request_or_iterator, context
    ) -> None:
        """Setup interceptor helper for streaming requests."""
        # TODO: -- need to implement this


class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):
    """Wrapper around client-side interceptor"""

    def __init__(self, tracer):
        super().__init__(tracer)

    def intercept_unary(self, request, metadata, client_info, invoker) -> None:
        try:
            # TODO: find how to obtain span object here
            # TODO" find how to obtain trailing metadata here
            _ = invoker(request, metadata)
        except grpc.RpcError as err:
            logging.exception(f"An error occurred in processing client request")
            raise err

    def intercept_stream(
        self, request_or_iterator, metadata, client_info, invoker
    ) -> None:
        # TODO: need to implement this
        pass
