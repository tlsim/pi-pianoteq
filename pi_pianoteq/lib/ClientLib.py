from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.instrument.Library import Library
from pi_pianoteq.instrument.Selector import Selector
from pi_pianoteq.midi.ProgramChange import ProgramChange
from pi_pianoteq.config import Config

from typing import List
from time import sleep

class ClientLib(ClientApi):

    def __init__(self, instrument_library: Library, selector: Selector, program_change: ProgramChange):
        self.program_change = program_change
        self.instrument_library = instrument_library
        self.selector = selector
        self.reset_initial_preset()

    def reset_initial_preset(self) -> None:
        sleep(Config.MIDI_PIANOTEQ_STARTUP_DELAY)
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_next(self) -> None:
        self.selector.set_preset_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_prev(self) -> None:
        self.selector.set_preset_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_next(self) -> None:
        self.selector.set_instrument_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument(self, name) -> None:
        self.selector.set_instrument(name)
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_prev(self) -> None:
        self.selector.set_instrument_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def get_instrument_names(self) -> List[str]:
        return [i.name for i in self.instrument_library.get_instruments()]

    def get_current_preset(self) -> str:
        return self.selector.get_current_preset().name

    def get_current_instrument(self) -> str:
        return self.selector.get_current_instrument().name

    def get_current_background_primary(self) -> str:
        return self.selector.get_current_instrument().background_primary

    def get_current_background_secondary(self) -> str:
        return self.selector.get_current_instrument().background_secondary

