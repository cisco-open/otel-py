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

from . import consts


class Options:
    collector_endpoint = consts.DEFAULT_COLLECTOR_ENDPOINT
    cisco_token = "token"

    def __init__(
        self,
        service_name: str = None,
        cisco_token: str = None,
        collector_endpoint: str = None,
        exporter_type: str = None,
    ):

        if service_name is None:
            self.service_name = (
                os.environ.get(consts.KEY_SERVICE_NAME) or consts.DEFAULT_SERVICE_NAME
            )

        if cisco_token is None:
            token = os.environ.get(consts.KEY_TOKEN)
            if token is None:
                print("Could not initiate tracing without fso token")
                # return
            self.cisco_token = token

        if collector_endpoint is None:
            self.collector_endpoint = (
                os.environ.get(consts.DEFAULT_COLLECTOR_ENDPOINT)
                or consts.DEFAULT_COLLECTOR_ENDPOINT
            )

        if exporter_type is None:
            self.exporter_type = (
                os.environ.get(consts.KEY_EXPORTER_TYPE) or consts.DEFAULT_EXPORTER_TYPE
            )
