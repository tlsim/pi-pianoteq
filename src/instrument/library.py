from typing import List, Dict, Tuple, Iterator
from sys import stderr
from instrument.Instrument import Instrument
from instrument.Preset import Preset
from constants import UNKNOWN_INSTRUMENT
from os import path


def get_instruments() -> List[str]:
    with open(path.join(path.dirname(__file__), 'instruments')) as instruments:
        return instruments.read().splitlines()


def midi_program_numbers_by_channel(from_channel: int = 0) -> Iterator[Tuple[int, int]]:
    program_number = 0
    channel_number = from_channel
    while channel_number < 16:
        while program_number < 128:
            yield (channel_number, program_number)
            program_number += 1
        program_number = 0
        channel_number += 1


class Library:
    def __init__(self, preset_names: List[str], instrument_names: List[str]):
        self.preset_names = preset_names
        self.instrument_names = instrument_names
        self.presets: List[Preset] = [Preset(name) for name in preset_names]
        self.instruments: Dict[str, Instrument] = self.group_presets_by_instrument()
        self.assign_midi_program_numbers()

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

    def get_known_instruments(self) -> List[Instrument]:
        return [i for i in self.get_all_instruments() if i.name != UNKNOWN_INSTRUMENT]

    def get_all_instruments(self) -> List[Instrument]:
        return [i for i in self.instruments.values() if len(i.presets) > 0]

    def assign_midi_program_numbers(self):
        generator = midi_program_numbers_by_channel()
        for inst in self.get_all_instruments():
            for preset in inst.presets:
                try:
                    preset.midi_channel, preset.midi_program_number = next(generator)
                except StopIteration:
                    print('Failed to assign midi program change number to all presets - '
                          'there were insufficient channels / program numbers available', file=stderr)
                    return
