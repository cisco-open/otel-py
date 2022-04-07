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

from cisco_otel_py import options, consts
from . import utils


def test_default():
    opt = options.Options(
        cisco_token=utils.TEST_TOKEN,
        exporters=[options.ExporterOptions(exporter_type=consts.CONSOLE_EXPORTER_TYPE)],
    )

    assert opt.service_name == consts.DEFAULT_SERVICE_NAME
    assert opt.cisco_token == utils.TEST_TOKEN
    assert opt.exporters[0].collector_endpoint == consts.DEFAULT_COLLECTOR_ENDPOINT
