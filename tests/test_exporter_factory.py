import unittest
from unittest.mock import patch

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)

from cisco_otel_py import consts, options, exporter_factory


class TestExporterFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_options = options.Options(cisco_token='sometoken')

    @patch("opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPGrpcExporter.__init__")
    def test_otlp_exporter(self, mock_otlp_grpc_exporter):
        import ipdb;ipdb.set_trace()
        self.test_options.exporters = [options.ExporterOptions(
            exporter_type=consts.GRPC_EXPORTER_TYPE,
            collector_endpoint='my-end'
        )]
        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPGrpcExporter)

