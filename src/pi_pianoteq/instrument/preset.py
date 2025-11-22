from typing import Optional


class Preset:
    def __init__(self, name: str, display_name: Optional[str] = None, modified: bool = False):
        """
        Create a Preset instance.

        Args:
            name: The full preset name from Pianoteq API
            display_name: The formatted name for display (computed during library construction)
            modified: Whether the preset has been modified from its saved state
        """
        self.name = name
        self.display_name = display_name or name
        self.modified = modified

    def get_display_name_with_modified(self) -> str:
        """
        Get display name with (modified) suffix if preset has been modified.

        Returns:
            Display name, with " (modified)" appended if modified=True
        """
        if self.modified:
            return f"{self.display_name} (modified)"
        return self.display_name
