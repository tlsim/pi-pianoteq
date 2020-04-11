from typing import List, Dict
from sys import stderr
from instrument.Instrument import Instrument
from instrument.Preset import Preset
from constants import UNKNOWN_INSTRUMENT
from midi.util import program_numbers_by_channel
from os import path


def get_instruments() -> List[str]:
    with open(path.join(path.dirname(__file__), 'instruments')) as instruments:
        return instruments.read().splitlines()


class Library:
    def __init__(self, preset_names: List[str], instrument_names: List[str]):
        self.preset_names = preset_names
        self.instrument_names = instrument_names
        self.presets: List[Preset] = [Preset(name) for name in preset_names]
        self.instruments: Dict[str, Instrument] = self.group_presets_by_instrument()
        self.assign_midi_program_numbers()
        self.current_preset_idx: int = 0

    def group_presets_by_instrument(self) -> Dict[str, Instrument]:
        instruments = {name: Instrument(name) for name in self.instrument_names}
        instruments[UNKNOWN_INSTRUMENT] = Instrument(UNKNOWN_INSTRUMENT)
        for preset in self.presets:
            inst = next((i for i in self.instrument_names if preset.name.find(i) == 0), None)
            if inst is not None:
                instruments[inst].add_preset(preset)
            else:
                instruments[UNKNOWN_INSTRUMENT].add_preset(preset)
        return instruments

    def get_instruments(self) -> List[Instrument]:
        return [i for i in self.instruments.values() if len(i.presets) > 0]

    def assign_midi_program_numbers(self):
        generator = program_numbers_by_channel()
        for inst in self.get_instruments():
            for preset in inst.presets:
                try:
                    preset.midi_channel, preset.midi_program_number = next(generator)
                except StopIteration:
                    print('Failed to assign midi program change number to all presets - '
                          'there were insufficient channels / program numbers available', file=stderr)
                    return

    def get_current_preset(self) -> Preset:
        return self.presets[self.current_preset_idx]

    def set_preset_next(self) -> None:
        self.current_preset_idx = (self.current_preset_idx + 1) % len(self.presets)

    def set_preset_prev(self) -> None:
        self.current_preset_idx = (self.current_preset_idx - 1) % len(self.presets)
