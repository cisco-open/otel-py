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

import unittest

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)

from telescope_instrumentor.src import options
from telescope_instrumentor.src import exporter_factory, consts
from cisco_opentelemetry_specifications import Consts

from . import utils


class TestExporterFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_default_exporter(self):
        opt = options.Options(cisco_token=utils.TEST_TOKEN)
        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPHTTPExporter)
        self.assertEqual(
            otlp_exporter._headers,
            {Consts.TOKEN_HEADER_KEY: "Bearer " + utils.TEST_TOKEN},
        )

    def test_default_exporter_bearer_token(self):
        opt = options.Options(cisco_token="Bearer " + utils.TEST_TOKEN)
        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertEqual(
            otlp_exporter._headers,
            {Consts.TOKEN_HEADER_KEY: "Bearer " + utils.TEST_TOKEN},
        )

    def test_custom_otlp_grpc_exporter(self):
        opt = options.Options(
            exporters=[
                options.ExporterOptions(
                    exporter_type=consts.GRPC_EXPORTER_TYPE,
                    collector_endpoint=utils.COLLECTOR_ENDPOINT,
                    custom_headers={utils.CUSTOM_HEADER_KEY: utils.CUSTOM_HEADER_VALUE},
                )
            ]
        )
        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPGrpcExporter)
        self.assertEqual(
            otlp_exporter._headers,
            ((utils.CUSTOM_HEADER_KEY, utils.CUSTOM_HEADER_VALUE),),
        )

    def test_custom_otlp_http_exporter(self):
        opt = options.Options(
            exporters=[
                options.ExporterOptions(
                    exporter_type=consts.HTTP_EXPORTER_TYPE,
                    collector_endpoint=utils.COLLECTOR_ENDPOINT,
                    custom_headers={utils.CUSTOM_HEADER_KEY: utils.CUSTOM_HEADER_VALUE},
                )
            ]
        )
        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPHTTPExporter)
        self.assertEqual(otlp_exporter._endpoint, utils.COLLECTOR_ENDPOINT)
        self.assertEqual(
            otlp_exporter._headers,
            {utils.CUSTOM_HEADER_KEY: utils.CUSTOM_HEADER_VALUE},
        )

    def test_console_exporter(self):
        opt = options.Options(
            exporters=[
                options.ExporterOptions(exporter_type=consts.CONSOLE_EXPORTER_TYPE)
            ]
        )
        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 1)

        console_exporter = exporters[0]
        self.assertIsInstance(console_exporter, ConsoleSpanExporter)

    def test_multiple_exporters(self):
        opt = options.Options(
            exporters=[
                options.ExporterOptions(
                    exporter_type=consts.GRPC_EXPORTER_TYPE,
                ),
                options.ExporterOptions(
                    exporter_type=consts.HTTP_EXPORTER_TYPE,
                ),
                options.ExporterOptions(
                    exporter_type=consts.CONSOLE_EXPORTER_TYPE,
                ),
            ]
        )

        exporters = exporter_factory.init_exporters(opt)
        self.assertEqual(len(exporters), 3)
