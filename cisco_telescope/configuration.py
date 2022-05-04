from . import options

from cisco_opentelemetry_specifications.consts import Consts


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Configuration(object):
    def __init__(self):
        self.reset_to_default()

    def reset_to_default(self):
        self._max_payload_size: int = Consts.DEFAULT_MAX_PAYLOAD_SIZE
        self._payloads_enabled: bool = Consts.DEFAULT_PAYLOADS_ENABLED

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
