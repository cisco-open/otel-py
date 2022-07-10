import pymongo
from cisco_telescope.configuration import Configuration
from cisco_telescope.instrumentations.pymongo import PymongoInstrumentorWrapper
from opentelemetry.test.test_base import TestBase
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.semconv.trace import SpanAttributes
from .base_http_test import BaseHttpTest
from .. import utils


class TestPymongoWrapper(BaseHttpTest, TestBase):
    def setUp(self) -> None:
        super().setUp()
        PymongoInstrumentorWrapper().instrument()
        self.client = pymongo.MongoClient(
            f"mongodb://{utils.MONGODB_HOST}:{utils.MONGODB_PORT}/"
        )
        self.db = self.client["database"]
        self.col = self.db["customers"]
        costumer = utils.MONGODB_RECORD
        self.col.insert_one(costumer)

    def tearDown(self) -> None:
        super().tearDown()
        PymongoInstrumentorWrapper().uninstrument()
        Configuration().reset_to_default()
        self.col.drop()
        self.client.close()

    def test_otel_attributes_unharmed(self):
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        span = spans[0]
        print(span)

        self.assertEqual(span.attributes[SpanAttributes.DB_SYSTEM], "mongodb")
        self.assertEqual(span.attributes[SpanAttributes.DB_NAME], "database")
        self.assertEqual(
            span.attributes[SpanAttributes.NET_PEER_PORT], utils.MONGODB_PORT
        )
        self.assertEqual(
            span.attributes[SpanAttributes.NET_PEER_NAME], utils.MONGODB_HOST
        )
        self.assertEqual(
            span.attributes[SpanAttributes.DB_STATEMENT], "insert customers"
        )

    def test_insert(self):
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        span = spans[0]
        self.assertIn(
            utils.MONGODB_RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_ARGUMENTS],
        )
        self.assertIn(
            utils.MONGODB_SUCCESS_RESPONSE,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_find(self):
        self.col.find_one()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)
        span = spans[1]

        self.assertIn(
            utils.MONGODB_RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_update(self):
        new_record = {"$set": {"address": "Canyon 123"}}
        self.col.update_one(utils.MONGODB_RECORD, new_record)
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)
        span = spans[1]

        self.assertNotIn(
            utils.MONGODB_RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

        self.assertIn(
            utils.MONGODB_SUCCESS_RESPONSE,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )
