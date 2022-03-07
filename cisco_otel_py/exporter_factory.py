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

from options import Options
import consts

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)


def init_exporter(options: Options):
    if options.exporter_type is consts.HTTP_EXPORTER_TYPE:
        return OTLPHTTPExporter(
            endpoint=options.collector_endpoint,
            headers={consts.TOKEN_HEADER: options.cisco_token},
        )
    else:
        return OTLPGrpcExporter(
            endpoint=options.collector_endpoint,
            headers={consts.TOKEN_HEADER: options.cisco_token},
        )
