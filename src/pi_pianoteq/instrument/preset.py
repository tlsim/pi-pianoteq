from typing import Optional


class Preset:
    def __init__(self, name: str, display_name: Optional[str] = None):
        """
        Create a Preset instance.

        Args:
            name: The full preset name from Pianoteq API
            display_name: The formatted name for display (computed during library construction)
        """
        self.name = name
        self.display_name = display_name or name
        self.midi_program_number: Optional[int] = None
        self.midi_channel: Optional[int] = None

    def has_midi_params(self) -> bool:
        return self.midi_program_number is not None and \
               self.midi_channel is not None
