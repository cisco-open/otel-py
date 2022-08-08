from cisco_opentelemetry_specifications import SemanticAttributes
from kafka.consumer.fetcher import ConsumerRecord
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.sdk.trace import Span

from ..utils import Utils


def produce_hook(span: Span, args, kwargs):
    if not span.is_recording():
        return

    Utils.set_payload(
        span,
        # TODO: add to semantic attributes
        "messaging.value",
        args[1],
    )


def consume_hook(span: Span, record: ConsumerRecord, args, kwargs):
    if not span.is_recording():
        return

    Utils.set_payload(
        span,
        # TODO: add to semantic attributes
        "messaging.value",
        record.value,
    )


class KafkaInstrumentorWrapper(KafkaInstrumentor):
    def __init__(self):
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            produce_hook=produce_hook,
            consume_hook=consume_hook
        )

    def _uninstrument(self, **kwargs) -> None:
        super()._uninstrument()
