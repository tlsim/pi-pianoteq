from typing import List
from pi_pianoteq.instrument.Instrument import Instrument, Preset


class Selector:
    def __init__(self, instruments):
        self.instruments: List[Instrument] = instruments
        self.current_instrument_idx: int = 0
        self.current_instrument_preset_idx: int = 0

    def get_current_instrument(self) -> Instrument:
        return self.instruments[self.current_instrument_idx]

    def set_instrument_next(self) -> None:
        self.current_instrument_idx = (self.current_instrument_idx + 1) % len(self.instruments)
        self.current_instrument_preset_idx = 0

    def set_instrument_prev(self) -> None:
        self.current_instrument_idx = (self.current_instrument_idx - 1) % len(self.instruments)
        self.current_instrument_preset_idx = 0

    def set_instrument(self, name) -> None:
        instrument = next((i for i in self.instruments if name == i.name), None)
        if instrument is not None:
            self.current_instrument_idx = self.instruments.index(instrument)
            self.current_instrument_preset_idx = 0

    def get_current_preset(self) -> Preset:
        return self.get_current_instrument().presets[self.current_instrument_preset_idx]

    def set_preset_next(self) -> None:
        if self.current_instrument_preset_idx < len(self.get_current_instrument().presets) - 1:
            self.current_instrument_preset_idx += 1
        else:
            self.set_instrument_next()

    def set_preset_prev(self) -> None:
        if self.current_instrument_preset_idx == 0:
            self.set_instrument_prev()
            self.current_instrument_preset_idx = len(self.get_current_instrument().presets) - 1
        else:
            self.current_instrument_preset_idx -= 1
