"""
Copyright The Cisco Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import types
import typing

import aiohttp
import wrapt

from opentelemetry.context import create_key
from opentelemetry import context as context_api
from opentelemetry.instrumentation.aiohttp_client import (
    AioHttpClientInstrumentor,
    _ResponseHookT,
    _RequestHookT,
)
from opentelemetry.instrumentation.aiohttp_client.version import __version__
from opentelemetry.instrumentation.utils import http_status_to_status_code
from opentelemetry.propagate import inject
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import (
    Span,
    TracerProvider,
    get_tracer,
    Status,
    SpanKind,
    StatusCode,
)
from opentelemetry import trace

from cisco_otel_py.instrumentations import BaseInstrumentorWrapper
from ..utils import Utils

from cisco_opentelemetry_specifications import SemanticAttributes


def request_hook(span: Span, params: aiohttp.TraceRequestChunkSentParams) -> None:
    if not span or not span.is_recording():
        return

    Utils.add_flattened_dict(
        span,
        SemanticAttributes.HTTP_REQUEST_HEADER.key,
        getattr(params, "headers", dict()),
    )


def response_hook(
    span: Span,
    params: aiohttp.TraceResponseChunkReceivedParams,
) -> None:
    if not span or not span.is_recording():
        return

    if hasattr(params, "response") and params.response is not None:
        Utils.add_flattened_dict(
            span,
            SemanticAttributes.HTTP_RESPONSE_HEADER.key,
            getattr(params.response, "headers", dict()),
        )


class AiohttpInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        _tracer_provider = kwargs.get("tracer_provider")
        # super()._instrument(
        #     tracer_provider=_tracer_provider,
        #     request_hook=request_hook,
        #     response_hook=response_hook,
        # )

        _instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            request_hook=request_hook,
            response_hook=response_hook,
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()


def create_trace_config(
    tracer_provider: TracerProvider = None,
    request_hook: _RequestHookT = None,
    response_hook: _ResponseHookT = None,
) -> aiohttp.TraceConfig:
    tracer = get_tracer(__name__, __version__, tracer_provider)

    def _end_trace(trace_config_ctx: types.SimpleNamespace):
        context_api.detach(trace_config_ctx.token)
        trace_config_ctx.span.end()

    async def on_request_start(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestStartParams,
    ):
        if context_api.get_value(create_key("suppress_instrumentation")):
            trace_config_ctx.span = None
            return

        http_method = params.method.upper()
        request_span_name = f"HTTP {http_method}"

        trace_config_ctx.span = trace_config_ctx.tracer.start_span(
            request_span_name,
            kind=SpanKind.CLIENT,
        )

        if callable(request_hook):
            request_hook(trace_config_ctx.span, params)

        if trace_config_ctx.span.is_recording():
            attributes = {
                SpanAttributes.HTTP_METHOD: http_method,
            }
            for key, value in attributes.items():
                trace_config_ctx.span.set_attribute(key, value)

        trace_config_ctx.token = context_api.attach(
            trace.set_span_in_context(trace_config_ctx.span)
        )

        inject(params.headers)

    async def on_request_end(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestEndParams,
    ):
        if trace_config_ctx.span is None:
            return

        if callable(response_hook):
            response_hook(trace_config_ctx.span, params)

        if trace_config_ctx.span.is_recording():
            trace_config_ctx.span.set_status(
                Status(http_status_to_status_code(int(params.response.status)))
            )
            trace_config_ctx.span.set_attribute(
                SpanAttributes.HTTP_STATUS_CODE, params.response.status
            )
            if (
                hasattr(trace_config_ctx, "request_body")
                and trace_config_ctx.request_body is not None
            ):
                Utils.set_payload(
                    trace_config_ctx.span,
                    SemanticAttributes.HTTP_REQUEST_BODY.key,
                    trace_config_ctx.request_body,
                    1024,
                )
            if (
                hasattr(trace_config_ctx, "response_body")
                and trace_config_ctx.response_body is not None
            ):
                Utils.set_payload(
                    trace_config_ctx.span,
                    SemanticAttributes.HTTP_RESPONSE_BODY.key,
                    trace_config_ctx.request_body,
                    1024,
                )

        _end_trace(trace_config_ctx)

    async def on_request_exception(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestExceptionParams,
    ):
        if trace_config_ctx.span is None:
            return

        if callable(response_hook):
            response_hook(trace_config_ctx.span, params)

        if trace_config_ctx.span.is_recording() and params.exception:
            trace_config_ctx.span.set_status(Status(StatusCode.ERROR))
            trace_config_ctx.span.record_exception(params.exception)
        _end_trace(trace_config_ctx)

    async def on_request_chunk_sent(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestChunkSentParams,
    ):
        if hasattr(params, "chunk") and params.chunk is not None:
            decoded_chunk = params.chunk.decode()
            trace_config_ctx.request_body += decoded_chunk

    async def on_responde_chunk_received(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestChunkSentParams,
    ):
        if hasattr(params, "chunk") and params.chunk is not None:
            decoded_chunk = params.chunk.decode()
            trace_config_ctx.response_body += decoded_chunk

    def _trace_config_ctx_factory(**kwargs):
        kwargs.setdefault("trace_request_ctx", {})
        return types.SimpleNamespace(
            tracer=tracer, **kwargs, request_body="", response_body=""
        )

    trace_config = aiohttp.TraceConfig(
        trace_config_ctx_factory=_trace_config_ctx_factory
    )

    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_response_chunk_received.append(on_responde_chunk_received)
    trace_config.on_request_exception.append(on_request_exception)
    trace_config.on_request_end.append(on_request_end)

    return trace_config


def _instrument(
    tracer_provider: TracerProvider = None,
    request_hook: _RequestHookT = None,
    response_hook: _ResponseHookT = None,
):
    def instrumented_init(wrapped, instance, args, kwargs) -> None:
        trace_configs = list(kwargs.get("trace_configs") or ())

        trace_config = create_trace_config(
            tracer_provider=tracer_provider,
            request_hook=request_hook,
            response_hook=response_hook,
        )

        trace_configs.append(trace_config)

        kwargs["trace_configs"] = trace_configs
        return wrapped(*args, **kwargs)

    wrapt.wrap_function_wrapper(aiohttp.ClientSession, "__init__", instrumented_init)
