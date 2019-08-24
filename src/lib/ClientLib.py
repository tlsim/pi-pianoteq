from client.ClientApi import ClientApi
from midi.ProgramChange import ProgramChange
from instrument.Library import Library


class ClientLib(ClientApi):
    def __init__(self, instrument_library: Library, program_change: ProgramChange):
        self.program_change = program_change
        self.instrument_library = instrument_library

    def set_preset_next(self) -> None:
        self.instrument_library.set_preset_next()
        self.program_change.set_preset(self.instrument_library.get_current_preset())

    def set_preset_prev(self) -> None:
        self.instrument_library.set_preset_prev()
        self.program_change.set_preset(self.instrument_library.get_current_preset())

    def get_current_preset(self) -> str:
        return self.instrument_library.get_current_preset().name
