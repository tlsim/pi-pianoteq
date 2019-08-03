from typing import List


class Instrument:

    def __init__(self, name: str):
        self.name = name
        self.presets: List[str] = []

    def add_preset(self, preset: str):
        self.presets.append(preset)
