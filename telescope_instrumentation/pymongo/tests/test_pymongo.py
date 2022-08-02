import pymongo
from pymongo.errors import DuplicateKeyError

from telescope_instrumentor.configuration import Configuration
from telescope_instrumentation.pymongo import PymongoInstrumentorWrapper
from opentelemetry.test.test_base import TestBase
from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.semconv.trace import SpanAttributes
from telescope_instrumentation.utils.base_http_tests_util import BaseHttpTest


class TestPymongoWrapper(BaseHttpTest, TestBase):
    SUCCESS_RESPONSE = '"ok": 1.0'
    RECORD = {"name": "John", "address": "Highway 37"}
    RECORD_STRIPPED = '"name": "John", "address": "Highway 37"'
    DB_HOST = "localhost"
    DB_PORT = 27017

    def setUp(self) -> None:
        super().setUp()
        PymongoInstrumentorWrapper().instrument()
        self.client = pymongo.MongoClient(f"mongodb://{self.DB_HOST}:{self.DB_PORT}/")
        db = self.client["database"]
        self.col = db["customers"]
        self.col.insert_one(self.RECORD)

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
        self.assertEqual(span.attributes[SpanAttributes.NET_PEER_PORT], self.DB_PORT)
        self.assertEqual(span.attributes[SpanAttributes.NET_PEER_NAME], self.DB_HOST)
        self.assertEqual(
            span.attributes[SpanAttributes.DB_STATEMENT], "insert customers"
        )

    def test_insert(self):
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        span = spans[0]
        self.assertIn(
            self.RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_ARGUMENTS],
        )
        self.assertIn(
            self.SUCCESS_RESPONSE,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_find(self):
        self.col.find_one()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)
        span = spans[1]

        self.assertIn(
            self.RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_update(self):
        new_record = {"$set": {"address": "Canyon 123"}}
        self.col.update_one(self.RECORD, new_record)
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)
        span = spans[1]

        self.assertNotIn(
            self.RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

        self.assertIn(
            self.SUCCESS_RESPONSE,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_collection_drop(self):
        self.col.drop()
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)
        span = spans[1]

        self.assertNotIn(SemanticAttributes.DB_MONGODB_ARGUMENTS, span.attributes)

    def test_find_none(self):
        self.col.drop()
        x = self.col.find_one()
        self.assertIsNone(x)
        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 3)
        span = spans[2]
        self.assertNotIn(
            self.RECORD_STRIPPED,
            span.attributes[SemanticAttributes.DB_MONGODB_RESPONSE],
        )

    def test_duplicate_ket_error(self):
        with self.assertRaisesRegex(DuplicateKeyError, "E11000 duplicate key error"):
            self.col.insert_one(self.RECORD)
            spans = self.memory_exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[1]
            self.assertIn(
                self.RECORD_STRIPPED,
                span.attributes[SemanticAttributes.DB_MONGODB_ARGUMENTS],
            )
