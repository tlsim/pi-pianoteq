from typing import List

from pi_pianoteq.instrument.preset import Preset


class Instrument:
    """
    Represents a Pianoteq instrument with its presets and UI colors.

    An instrument is a collection of related presets (e.g., "D4 Grand Piano"
    contains presets like "Close Mic", "Classical", etc.).

    Attributes:
        name (str): Full display name (e.g., "D4 Grand Piano")
        preset_prefix (str): Short prefix for grouping (e.g., "D4")
        background_primary (str): Hex color for UI elements (e.g., "#1e3a5f")
        background_secondary (str): Hex color for gradients (e.g., "#0f1d2f")
        presets (List[Preset]): List of available presets for this instrument
    """

    def __init__(self, name: str, preset_prefix: str, bg_primary: str, bg_secondary: str):
        """
        Create an Instrument instance.

        Args:
            name (str): Full display name of the instrument
            preset_prefix (str): Short prefix used to group presets
            bg_primary (str): Primary background color (hex format)
            bg_secondary (str): Secondary background color (hex format)
        """
        self.name = name
        self.preset_prefix = preset_prefix
        self.background_primary = bg_primary
        self.background_secondary = bg_secondary
        self.presets: List[Preset] = []

    def add_preset(self, preset: Preset):
        """
        Add a preset to this instrument.

        Args:
            preset (Preset): The preset to add

        Note:
            This is typically called during instrument discovery, not by
            client code.
        """
        self.presets.append(preset)
