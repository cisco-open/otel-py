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
from typing import Optional

import consts


class ExporterOptions:

    def __init__(self, collector_endpoint, exporter_type):
        self.collector_endpoint = collector_endpoint
        self.type = exporter_type


class Options:
    exporters: ExporterOptions

    def __init__(
            self,
            service_name: str = None,
            cisco_token: str = None,
            collector_endpoint: str = None,
            exporter_type: str = None):

        if service_name is None:
            self.service_name = os.environ.get(consts.KEY_SERVICE_NAME) or consts.DEFAULT_SERVICE_NAME

        if cisco_token is None:
            token = os.environ.get(consts.KEY_TOKEN)
            if token is None:
                print("Could not initiate tracing without fso token")
                return
            self.cisco_token = token

        if collector_endpoint is None:
            self.exporters.collector_endpoint = os.environ.get(
                consts.DEFAULT_COLLECTOR_ENDPOINT) or consts.DEFAULT_COLLECTOR_ENDPOINT

        if exporter_type is None:
            self.exporters.exporter_type = os.environ.get(consts.KEY_EXPORTER_TYPE) or consts.DEFAULT_EXPORTER_TYPE
