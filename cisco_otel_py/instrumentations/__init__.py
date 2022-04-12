from .. import consts, options


class BaseInstrumentorWrapper:
    """This is a base class for all Instrumentation wrapper classes"""

    def __init__(self):
        super().__init__()
        self._max_payload_size: int = consts.MAX_PAYLOAD_SIZE

    def set_options(self, opt: options.Options):
        self._max_payload_size = opt.max_payload_size
