from cisco_otel_py.instrumentations.wrappers import Wrapper

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


def get_instrumentation_wrapper(library_key):
    """load and initialize an instrumentation wrapper"""
    if is_already_instrumented(library_key):
        return None
    try:
        inst_dict = Wrapper.get_wrappers()
        if library_key in inst_dict:
            wrapper_object = inst_dict[library_key]
            wrapper_instance = wrapper_object();
            _mark_as_instrumented(library_key, wrapper_instance)
            return wrapper_instance
        else:
            print("No instrumentation wrapper for %s" % library_key)
            return None
    except Exception as err:
        print(
            "Error while attempting to load instrumentation wrapper for %s"
            % err
        )
        return None
