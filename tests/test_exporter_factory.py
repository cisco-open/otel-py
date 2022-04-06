import unittest

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPExporter,
)

from cisco_otel_py import consts, options, exporter_factory


class TestExporterFactory(unittest.TestCase):
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_options = options.Options(cisco_token='sometoken')

    def test_otlp_exporter(self):
        self.test_options.exporters = [options.ExporterOptions(
            exporter_type=consts.GRPC_EXPORTER_TYPE,
            collector_endpoint='my-end'
        )]

        exporters = exporter_factory.init_exporters(self.test_options)
        self.assertEqual(len(exporters), 1)

        otlp_exporter = exporters[0]
        self.assertIsInstance(otlp_exporter, OTLPGrpcExporter)
        import ipdb;ipdb.set_trace()

