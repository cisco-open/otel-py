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

from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from pymongo import monitoring
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.trace import Span
from ... import consts


def request_hook(span: Span, params: monitoring.CommandStartedEvent) -> None:
    if not span or not span.is_recording() or not params.command_name:
        return

    if params.command_name == "insert":
        span.set_attribute(
            SemanticAttributes.DB_MONGODB_ARGUMENTS,
            str(params.command.get("documents")),
        )

    if params.command_name == "update":
        span.set_attribute(
            SemanticAttributes.DB_MONGODB_ARGUMENTS, str(params.command.get("updates"))
        )


def response_hook(span: Span, params: monitoring.CommandSucceededEvent) -> None:
    if not span or not span.is_recording() or not params.command_name:
        return

    if params.reply and params.command_name in consts.MONGODB_RESPONSE_KEYS:
        span.set_attribute(SemanticAttributes.DB_MONGODB_RESPONSE, str(params.reply))


class PymongoInstrumentorWrapper(PymongoInstrumentor):
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
