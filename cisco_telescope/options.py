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
import logging
from distutils.util import strtobool
from typing import Optional, Dict

from . import consts as project_consts
from cisco_opentelemetry_specifications import Consts


class ExporterOptions:
    def __init__(
        self,
        exporter_type: str = None,
        collector_endpoint: str = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ):
        self.exporter_type = exporter_type or os.environ.get(
            Consts.OTEL_EXPORTER_TYPE_ENV
        )
        self.collector_endpoint = collector_endpoint or os.environ.get(
            Consts.OTEL_COLLECTOR_ENDPOINT
        )
        if self.exporter_type not in project_consts.ALLOWED_EXPORTER_TYPES:
            raise ValueError("Unsupported exported type")

        if (
            self.exporter_type is not project_consts.CONSOLE_EXPORTER_TYPE
            and not self.collector_endpoint
        ):
            logging.warning(
                "Warning: Custom exporter is set without collector endpoint"
            )

        self.custom_headers = custom_headers

    def __eq__(self, other):
        return (
            type(other) == ExporterOptions
            and self.exporter_type == other.exporter_type
            and self.collector_endpoint == other.collector_endpoint
            and self.custom_headers == other.custom_headers
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\t"
            f"exporter_type: {self.exporter_type},\n\t"
            f"endpoint: {self.collector_endpoint},\n\t"
            f"custom_headers: {self.custom_headers})"
        )


class Options:
    def __init__(
        self,
        service_name: str = None,
        cisco_token: str = None,
        debug: bool = None,
        payloads_enabled: bool = None,
        max_payload_size: int = None,
        exporters: [ExporterOptions] = None,
    ):

        self.cisco_token = cisco_token or os.environ.get(Consts.CISCO_TOKEN_ENV)
        if self.cisco_token is None and exporters is None:
            raise ValueError("Can not initiate cisco-telescope without token")

        if self.cisco_token is not None and exporters is not None:
            logging.warning(
                "Warning: Custom exporters do not use cisco token, it can be passed as a custom header"
            )

        if not exporters or len(exporters) == 0:  # Set default exporter
            self.exporters = [
                ExporterOptions(
                    exporter_type=Consts.DEFAULT_EXPORTER_TYPE,
                    collector_endpoint=Consts.DEFAULT_COLLECTOR_ENDPOINT,
                    custom_headers={
                        Consts.TOKEN_HEADER_KEY: verify_token(self.cisco_token)
                    },
                )
            ]
        else:
            self.exporters = exporters

        self.service_name = service_name

        if payloads_enabled is None:
            self.payloads_enabled = strtobool(
                os.environ.get(
                    Consts.CISCO_PAYLOADS_ENABLED_ENV,
                    str(Consts.DEFAULT_PAYLOADS_ENABLED),
                )
            )
        else:
            self.payloads_enabled = payloads_enabled

        if debug is None:
            self.debug = strtobool(
                os.environ.get(Consts.CISCO_DEBUG_ENV, str(Consts.DEFAULT_CISCO_DEBUG))
            )
        else:
            self.debug = debug

        self.max_payload_size = max_payload_size or Consts.DEFAULT_MAX_PAYLOAD_SIZE

    def __str__(self):
        return (
            f"\n{self.__class__.__name__}(\n\t"
            f"token: {self.cisco_token},\n\t"
            f"service_name:{self.service_name},\n\t"
            f"max_payload_size: {self.max_payload_size},\n\t"
            f"exporters: \n\t{', '.join(map(str, self.exporters))})"
        )


def verify_token(token: str) -> str:
    auth_prefix = "Bearer "
    if token.startswith(auth_prefix):
        return token
    else:
        return auth_prefix + token
