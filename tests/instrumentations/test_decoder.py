import json
from datetime import datetime
from cisco_telescope.instrumentations.pymongo import (
    ObjectIDEncoder,
)
from opentelemetry.test.test_base import TestBase
from tests.instrumentations.base_http_tests_util import BaseHttpTest


class TestJsonEncoder(BaseHttpTest, TestBase):
    def test_json_with_double(self):
        person = {"name": "John", "age": 10.5}
        json_str = json.dumps(person, cls=ObjectIDEncoder, skipkeys=True)
        self.assertEqual(json_str, '''{"name": "John", "age": 10.5}''')  # fmt: skip

    def test_json_with_boolean(self):
        person = {
            "name": "John",
            "isAChild": False,
        }
        json_str = json.dumps(person, cls=ObjectIDEncoder, skipkeys=True)
        self.assertEqual(json_str, '''{"name": "John", "isAChild": false}''')  # fmt: skip

    def test_json_with_integer(self):
        person = {"name": "John", "age": 30, "city": "New York"}
        json_str = json.dumps(person, cls=ObjectIDEncoder, skipkeys=True)
        self.assertEqual(json_str, '''{"name": "John", "age": 30, "city": "New York"}''')  # fmt: skip

    def test_json_with_array(self):
        array = ["Ford", "Volvo", 50]
        person = {"name": "John", "preferred cars": array}
        json_str = json.dumps(person, cls=ObjectIDEncoder, skipkeys=True)
        self.assertEqual(json_str, '''{"name": "John", "preferred cars": ["Ford", "Volvo", 50]}''')  # fmt: skip

    def test_json_with_null(self):
        person = {"name": "John", "hobbies": None}
        json_str = json.dumps(person, cls=ObjectIDEncoder, skipkeys=True)
        self.assertEqual(json_str, '''{"name": "John", "hobbies": null}''')  # fmt: skip

    def test_json_with_timestamp(self):
        with self.assertLogs() as captured:
            timestamp = 1577872800  # selected date: 1/1/2020 10:00:00
            dt_object = datetime.utcfromtimestamp(timestamp)
            json_str = json.dumps(
                {"created_at": dt_object}, cls=ObjectIDEncoder, skipkeys=True
            )
            self.assertEqual(json_str, '''{"created_at": "2020-01-01 10:00:00"}''')  # fmt: skip
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(
                "Could not decode object of type" in captured.records[0].getMessage(),
                True,
            )
