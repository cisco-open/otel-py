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
import unittest
from unittest import mock

from cisco_otel_py import options, consts

from . import utils


class TestOptions(unittest.TestCase):
    def test_defaults(self):
        opt = options.Options(cisco_token=utils.TEST_TOKEN)

        self.assertEqual(opt.service_name, consts.DEFAULT_SERVICE_NAME)
        self.assertEqual(opt.exporters, [options.ExporterOptions()])
        self.assertEqual(opt.max_payload_size, consts.MAX_PAYLOAD_SIZE)

    def test_empty_exporter_defaults(self):
        opt = options.Options(cisco_token=utils.TEST_TOKEN, exporters=[])

        self.assertEqual(opt.exporters, [options.ExporterOptions()])

    def test_parameters(self):
        exporters = [
            options.ExporterOptions(
                exporter_type=consts.HTTP_EXPORTER_TYPE, collector_endpoint="endpoint"
            )
        ]
        opt = options.Options(
            cisco_token=utils.TEST_TOKEN,
            service_name="Service",
            max_payload_size=1023,
            exporters=exporters,
        )

        self.assertEqual(opt.cisco_token, utils.TEST_TOKEN)
        self.assertEqual(opt.service_name, "Service")
        self.assertEqual(opt.max_payload_size, 1023)
        self.assertEqual(opt.exporters, exporters)

    @mock.patch.dict(
        os.environ,
        {consts.KEY_SERVICE_NAME: "Service", consts.KEY_TOKEN: utils.TEST_TOKEN},
    )
    def test_parameters_from_env(self):
        opt = options.Options()

        self.assertEqual(opt.cisco_token, utils.TEST_TOKEN)
        self.assertEqual(opt.service_name, "Service")

    def test_token_is_missing(self):
        with self.assertRaisesRegex(
            ValueError, "Can not initiate cisco-otel launcher without token"
        ):
            _ = options.Options()


class TestExporterOptions(unittest.TestCase):
    def test_defaults(self):
        exporter_opts = options.ExporterOptions()

        self.assertEqual(exporter_opts.exporter_type, consts.DEFAULT_EXPORTER_TYPE)
        self.assertEqual(
            exporter_opts.collector_endpoint, consts.DEFAULT_COLLECTOR_ENDPOINT
        )

    @mock.patch.dict(
        os.environ,
        {
            consts.KEY_COLLECTOR_ENDPOINT: "env_endpoint",
            consts.KEY_EXPORTER_TYPE: consts.HTTP_EXPORTER_TYPE,
        },
    )
    def test_parameters_from_env(self):
        exporter_opts = options.ExporterOptions()

        self.assertEqual(exporter_opts.exporter_type, consts.HTTP_EXPORTER_TYPE)
        self.assertEqual(exporter_opts.collector_endpoint, "env_endpoint")

    def test_parameters(self):
        exporter_opts = options.ExporterOptions(
            consts.HTTP_EXPORTER_TYPE, "collector_endpoint"
        )

        self.assertEqual(exporter_opts.exporter_type, consts.HTTP_EXPORTER_TYPE)
        self.assertEqual(exporter_opts.collector_endpoint, "collector_endpoint")

    def test_token_is_missing(self):
        with self.assertRaisesRegex(ValueError, "Unsupported exported type"):
            _ = options.ExporterOptions(exporter_type="unsupported-type")
