import json
import grpc
import logging
from typing import MutableMapping
from collections import OrderedDict

from wrapt import wrap_function_wrapper as _wrap
from typing import Any
from google.protobuf.json_format import MessageToDict
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorServer,
    GrpcInstrumentorClient,
    _server,
    _client,
)
from opentelemetry.propagate import inject
from opentelemetry.propagators.textmap import Setter
from opentelemetry.instrumentation.grpc.version import __version__
from opentelemetry.instrumentation.grpc.grpcext import intercept_channel
from ..utils import Utils
from opentelemetry.instrumentation.grpc._utilities import RpcInfo
from opentelemetry.trace.status import Status, StatusCode
from cisco_telescope.instrumentations import utils

from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.semconv.trace import SpanAttributes


# code was taken from github commit sha: f7eb9673bca5d6fb4d16040e8ac28053225ad302
# https://github.com/hypertrace/pythonagent/pull/262


class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer):
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
class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        """Internal initialize instrumentation"""
        logging.debug("Instrumenting")
        for ctype in self._which_channel(kwargs):
            _wrap(
                "grpc",
                ctype,
                self.wrapper_fn_wrapper,
            )

    def _uninstrument(self, **kwargs) -> None:
        """Internal disable instrumentation"""
        super()._uninstrument(**kwargs)

    def wrapper_fn_wrapper(self, original_func, instance, args, kwargs) -> None:
        """Wrap function for initializing the request handler"""
        channel = original_func(*args, **kwargs)
        tracer_provider = kwargs.get("tracer_provider")
        return intercept_channel(
            channel,
            client_interceptor_wrapper(self, tracer_provider=tracer_provider),
        )


def server_interceptor_wrapper(gisw, tracer_provider=None):
    """Helper function to set interceptor."""
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryServerInterceptorWrapper(tracer, gisw)


def client_interceptor_wrapper(gicw, tracer_provider):
    """Helper function to set interceptor."""
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryClientInterceptorWrapper(tracer, gicw)


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
                    SemanticAttributes.RPC_REQUEST_BODY,
                    json.dumps(MessageToDict(request_or_iterator)),
                )

                Utils.add_flattened_dict(
                    span,
                    SemanticAttributes.RPC_REQUEST_METADATA,
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
                        SemanticAttributes.RPC_RESPONSE_BODY,
                        json.dumps(response_dict),
                    )

                    Utils.add_flattened_dict(
                        span,
                        SemanticAttributes.RPC_RESPONSE_METADATA,
                        trailing_metadata,
                    )

                    return response

            return telemetry_interceptor

        return _server._wrap_rpc_behavior(
            continuation(handler_call_details), telemetry_wrapper
        )  # pylint: disable=W0212

    # def _intercept_server_stream(
    #         self, behavior, handler_call_details, request_or_iterator, context
    # ):
    #     print("Entering OpenTelemetryServerInterceptorWrapper.intercept_server_stream().")
    #     with self._set_remote_context(context):
    #         with self._start_span(
    #                 handler_call_details, context, set_status_on_exception=False
    #         ) as span:
    #             context = _OpenTelemetryWrapperServicerContext(context, span)
    #
    #             try:
    #                 yield from behavior(request_or_iterator, context)
    #
    #             except Exception as error:
    #                 # pylint:disable=unidiomatic-typecheck
    #                 if type(error) != Exception:
    #                     span.record_exception(error)
    #                 raise error


class _CarrierSetter(Setter):
    """
    We use a custom setter in order to be able to lower case
    keys as is required by grpc.
    """

    def set(self, carrier: MutableMapping[str, str], key: str, value: str):
        carrier[key.lower()] = value


class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):
    """Wrapper around client-side interceptor"""

    def __init__(self, tracer, gicw):
        super().__init__(tracer)
        self._gicw = gicw

    def _intercept(self, request, metadata, client_info, invoker):
        # if context.get_value(_SUPPRESS_INSTRUMENTATION_KEY):
        #     return invoker(request, metadata)
        if not metadata:
            mutable_metadata = OrderedDict()
        else:
            mutable_metadata = OrderedDict(metadata)
        with self._start_span(
            client_info.full_method,
            end_on_exit=False,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            result = None
            try:
                inject(mutable_metadata, setter=_CarrierSetter())
                metadata = tuple(mutable_metadata.items())

                rpc_info = RpcInfo(
                    full_method=client_info.full_method,
                    metadata=metadata,
                    timeout=client_info.timeout,
                    request=request,
                )

                result = invoker(request, metadata)

                # Add request headers
                Utils.add_flattened_dict(
                    span,
                    SemanticAttributes.RPC_REQUEST_METADATA,
                    utils.Utils.lowercase_items(dict(metadata)),
                )

                # Add request body
                Utils.set_payload(
                    span,
                    SemanticAttributes.RPC_REQUEST_BODY,
                    str(request),  # body
                )

            except Exception as exc:
                if isinstance(exc, grpc.RpcError):
                    span.set_attribute(
                        SpanAttributes.RPC_GRPC_STATUS_CODE,
                        exc.code().value[0],
                    )
                span.set_status(
                    Status(
                        status_code=StatusCode.ERROR,
                        description=f"{type(exc).__name__}: {exc}",
                    )
                )
                span.record_exception(exc)
                raise exc
            finally:
                if not result:
                    span.end()

        return self._trace_result(span, rpc_info, result)

    # def _intercept_server_stream(
    #         self, request_or_iterator, metadata, client_info, invoker
    # ):
    #     print("Entering OpenTelemetryClientInterceptorWrapper.intercept_server_stream().")
    #     if not metadata:
    #         mutable_metadata = OrderedDict()
    #     else:
    #         mutable_metadata = OrderedDict(metadata)
    #
    #     with self._start_span(client_info.full_method) as span:
    #         inject(mutable_metadata, setter=_CarrierSetter())
    #         metadata = tuple(mutable_metadata.items())
    #         rpc_info = RpcInfo(
    #             full_method=client_info.full_method,
    #             metadata=metadata,
    #             timeout=client_info.timeout,
    #         )
    #
    #         if client_info.is_client_stream:
    #             rpc_info.request = request_or_iterator
    #
    #         try:
    #             yield from invoker(request_or_iterator, metadata)
    #         except grpc.RpcError as err:
    #             span.set_status(Status(StatusCode.ERROR))
    #             span.set_attribute(
    #                 SpanAttributes.RPC_GRPC_STATUS_CODE, err.code().value[0]
    #             )
    #             raise err

    # def intercept_stream(
    #     self, request_or_iterator, metadata, client_info, invoker
    # ):
    #     print("Entering OpenTelemetryClientInterceptorWrapper.intercept_stream().")
    #     if client_info.is_server_stream:
    #         return self._intercept_server_stream(
    #             request_or_iterator, metadata, client_info, invoker
    #         )
    #
    #     return self._intercept(
    #         request_or_iterator, metadata, client_info, invoker
    #     )
