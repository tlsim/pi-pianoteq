from sys import stderr
from typing import List, Dict

from pi_pianoteq.config import Config
from pi_pianoteq.instrument.Instrument import Instrument
from pi_pianoteq.instrument.Preset import Preset
from pi_pianoteq.midi.util import program_numbers_by_channel


class Library:
    def __init__(self, preset_names: List[str], instrument_names: List[str]):
        self.preset_names = preset_names
        self.instrument_names = instrument_names
        self.presets: List[Preset] = [Preset(name) for name in preset_names]
        self.instruments: Dict[str, Instrument] = self.group_presets_by_instrument()
        self.assign_midi_program_numbers()

    def group_presets_by_instrument(self) -> Dict[str, Instrument]:
        instruments = {name: Instrument(name) for name in self.instrument_names}
        instruments[Config.UNKNOWN_INSTRUMENT] = Instrument(Config.UNKNOWN_INSTRUMENT)
        for preset in self.presets:
            inst = next((i for i in self.instrument_names if preset.name.find(i) == 0), None)
            if inst is not None:
                instruments[inst].add_preset(preset)
            else:
                instruments[Config.UNKNOWN_INSTRUMENT].add_preset(preset)
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
