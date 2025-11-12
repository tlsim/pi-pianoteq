from typing import List
from pi_pianoteq.instrument.instrument import Instrument, Preset


class Selector:
    def __init__(self, instruments):
        self.instruments: List[Instrument] = instruments
        self.current_instrument_idx: int = 0
        self.current_instrument_preset_idx: int = 0

    def get_instrument_by_name(self, name: str) -> Instrument | None:
        """Find instrument by name."""
        return next((i for i in self.instruments if i.name == name), None)

    def get_current_instrument(self) -> Instrument:
        return self.instruments[self.current_instrument_idx]

    def set_instrument_next(self) -> None:
        self.current_instrument_idx = (self.current_instrument_idx + 1) % len(self.instruments)
        self.current_instrument_preset_idx = 0

    def set_instrument_prev(self) -> None:
        self.current_instrument_idx = (self.current_instrument_idx - 1) % len(self.instruments)
        self.current_instrument_preset_idx = 0

    def set_instrument(self, name) -> None:
        instrument = self.get_instrument_by_name(name)
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

    def set_preset_by_name(self, instrument_name: str, preset_name: str) -> bool:
        """
        Set preset by instrument and preset name.

        Returns True if successful, False if instrument or preset not found.
        """
        instrument = self.get_instrument_by_name(instrument_name)
        if not instrument:
            return False

        preset = next((p for p in instrument.presets if p.name == preset_name), None)
        if not preset:
            return False

        self.current_instrument_idx = self.instruments.index(instrument)
        self.current_instrument_preset_idx = instrument.presets.index(preset)
        return True

    def set_position_from_objects(self, instrument: Instrument, preset: Preset) -> bool:
        """
        Set position from Instrument and Preset objects.

        Returns True if successful, False if instrument or preset not found in library.
        """
        try:
            self.current_instrument_idx = self.instruments.index(instrument)
            self.current_instrument_preset_idx = instrument.presets.index(preset)
            return True
        except ValueError:
            return False
