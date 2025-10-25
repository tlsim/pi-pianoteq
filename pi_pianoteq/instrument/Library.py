from typing import List, Dict
import logging

from pi_pianoteq.instrument.Instrument import Instrument
from pi_pianoteq.instrument.Preset import Preset
from pi_pianoteq.midi.util import program_numbers_by_channel

logger = logging.getLogger(__name__)


class Library:
    def __init__(self, preset_names: List[str], instruments: List[Instrument]):
        self.preset_names = preset_names
        self.presets: List[Preset] = [Preset(name) for name in preset_names]
        self.instruments: List[Instrument] = instruments
        self.group_presets_by_instrument()
        self.assign_midi_program_numbers()

    def group_presets_by_instrument(self) -> None:
        for preset in self.presets:
            inst = next((i for i in self.instruments if preset.name.find(i.preset_prefix) == 0), None)
            if inst is not None:
                inst.add_preset(preset)

    def get_instruments(self) -> List[Instrument]:
        return [i for i in self.instruments if len(i.presets) > 0]

    def assign_midi_program_numbers(self):
        generator = program_numbers_by_channel()
        for inst in self.get_instruments():
            for preset in inst.presets:
                try:
                    preset.midi_channel, preset.midi_program_number = next(generator)
                except StopIteration:
                    logger.error(
                        'Failed to assign midi program change number to all presets - '
                        'there were insufficient channels / program numbers available'
                    )
                    return
