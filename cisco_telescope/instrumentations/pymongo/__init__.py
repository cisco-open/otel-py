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
import json

from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from pymongo import monitoring
from bson import objectid
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.trace import Span
from ... import consts


def request_hook(span: Span, params: monitoring.CommandStartedEvent) -> None:
    if not span or not span.is_recording():
        return

    if params.command_name == "insert":
        arguments = json.dumps(
            params.command.__getitem__("documents"), cls=ObjectIDEncoder, skipkeys=True
        )
        span.set_attribute(
            SemanticAttributes.DB_MONGODB_ARGUMENTS,
            arguments,
        )

    if params.command_name == "update":
        arguments = json.dumps(
            params.command.__getitem__("updates"), cls=ObjectIDEncoder, skipkeys=True
        )
        span.set_attribute(
            SemanticAttributes.DB_MONGODB_ARGUMENTS,
            arguments,
        )


def response_hook(span: Span, params: monitoring.CommandSucceededEvent) -> None:
    if not span or not span.is_recording():
        return

    if params.reply and params.command_name in consts.MONGODB_RESPONSE_KEYS:

        span.set_attribute(
            SemanticAttributes.DB_MONGODB_RESPONSE,
            json.dumps(params.reply, cls=ObjectIDEncoder, skipkeys=True),
        )


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


class ObjectIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, objectid.ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
