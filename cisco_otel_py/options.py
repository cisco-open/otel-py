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
from pkg_resources import get_distribution

from . import consts


class ExporterOptions:
    def __init__(self, exporter_type: str = None, collector_endpoint: str = None):
        self.exporter_type = exporter_type or os.environ.get(
            consts.KEY_EXPORTER_TYPE, consts.DEFAULT_EXPORTER_TYPE
        )
        if self.exporter_type not in consts.ALLOWED_EXPORTER_TYPES:
            raise ValueError("Unsupported exported type")
        self.collector_endpoint = collector_endpoint or os.environ.get(
            consts.KEY_COLLECTOR_ENDPOINT, consts.DEFAULT_COLLECTOR_ENDPOINT
        )

    def __eq__(self, other):
        return (
            type(other) == ExporterOptions
            and self.exporter_type == other.exporter_type
            and self.collector_endpoint == other.collector_endpoint
        )


class Options:
    def __init__(
        self,
        service_name: str = None,
        cisco_token: str = None,
        max_payload_size: int = None,
        exporters: [ExporterOptions] = None,
    ):

        if not exporters or len(exporters) == 0:
            self.exporters = [ExporterOptions()]
        else:
            self.exporters = exporters

        self.service_name = service_name or os.environ.get(
            consts.KEY_SERVICE_NAME, consts.DEFAULT_SERVICE_NAME
        )
        self.cisco_token = cisco_token or os.environ.get(consts.KEY_TOKEN)
        self.cisco_otel_version = get_distribution(__package__).version
        self.max_payload_size = max_payload_size or consts.MAX_PAYLOAD_SIZE

        if self.cisco_token is None:
            raise ValueError("Can not initiate cisco-otel launcher without token")
