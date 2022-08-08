"""Copyright The Cisco Authors.

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
import json

from kafka import KafkaConsumer, KafkaProducer

from opentelemetry.test.test_base import TestBase

from cisco_opentelemetry_specifications import SemanticAttributes
from opentelemetry.trace import SpanKind

from cisco_telescope.configuration import Configuration
from cisco_telescope.instrumentations.kafka import KafkaInstrumentorWrapper


class TestKafkaWrapper(TestBase):
    def setUp(self) -> None:
        super().setUp()
        KafkaInstrumentorWrapper().instrument()

    def tearDown(self) -> None:
        super().tearDown()
        KafkaInstrumentorWrapper().uninstrument()
        Configuration().reset_to_default()

    def test_get_request_sanity(self):
        Configuration().payloads_enabled = True

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        producer.send('test-topic', b'test message')

        consumer = KafkaConsumer('test-topic',
                                 group_id='my-group',
                                 bootstrap_servers=['localhost:9092'])

        for message in consumer:
            print(message)
            break

        spans = self.memory_exporter.get_finished_spans()
        self.assertEqual(len(spans), 2)

        producer_span = spans[0]
        consumer_span = spans[1]

        self.assertEqual(producer_span.kind, SpanKind.PRODUCER)
        # TODO: use semanticAttributes
        self.assertEqual(producer_span.attributes[f"messaging.value"], 'test message')

        self.assertEqual(consumer_span.kind, SpanKind.CONSUMER)
        # TODO: use semanticAttributes
        self.assertEqual(consumer_span.attributes[f"messaging.value"], 'test message')
