from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.instrument.Library import Library
from pi_pianoteq.midi.ProgramChange import ProgramChange


class ClientLib(ClientApi):
    def __init__(self, instrument_library: Library, program_change: ProgramChange):
        self.program_change = program_change
        self.instrument_library = instrument_library
        # TODO: wait for PTQ
        # program_change.set_preset(instrument_library.get_current_preset())

    def set_preset_next(self) -> None:
        self.instrument_library.set_preset_next()
        self.program_change.set_preset(self.instrument_library.get_current_preset())

    def set_preset_prev(self) -> None:
        self.instrument_library.set_preset_prev()
        self.program_change.set_preset(self.instrument_library.get_current_preset())

    def get_current_preset(self) -> str:
        return self.instrument_library.get_current_preset().name
