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
import typing

import aiohttp
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.trace import Span

from cisco_otel_py.instrumentations import BaseInstrumentorWrapper
from ..utils import Utils

from cisco_opentelemetry_specifications import SemanticAttributes


def request_hook(span: Span, params: aiohttp.TraceRequestStartParams):
    if not span or not span.is_recording():
        return

    Utils.add_flattened_dict(
        span,
        SemanticAttributes.HTTP_REQUEST_HEADER,
        getattr(params, "headers", dict()),
    )


def response_hook(
    span: Span,
    params: typing.Union[
        aiohttp.TraceRequestEndParams,
        aiohttp.TraceRequestExceptionParams,
    ],
):
    if not span or not span.is_recording():
        return

    Utils.add_flattened_dict(
        span,
        SemanticAttributes.HTTP_RESPONSE_HEADER.key,
        getattr(params, "headers", dict()),
    )


class RequestsInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            request_hook=request_hook,
            response_hook=response_hook,
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()
