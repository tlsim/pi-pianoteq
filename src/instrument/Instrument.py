from typing import List
from instrument.Preset import Preset


class Instrument:

    def __init__(self, name: str):
        self.name = name
        self.presets: List[Preset] = []

    def add_preset(self, preset: Preset):
        self.presets.append(preset)
