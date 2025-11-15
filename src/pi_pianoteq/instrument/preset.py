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
