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

# Inner naming conventions
HTTP_EXPORTER_TYPE = "otlp-http"
GRPC_EXPORTER_TYPE = "otlp-grpc"
CONSOLE_EXPORTER_TYPE = "console"

ENCODING_UTF8 = "UTF8"
DECODE_PAYLOAD_IN_CASE_OF_ERROR = "backslashreplace"

REQUESTS_KEY = "requests"
AIOHTTP_KEY = "aiohttp"
PYMONGO_KEY = "pymongo"
AIOHTTP_CLIENT_KEY = "aiohttp-client"
GRPC_SERVER_KEY = "grpc_server"
GRPC_CLIENT_KEY = "grpc_client"

# Configurations
MAX_WAIT_TIME = 0.1  # seconds
ALLOWED_EXPORTER_TYPES = [HTTP_EXPORTER_TYPE, GRPC_EXPORTER_TYPE, CONSOLE_EXPORTER_TYPE]
ALLOWED_CONTENT_TYPES = [
    "application/json",
    "application/graphql",
    "application/x-www-form-urlencoded",
]
MONGODB_ARGUMENTS_KEYS = ["insert", "update"]
MONGODB_RESPONSE_KEYS = ["insert", "update", "find", "createIndexes"]
