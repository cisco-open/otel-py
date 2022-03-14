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

from . import options
from . import consts

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)


def exporter_selector(exporter: options.ExporterOptions, opt: options.Options):
    if exporter.exporter_type == consts.GRPC_EXPORTER_TYPE:
        return OTLPGrpcExporter(
            endpoint=exporter.collector_endpoint,
            headers=((consts.TOKEN_HEADER, opt.cisco_token),),
        )

    elif exporter.exporter_type == consts.HTTP_EXPORTER_TYPE:
        return OTLPHTTPExporter(
            endpoint=exporter.collector_endpoint,
            headers={consts.TOKEN_HEADER: opt.cisco_token},
        )
    else:
        return ConsoleSpanExporter(service_name=opt.service_name)


def init_exporter(opt: options.Options):
    for exporter in opt.exporters:
        return [exporter_selector(exporter, opt)]