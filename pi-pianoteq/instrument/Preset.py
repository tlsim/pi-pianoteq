from typing import Optional


class Preset:
    def __init__(self, name: str):
        self.name = name
        self.midi_program_number: Optional[int] = None
        self.midi_channel: Optional[int] = None

    def has_midi_params(self) -> bool:
        return self.midi_program_number is not None and \
               self.midi_channel is not None
