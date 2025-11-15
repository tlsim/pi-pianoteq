from typing import List, Dict
import logging

from pi_pianoteq.instrument.instrument import Instrument
from pi_pianoteq.instrument.preset import Preset

logger = logging.getLogger(__name__)


class Library:
    def __init__(self, instruments: List[Instrument]):
        """
        Initialize Library with pre-grouped instruments.

        Args:
            instruments: List of Instrument objects with presets already added
                        (typically from Config.discover_instruments_from_api())
        """
        self.instruments: List[Instrument] = instruments

    def get_instruments(self) -> List[Instrument]:
        return [i for i in self.instruments if len(i.presets) > 0]

    def find_preset_by_name(self, preset_name: str) -> tuple[Instrument, Preset] | None:
        """
        Find a preset by name across all instruments.

        Args:
            preset_name: The exact preset name to search for

        Returns:
            Tuple of (Instrument, Preset) if found, None otherwise
        """
        for instrument in self.get_instruments():
            for preset in instrument.presets:
                if preset.name == preset_name:
                    return (instrument, preset)
        return None
