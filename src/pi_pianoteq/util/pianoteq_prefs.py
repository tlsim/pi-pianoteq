import xml.etree.ElementTree as ET
from pathlib import Path


def is_midi_device_enabled(prefs_file_path: str, device_name: str = "PI-PTQ") -> bool:
    """
    Check if a MIDI device is enabled in Pianoteq preferences.

    Args:
        prefs_file_path: Path to Pianoteq .prefs file
        device_name: Name of MIDI device to check for (default: "PI-PTQ")

    Returns:
        True if device is enabled, False otherwise
    """
    prefs_path = Path(prefs_file_path).expanduser()

    if not prefs_path.exists():
        return False

    try:
        tree = ET.parse(prefs_path)
        root = tree.getroot()

        # Find midi-setup element
        midi_setup = root.find('.//VALUE[@name="midi-setup"]/midi-setup')
        if midi_setup is None:
            return False

        # Check if device with specified name exists
        device = midi_setup.find(f'.//device[@name="{device_name}"]')
        return device is not None

    except (ET.ParseError, OSError):
        # If we can't parse the file, assume device is not enabled
        return False
