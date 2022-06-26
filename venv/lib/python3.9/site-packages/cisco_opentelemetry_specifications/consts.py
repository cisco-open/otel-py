# Copyright The Cisco Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# DO NOT EDIT, this is an Auto-generated file from tools


class Consts:
    CISCO_TOKEN_ENV = "CISCO_TOKEN"
    """
    Token environment variable
    """
    
    SERVICE_NAME_KEY = "OTEL_SERVICE_NAME"
    """
    Service-name environement variable
    """
    
    CISCO_DEBUG_ENV = "CISCO_DEBUG"
    """
    Debug environment variable
    """
    
    CISCO_PAYLOADS_ENABLED_ENV = "CISCO_PAYLOADS_ENABLED"
    """
    Payloads-enabled environment variable
    """
    
    CISCO_MAX_PAYLOAD_SIZE_ENV = "CISCO_MAX_PAYLOAD_SIZE"
    """
    Max payload size environment variable
    """
    
    CISCO_DISABLE_INSTRUMENTATIONS_ENV = "CISCO_DISABLE_INSTRUMENTATIONS"
    """
    Disable instrumentations environment variable
    """
    
    OTEL_COLLECTOR_ENDPOINT = "OTEL_COLLECTOR_ENDPOINT"
    """
    The Collector endpoint env var name
    """
    
    OTEL_EXPORTER_TYPE_ENV = "OTEL_EXPORTER_TYPE"
    """
    The Otel exporter type var name. NOTE: that is OTEL env and he responsible to parse and use
    """
    
    DEFAULT_SERVICE_NAME = "application"
    """
    Default service-name value
    """
    
    DEFAULT_CISCO_DEBUG = False
    """
    Default debug logs value
    """
    
    DEFAULT_PAYLOADS_ENABLED = True
    """
    Whether should collect payloads by default
    """
    
    DEFAULT_MAX_PAYLOAD_SIZE = 1024
    """
    The default max payload size to capture
    """
    
    DEFAULT_DISABLE_INSTRUMENTATIONS = False
    """
    Default disable instrumentations value
    """
    
    DEFAULT_COLLECTOR_ENDPOINT = "https://production.cisco-udp.com/trace-collector"
    """
    The default URL to Telescope OTel collector
    """
    
    DEFAULT_EXPORTER_TYPE = "otlp-http"
    """
    The default Exporter type
    """
    
    CISCO_SDK_VERSION_NOT_SUPPORTED = "version not supported"
    """
    Cisco sdk version not supported
    """
    
    TOKEN_HEADER_KEY = "authorization"
    """
    Authorization header key
    """
    
    CISCO_SDK_VERSION = "cisco.sdk.version"
    """
    The Cisco sdk version
    """
    