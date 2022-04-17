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

KEY_SERVICE_NAME = "OTEL_SERVICE_NAME"
KEY_DEBUG_NAME = "CISCO_DEBUG"
KEY_COLLECTOR_ENDPOINT = "OTEL_COLLECTOR_ENDPOINT"
KEY_EXPORTER_TYPE = "OTEL_EXPORTER_TYPE"
KEY_TOKEN = "CISCO_TOKEN"

HTTP_EXPORTER_TYPE = "otlp-http"
GRPC_EXPORTER_TYPE = "otlp-grpc"
CONSOLE_EXPORTER_TYPE = "console"
TOKEN_HEADER = "x-epsagon-token"

DEFAULT_SERVICE_NAME = "application"
DEFAULT_DEBUG = "False"
DEFAULT_SDK_VERSION = "version not supported"
DEFAULT_COLLECTOR_ENDPOINT = "http://localhost:4317"
DEFAULT_EXPORTER_TYPE = GRPC_EXPORTER_TYPE

MAX_PAYLOAD_SIZE = 128 * 1024

ALLOWED_EXPORTER_TYPES = [HTTP_EXPORTER_TYPE, GRPC_EXPORTER_TYPE, CONSOLE_EXPORTER_TYPE]

ALLOWED_CONTENT_TYPES = [
    "application/json",
    "application/graphql",
    "application/x-www-form-urlencoded",
]

ENCODING_UTF8 = "UTF8"
DECODE_PAYLOAD_IN_CASE_OF_ERROR = "backslashreplace"

REQUESTS_KEY = "requests"
GRPC_SERVER_KEY = "grpc_server"
GRPC_CLIENT_KEY = "grpc_client"
