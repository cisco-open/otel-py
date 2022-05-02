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
import asyncio
import types
from collections import deque

import aiohttp
import wrapt

from opentelemetry import context as context_api
from opentelemetry.instrumentation.aiohttp_client import (
    AioHttpClientInstrumentor,
    _ResponseHookT,
    _RequestHookT,
)
from opentelemetry.instrumentation.utils import http_status_to_status_code
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.instrumentation.aiohttp_client.version import __version__
from opentelemetry.trace import (
    Span,
    TracerProvider,
    get_tracer,
    Status,
)

from cisco_telescope.instrumentations import BaseInstrumentorWrapper
from ..utils import Utils

from cisco_opentelemetry_specifications import SemanticAttributes

from ... import consts


def request_hook(span: Span, params: aiohttp.TraceRequestStartParams) -> None:
    if not span or not span.is_recording():
        return

    Utils.add_flattened_dict(
        span,
        SemanticAttributes.HTTP_REQUEST_HEADER,
        getattr(params, "headers", dict()),
    )


def response_hook(
    span: Span,
    params: aiohttp.TraceRequestEndParams,
) -> None:
    if not span or not span.is_recording():
        return

    if hasattr(params, "response"):
        Utils.add_flattened_dict(
            span,
            SemanticAttributes.HTTP_RESPONSE_HEADER,
            getattr(params.response, "headers", dict()),
        )


class AiohttpInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            request_hook=request_hook,
            response_hook=response_hook,
            trace_config=[create_trace_config()]
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
            # Expand opentelemetry implementations
            handle_request_body(trace_config_ctx)
            await handle_response_body(trace_config_ctx, params)

        _end_trace(trace_config_ctx)

    async def on_request_chunk_sent(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestChunkSentParams,
    ):
        if getattr(params, "chunk"):
            decoded_chunk = params.chunk.decode()
            trace_config_ctx.request_body += decoded_chunk

    async def on_response_chunk_received(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestChunkSentParams,
    ):
        if getattr(params, "chunk"):
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

    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_response_chunk_received.append(on_response_chunk_received)
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


def handle_request_body(trace_config_ctx: types.SimpleNamespace):
    if getattr(trace_config_ctx, "request_body"):
        Utils.set_payload(
            trace_config_ctx.span,
            SemanticAttributes.HTTP_REQUEST_BODY,
            trace_config_ctx.request_body,
        )


async def handle_response_body(
    trace_config_ctx: types.SimpleNamespace, params: aiohttp.TraceRequestEndParams
):
    response_body = b""
    if getattr(params.response, "content"):
        # copy response content into temporary queue
        content_stream = params.response.content
        tmp_deque = deque()
        try:
            while not content_stream.at_eof():
                response_chunk = b""  # verify var has value
                response_chunk = await asyncio.wait_for(
                    content_stream.read(), consts.MAX_WAIT_TIME
                )
                tmp_deque.append(response_chunk)
                response_body += response_chunk

        finally:
            # retrieve response data from temporary queue
            content_stream._cursor = 0

            content_stream._buffer = tmp_deque

            Utils.set_payload(
                trace_config_ctx.span,
                SemanticAttributes.HTTP_RESPONSE_BODY,
                response_body,
            )
