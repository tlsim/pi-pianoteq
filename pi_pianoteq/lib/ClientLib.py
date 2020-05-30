from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.instrument.Library import Library
from pi_pianoteq.instrument.Selector import Selector
from pi_pianoteq.midi.ProgramChange import ProgramChange


class ClientLib(ClientApi):
    def __init__(self, instrument_library: Library, selector: Selector, program_change: ProgramChange):
        self.program_change = program_change
        self.instrument_library = instrument_library
        self.selector = selector
        # TODO: wait for PTQ
        # program_change.set_preset(instrument_library.get_current_preset())

    def set_preset_next(self) -> None:
        self.selector.set_preset_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_prev(self) -> None:
        self.selector.set_preset_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_next(self) -> None:
        self.selector.set_instrument_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_prev(self) -> None:
        self.selector.set_instrument_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def get_current_preset(self) -> str:
        return self.selector.get_current_preset().name

    def get_current_instrument(self) -> str:
        return self.selector.get_current_instrument().name
