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


def _set_default_options():
    if os.getenv(consts.KEY_SERVICE_NAME) is None:
        os.environ[consts.KEY_SERVICE_NAME] = consts.DEFAULT_SERVICE_NAME

    if os.getenv(consts.KEY_EXPORTER_TYPE) is None:
        os.environ[consts.KEY_EXPORTER_TYPE] = consts.DEFAULT_EXPORTER_TYPE

    if os.getenv(consts.KEY_COLLECTOR_ENDPOINT) is None:
        os.environ[consts.KEY_COLLECTOR_ENDPOINT] = consts.DEFAULT_COLLECTOR_ENDPOINT


class Options:
    def __init__(
        self,
        service_name: str = None,
        cisco_token: str = None,
        collector_endpoint: str = None,
        exporter_type: str = None,
    ):
        _set_default_options()

        try:
            self.service_name = service_name or os.environ.get(consts.KEY_SERVICE_NAME)
            self.cisco_token = cisco_token or os.environ.get(consts.KEY_TOKEN)
            self.collector_endpoint = collector_endpoint or os.environ.get(
                consts.DEFAULT_COLLECTOR_ENDPOINT
            )
            self.exporter_type = exporter_type or os.environ.get(
                consts.KEY_EXPORTER_TYPE
            )

            if self.cisco_token is None:
                print("Can not initiate cisco-otel launcher without token")
                raise ValueError

            if self.exporter_type not in consts.ALLOWED_EXPORTER_TYPES:
                print("Unsupported exported type")
                raise ValueError

        except ValueError:
            raise
