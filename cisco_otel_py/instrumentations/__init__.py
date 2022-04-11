from cisco_otel_py import consts


# This is a base class for all Instrumentation wrapper classes
class BaseInstrumentorWrapper:
    def __init__(
        self,
    ):
        super().__init__()
        self.max_payload_size: int = consts.MAX_PAYLOAD_SIZE

    def set_payload_max_size(self, max_payload_size) -> None:
        print("Setting self.max_payload_size to %s." % max_payload_size)
        self.max_payload_size = max_payload_size
