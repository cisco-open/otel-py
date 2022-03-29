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

from os import environ
import unittest
from cisco_otel_py import options, consts
from . import utils


def test_default():
    options.Options(cisco_token=utils.TEST_TOKEN)

    assert environ.get(consts.KEY_SERVICE_NAME) == consts.DEFAULT_SERVICE_NAME
    assert environ.get(consts.KEY_EXPORTER_TYPE) == consts.DEFAULT_EXPORTER_TYPE
    assert (
        environ.get(consts.KEY_COLLECTOR_ENDPOINT) == consts.DEFAULT_COLLECTOR_ENDPOINT
    )

    utils.clean_env_vars(
        [
            consts.KEY_SERVICE_NAME,
            consts.KEY_EXPORTER_TYPE,
            consts.KEY_COLLECTOR_ENDPOINT,
        ]
    )
