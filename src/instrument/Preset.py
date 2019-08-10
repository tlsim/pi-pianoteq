from typing import Optional


class Preset:
    def __init__(self, name: str):
        self.name = name
        self.midi_program_number: Optional[int] = None
        self.midi_channel: Optional[int] = None
