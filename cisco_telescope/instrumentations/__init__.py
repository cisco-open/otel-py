from .. import consts, options


class BaseInstrumentorWrapper:
    """This is a base class for all Instrumentation wrapper classes"""

    def __init__(self):
        super().__init__()
        self._max_payload_size: int = consts.MAX_PAYLOAD_SIZE
        self._payloads_enabled: bool = consts.DEFAULT_PAYLOADS_ENABLED

    def set_options(self, opt: options.Options):
        self._max_payload_size = opt.max_payload_size
        self._payloads_enabled = opt.payloads_enabled

    @property
    def max_payload_size(self):
        return self._max_payload_size

    @max_payload_size.setter
    def max_payload_size(self, value):
        self._max_payload_size = value

    @property
    def payloads_enabled(self):
        return self._payloads_enabled

    @payloads_enabled.setter
    def payloads_enabled(self, value):
        self._payloads_enabled = value
