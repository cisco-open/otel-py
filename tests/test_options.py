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

from cisco_telescope import options, consts
from cisco_opentelemetry_specifications import Consts

from . import utils


class TestOptions(unittest.TestCase):
    def tearDown(self) -> None:
        utils.clean_env_vars([Consts.CISCO_DEBUG_ENV])

    def test_defaults(self):
        opt = options.Options(cisco_token=utils.TEST_TOKEN)
        self.assertEqual(opt.service_name, None)
        self.assertEqual(opt.debug, Consts.DEFAULT_CISCO_DEBUG)
        self.assertEqual(opt.max_payload_size, Consts.DEFAULT_MAX_PAYLOAD_SIZE)
        self.assertEqual(opt.payloads_enabled, Consts.DEFAULT_PAYLOADS_ENABLED)

    def test_parameters(self):
        exporters = [
            options.ExporterOptions(
                exporter_type=consts.HTTP_EXPORTER_TYPE,
                collector_endpoint="endpoint",
                custom_headers={"custom_header_key": "custom_header_value"},
            )
        ]
        opt = options.Options(
            cisco_token=utils.TEST_TOKEN,
            service_name="Service",
            max_payload_size=1023,
            exporters=exporters,
            debug=True,
            payloads_enabled=True,
        )

        self.assertEqual(opt.cisco_token, utils.TEST_TOKEN)
        self.assertEqual(opt.service_name, "Service")
        self.assertEqual(opt.debug, True)
        self.assertEqual(opt.payloads_enabled, True)
        self.assertEqual(opt.max_payload_size, 1023)
        self.assertEqual(opt.exporters, exporters)

    def test_redundant_token_warning(self):
        with self.assertLogs() as captured:
            exporters = [
                options.ExporterOptions(
                    exporter_type=consts.HTTP_EXPORTER_TYPE,
                    collector_endpoint="endpoint",
                    custom_headers={"custom_header_key": "custom_header_value"},
                )
            ]
            _ = options.Options(cisco_token=utils.TEST_TOKEN, exporters=exporters)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(
                captured.records[0].getMessage(),
                "Warning: Custom exporters do not use cisco token, it can be passed as a custom header",
            )

    @mock.patch.dict(
        os.environ,
        {
            Consts.CISCO_TOKEN_ENV: utils.TEST_TOKEN,
            Consts.CISCO_DEBUG_ENV: "True",
            Consts.CISCO_PAYLOADS_ENABLED_ENV: "True",
        },
    )
    def test_parameters_from_env(self):
        opt = options.Options()

        self.assertEqual(opt.cisco_token, utils.TEST_TOKEN)
        self.assertEqual(opt.debug, True)
        self.assertEqual(opt.payloads_enabled, True)

    def test_token_is_missing(self):
        with self.assertRaisesRegex(
            ValueError, "Can not initiate cisco-telescope without token"
        ):
            _ = options.Options()


class TestExporterOptions(unittest.TestCase):
    def test_defaults(self):
        exporter_opts = options.ExporterOptions(
            collector_endpoint=Consts.DEFAULT_COLLECTOR_ENDPOINT,
            exporter_type=Consts.DEFAULT_EXPORTER_TYPE,
        )

        self.assertEqual(exporter_opts.exporter_type, Consts.DEFAULT_EXPORTER_TYPE)
        self.assertEqual(
            exporter_opts.collector_endpoint, Consts.DEFAULT_COLLECTOR_ENDPOINT
        )

    def test_missing_collector_url_warning(self):
        with self.assertLogs() as captured:
            _ = options.ExporterOptions(exporter_type=Consts.DEFAULT_EXPORTER_TYPE)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(
                captured.records[0].getMessage(),
                "Warning: Custom exporter is set without collector endpoint",
            )

    def test_rm_collector_url_warning_on_console_exporter(self):
        with self.assertLogs() as captured:
            captured.records.append("dummy record to ensure no real record was generated")
            _ = options.ExporterOptions(exporter_type=consts.CONSOLE_EXPORTER_TYPE)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(
                captured.records[0],
                "dummy record to ensure no real record was generated",
            )

    @mock.patch.dict(
        os.environ,
        {
            Consts.OTEL_COLLECTOR_ENDPOINT: "env_endpoint",
            Consts.OTEL_EXPORTER_TYPE_ENV: consts.HTTP_EXPORTER_TYPE,
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
