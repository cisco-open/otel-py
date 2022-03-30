from cisco_otel_py.consts import REQUESTS_KEY

_INSTRUMENTATION_STATE = {}


def uninstrument_all():
    for key in _INSTRUMENTATION_STATE:
        _INSTRUMENTATION_STATE[key].uninstrument()

    _INSTRUMENTATION_STATE.clear()


def is_already_instrumented(library_key):
    """check if an instrumentation wrapper is already registered"""
    return library_key in _INSTRUMENTATION_STATE.keys()


def _mark_as_instrumented(library_key, wrapper_instance):
    """mark an instrumentation wrapper as registered"""
    _INSTRUMENTATION_STATE[library_key] = wrapper_instance


def get_instrumentation_wrapper(library_key, max_payload_size):
    """load an initialize an instrumentation wrapper"""
    if is_already_instrumented(library_key):
        return None
    try:
        wrapper_instance = None
        if REQUESTS_KEY == library_key:
            from .requests import RequestsInstrumentorWrapper

            wrapper_instance = RequestsInstrumentorWrapper()
            wrapper_instance.set_process_request_headers(True)
            wrapper_instance.set_process_request_body(True, max_payload_size)
        else:
            return None

        _mark_as_instrumented(library_key, wrapper_instance)
        return wrapper_instance
    except Exception as _err:  # pylint:disable=W0703
        print(
            f"Error while attempting to load instrumentation wrapper for {library_key}"
        )
        return None
