from typing import Optional
import re


class Preset:
    def __init__(self, name: str):
        self.name = name
        self.midi_program_number: Optional[int] = None
        self.midi_channel: Optional[int] = None

    def has_midi_params(self) -> bool:
        return self.midi_program_number is not None and \
               self.midi_channel is not None

    def get_display_name(self, instrument_prefix: str) -> str:
        """
        Get a formatted preset name for display, removing redundant instrument prefix.

        Strips the instrument prefix (case-insensitive) and any following separators,
        then capitalizes the first letter. Returns the original name if result would be empty.

        Args:
            instrument_prefix: The instrument's preset_prefix to strip

        Returns:
            Formatted preset name suitable for display

        Examples:
            "Steel Drum natural" with prefix "Steel Drum" → "Natural"
            "Hand Pan - foo" with prefix "Hand Pan" → "Foo"
            "Steel Drum" with prefix "Steel Drum" → "Steel Drum" (unchanged)
        """
        # Case-insensitive check if name starts with prefix
        if not self.name.lower().startswith(instrument_prefix.lower()):
            return self.name

        # Strip the prefix
        result = self.name[len(instrument_prefix):]

        # Strip common separators and whitespace from the start
        result = re.sub(r'^[\s\-—:|\u2013\u2014]+', '', result).strip()

        # Return original if nothing remains
        if not result:
            return self.name

        # Capitalize first letter
        return result[0].upper() + result[1:] if len(result) > 1 else result.upper()
