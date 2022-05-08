import unittest

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)

from cisco_telescope import consts, options, exporter_factory
from cisco_opentelemetry_specifications import Consts

from . import utils


class TestExporterFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_options = options.Options(cisco_token=utils.TEST_TOKEN)

    def test_otlp_grpc_exporter(self):
        self.test_options.exporters = [
            options.ExporterOptions(
                exporter_type=consts.GRPC_EXPORTER_TYPE,
                collector_endpoint="my-end",
            )
        ]
        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPGrpcExporter)
        self.assertEqual(
            otlp_exporter._headers, ((Consts.TOKEN_HEADER_KEY, utils.TEST_TOKEN),)
        )

    def test_otlp_http_exporter(self):
        self.test_options.exporters = [
            options.ExporterOptions(
                exporter_type=consts.HTTP_EXPORTER_TYPE,
                collector_endpoint="my-end",
            )
        ]
        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPHTTPExporter)
        self.assertEqual(
            otlp_exporter._headers, {Consts.TOKEN_HEADER_KEY: utils.TEST_TOKEN}
        )
        self.assertEqual(otlp_exporter._endpoint, "my-end")

    def test_console_exporter(self):
        self.test_options.exporters = [
            options.ExporterOptions(
                exporter_type=consts.CONSOLE_EXPORTER_TYPE,
            )
        ]
        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 1)

        console_exporter = exporters[0]
        self.assertIsInstance(console_exporter, ConsoleSpanExporter)

    def test_multiple_exporters(self):
        self.test_options.exporters = [
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

        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 3)
