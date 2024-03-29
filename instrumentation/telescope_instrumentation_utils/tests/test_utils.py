import unittest

from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace

from cisco_telescope import consts
from cisco_telescope.configuration import Configuration
from instrumentation import telescope_instrumentation_utils


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        context = trace_api.SpanContext(
            trace_id=0x000000000000000000000000DEADBEEF,
            span_id=0x00000000DEADBEF0,
            is_remote=False,
        )

        self._test_span = trace._Span("test_span", context=context)
        self._test_span.start()

    def tearDown(self) -> None:
        self._test_span.end()
        Configuration().reset_to_default()

    def test_lowered_case_items(self):
        lowered_items = telescope_instrumentation_utils.Utils.lowercase_items(
            {"Cisco-Label": "Don't touch me", "Another One": "YAP"}
        )

        self.assertDictEqual(
            lowered_items, {"cisco-label": "Don't touch me", "another one": "YAP"}
        )

    def test_add_flattened_dict(self):
        test_dict = telescope_instrumentation_utils.Utils.lowercase_items(
            {"Cisco-Label": "Don't touch me", "Another One": "YAP"}
        )

        telescope_instrumentation_utils.Utils.add_flattened_dict(
            self._test_span, "test.attrs", test_dict
        )

        for test_key, test_value in test_dict.items():
            self.assertEqual(
                self._test_span.attributes.get(f"test.attrs.{test_key}"), test_value
            )

    def test_set_payload_sanity(self):
        telescope_instrumentation_utils.Utils.set_payload(
            self._test_span, "test.payload", "test payload"
        )
        self.assertEqual(self._test_span.attributes.get("test.payload"), "test payload")

    def test_set_payload_none(self):
        telescope_instrumentation_utils.Utils.set_payload(
            self._test_span, "test.payload", None
        )
        self.assertEqual(self._test_span.attributes.get("test.payload"), "")

    def test_set_payload_bytes_sanity(self):
        payload = bytes("test bytes", "utf8")
        telescope_instrumentation_utils.Utils.set_payload(
            self._test_span, "test.payload", payload
        )

        self.assertIsInstance(self._test_span.attributes.get("test.payload"), str)
        self.assertEqual(
            self._test_span.attributes.get("test.payload"), payload.decode("utf8")
        )

    def test_set_payload_bytes_non_utf8(self):
        payload = bytes("🙀", "utf16")
        telescope_instrumentation_utils.Utils.set_payload(
            self._test_span, "test.payload", payload
        )

        self.assertIsInstance(self._test_span.attributes.get("test.payload"), str)
        self.assertEqual(
            self._test_span.attributes.get("test.payload"),
            payload.decode(
                consts.ENCODING_UTF8, consts.DECODE_PAYLOAD_IN_CASE_OF_ERROR
            ),
        )

    def test_set_payload_above_max_payload_size(self):
        payload = bytes("test bytes", "utf8")
        Configuration().max_payload_size = 5
        telescope_instrumentation_utils.Utils.set_payload(
            self._test_span, "test.payload", payload
        )

        self.assertIsInstance(self._test_span.attributes.get("test.payload"), str)
        self.assertEqual(
            self._test_span.attributes.get("test.payload"), payload.decode("utf8")[:5]
        )
