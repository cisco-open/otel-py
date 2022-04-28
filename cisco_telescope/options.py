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

import os
from distutils.util import strtobool
from . import consts
from cisco_opentelemetry_specifications import Consts


class ExporterOptions:
    def __init__(self, exporter_type: str = None, collector_endpoint: str = None):
        self.exporter_type = exporter_type or os.environ.get(
            Consts.OTEL_EXPORTER_TYPE_ENV, Consts.DEFAULT_EXPORTER_TYPE
        )
        if self.exporter_type not in consts.ALLOWED_EXPORTER_TYPES:
            raise ValueError("Unsupported exported type")
        self.collector_endpoint = collector_endpoint or os.environ.get(
            Consts.OTEL_COLLECTOR_ENDPOINT, Consts.DEFAULT_COLLECTOR_ENDPOINT
        )

    def __eq__(self, other):
        return (
            type(other) == ExporterOptions
            and self.exporter_type == other.exporter_type
            and self.collector_endpoint == other.collector_endpoint
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\t"
            f"exporter_type: {self.exporter_type},\n\t"
            f"endpoint: {self.collector_endpoint})"
        )


class Options:
    def __init__(
        self,
        service_name: str = None,
        cisco_token: str = None,
        debug: bool = False,
        payloads_enabled: bool = True,
        max_payload_size: int = None,
        exporters: [ExporterOptions] = None,
    ):

        if not exporters or len(exporters) == 0:
            self.exporters = [ExporterOptions()]
        else:
            self.exporters = exporters

        self.service_name = service_name
        self.payloads_enabled = payloads_enabled

        self.debug = debug or strtobool(
            os.environ.get(Consts.CISCO_DEBUG_ENV, str(Consts.DEFAULT_CISCO_DEBUG))
        )

        self.cisco_token = cisco_token or os.environ.get(Consts.CISCO_TOKEN_ENV)
        self.max_payload_size = max_payload_size or Consts.DEFAULT_MAX_PAYLOAD_SIZE

        if self.cisco_token is None:
            raise ValueError("Can not initiate cisco-otel launcher without token")

    def __str__(self):
        return (
            f"\n{self.__class__.__name__}(\n\t"
            f"token: {self.cisco_token},\n\t"
            f"service_name:{self.service_name},\n\t"
            f"max_payload_size: {self.max_payload_size},\n\t"
            f"exporters: \n\t{', '.join(map(str, self.exporters))})"
        )