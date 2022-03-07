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

DEFAULT_SERVICE_NAME = "application"
DEFAULT_COLLECTOR_ENDPOINT = "http://localhost:4317"
DEFAULT_EXPORTER_TYPE = "otlp-grpc"

KEY_SERVICE_NAME = "OTEL_SERVICE_NAME"
KEY_COLLECTOR_ENDPOINT = "OTEL_COLLECTOR_ENDPOINT"
KEY_EXPORTER_TYPE = "OTEL_EXPORTER_TYPE"
KEY_TOKEN = "CISCO_TOKEN"

HTTP_EXPORTER_TYPE = "otlp-http"
GRPC_EXPORTER_TYPE = "otlp-grpc"
TOKEN_HEADER = "X-Epsagon-Token"
