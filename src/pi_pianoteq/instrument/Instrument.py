from typing import List

from pi_pianoteq.instrument.Preset import Preset


class Instrument:

    def __init__(self, name: str, preset_prefix: str, bg_primary: str, bg_secondary: str):
        self.name = name
        self.preset_prefix = preset_prefix
        self.background_primary = bg_primary
        self.background_secondary = bg_secondary
        self.presets: List[Preset] = []

    def add_preset(self, preset: Preset):
        self.presets.append(preset)
