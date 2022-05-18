import logging
from cisco_telescope.instrumentations.requests import RequestsInstrumentorWrapper
from cisco_telescope.instrumentations.aiohttp import AiohttpInstrumentorWrapper
from cisco_telescope.instrumentations.grpc import GrpcInstrumentorServerWrapper
from cisco_telescope.instrumentations.grpc import GrpcInstrumentorClientWrapper
from .. import consts, options


class InstrumentationWrapper:

    _INSTRUMENTATION_STATE = {}

    @classmethod
    def get_wrappers(cls):
        return {
            consts.REQUESTS_KEY: RequestsInstrumentorWrapper,
            consts.AIOHTTP_KEY: AiohttpInstrumentorWrapper,
            consts.GRPC_SERVER_KEY: GrpcInstrumentorServerWrapper,
            consts.GRPC_CLIENT_KEY: GrpcInstrumentorClientWrapper,
        }

    @classmethod
    def is_already_instrumented(cls, library_key):
        """check if an instrumentation wrapper is already registered"""
        return library_key in cls._INSTRUMENTATION_STATE.keys()

    @classmethod
    def get_instrumentation_wrapper(cls, opt: options.Options, library_key):
        """load and initialize an instrumentation wrapper"""
        if cls.is_already_instrumented(library_key):
            return None
        try:
            inst_dict = InstrumentationWrapper.get_wrappers()
            if library_key in inst_dict:
                wrapper_object = inst_dict[library_key]
                wrapper_instance = wrapper_object()
                cls._mark_as_instrumented(library_key, wrapper_instance)
                return wrapper_instance
            else:
                logging.info(f"No instrumentation wrapper for {library_key}")
                return
        except Exception:
            logging.exception(
                f"Error while attempting to load instrumentation wrapper for {library_key}"
            )
            return

    @classmethod
    def uninstrument_all(cls):
        for key in cls._INSTRUMENTATION_STATE:
            cls._INSTRUMENTATION_STATE[key].uninstrument()

        cls._INSTRUMENTATION_STATE.clear()

    @classmethod
    def _mark_as_instrumented(cls, library_key, wrapper_instance):
        """mark an instrumentation wrapper as registered"""
        cls._INSTRUMENTATION_STATE[library_key] = wrapper_instance
