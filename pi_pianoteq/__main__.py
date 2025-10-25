import argparse
import sys
import time

from pi_pianoteq.config import (
    Config,
    ConfigLoader,
    USER_CONFIG_PATH,
    BUNDLED_CONFIG_PATH,
    USER_INSTRUMENTS_PATH,
    BUNDLED_INSTRUMENTS_PATH
)


def show_config():
    """Display current configuration and sources"""
    print("Pi-Pianoteq Configuration")
    print("=" * 60)
    print()

    # Show config file locations
    print("Config file locations:")
    print(f"  User config:     {USER_CONFIG_PATH}")
    print(f"                   {'[exists]' if USER_CONFIG_PATH.exists() else '[not found]'}")
    print(f"  Bundled default: {BUNDLED_CONFIG_PATH}")
    print()

    # Show instruments file locations
    print("Instruments file locations:")
    print(f"  User instruments: {USER_INSTRUMENTS_PATH}")
    print(f"                    {'[exists - using this]' if USER_INSTRUMENTS_PATH.exists() else '[not found]'}")
    print(f"  Bundled default:  {BUNDLED_INSTRUMENTS_PATH}")
    print()

    # Show current values and their sources
    print("Current configuration (source in brackets):")
    print()
    sources = Config.get_config_sources()

    configs = [
        ("PIANOTEQ_DIR", Config.PIANOTEQ_DIR),
        ("PIANOTEQ_BIN", Config.PIANOTEQ_BIN),
        ("PIANOTEQ_DATA_DIR", Config.PIANOTEQ_DATA_DIR),
        ("PIANOTEQ_MIDI_MAPPINGS_DIR", Config.PIANOTEQ_MIDI_MAPPINGS_DIR),
        ("PIANOTEQ_PREFS_FILE", Config.PIANOTEQ_PREFS_FILE),
        ("PIANOTEQ_HEADLESS", Config.PIANOTEQ_HEADLESS),
        ("MIDI_PORT_NAME", Config.MIDI_PORT_NAME),
        ("MIDI_MAPPING_NAME", Config.MIDI_MAPPING_NAME),
        ("MIDI_PIANOTEQ_STARTUP_DELAY", Config.MIDI_PIANOTEQ_STARTUP_DELAY),
        ("SHUTDOWN_COMMAND", Config.SHUTDOWN_COMMAND),
    ]

    for key, value in configs:
        source = sources.get(key, 'unknown')
        print(f"  {key:30} = {value}")
        print(f"  {' ' * 30}   [{source}]")
        print()

    print("Priority order: environment > user_config > bundled_default")


def init_config():
    """Initialize user config file"""
    success, message = ConfigLoader.init_user_config()
    print(message)
    if success:
        print()
        print(f"Edit your configuration at: {USER_CONFIG_PATH}")
        print("Then restart pi_pianoteq for changes to take effect.")
    return 0 if success else 1


def init_instruments():
    """Initialize user instruments file"""
    success, message = ConfigLoader.init_user_instruments()
    print(message)
    if success:
        print()
        print("Customize which instruments appear in the interface by editing:")
        print(f"  {USER_INSTRUMENTS_PATH}")
        print()
        print("You can:")
        print("  - Remove instruments you don't own")
        print("  - Reorder instruments by preference")
        print("  - Customize backlight colors")
        print()
        print("See README.md for details on the file format and prefix matching.")
        print()
        print("Restart pi_pianoteq for changes to take effect.")
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(
        description="Pi-Pianoteq: Python/MIDI remote control for Pianoteq"
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Display current configuration and exit'
    )
    parser.add_argument(
        '--init-config',
        action='store_true',
        help='Initialize user config file at ~/.config/pi_pianoteq/ and exit'
    )
    parser.add_argument(
        '--init-instruments',
        action='store_true',
        help='Initialize user instruments.json file at ~/.config/pi_pianoteq/ and exit'
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Use CLI client instead of GFX HAT client (for development/testing)'
    )

    args = parser.parse_args()

    # Handle special commands
    if args.show_config:
        show_config()
        return 0

    if args.init_config:
        return init_config()

    if args.init_instruments:
        return init_instruments()

    # Normal startup - import hardware dependencies only when needed
    from rtmidi import MidiOut
    from pi_pianoteq.instrument.Library import Library
    from pi_pianoteq.instrument.Selector import Selector
    from pi_pianoteq.lib.ClientLib import ClientLib
    from pi_pianoteq.mapping.MappingBuilder import MappingBuilder
    from pi_pianoteq.mapping.Writer import Writer
    from pi_pianoteq.midi.ProgramChange import ProgramChange
    from pi_pianoteq.process.Pianoteq import Pianoteq
    from pi_pianoteq.util.pianoteq_prefs import is_midi_device_enabled

    # Import appropriate client based on mode
    if args.cli:
        from pi_pianoteq.client.cli.CliClient import CliClient
    else:
        from pi_pianoteq.client.gfxhat.GfxhatClient import GfxhatClient

    pianoteq = Pianoteq()
    library = Library(pianoteq.get_presets(), Config.load_instruments())
    selector = Selector(library.get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

    print(pianoteq.get_version())

    pianoteq.start()

    midiout = MidiOut()
    midiout.open_virtual_port(Config.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    client_lib = ClientLib(library, selector, program_change)

    # Give Pianoteq time to detect the virtual MIDI port and update its prefs
    time.sleep(2)

    # Check if PI-PTQ MIDI device is enabled in Pianoteq preferences
    if not is_midi_device_enabled(Config.PIANOTEQ_PREFS_FILE):
        print("⚠️  WARNING: PI-PTQ MIDI port not enabled in Pianoteq")
        print()
        print("Please enable it in Pianoteq preferences:")
        print("  1. With pi_pianoteq running, open Pianoteq")
        print("  2. Go to Edit → Preferences → Devices")
        print("  3. Enable the checkbox next to \"PI-PTQ\" under Active MIDI Inputs")
        print("  4. Click OK")
        print()
        print("Note: You may need to restart the service after enabling the port.")
        print()
        print("Continuing anyway (preset/instrument changes won't work until configured)...")
        print()

        # Only wait for keypress in CLI mode (not in headless/systemd service)
        if args.cli:
            input("Press Enter to continue...")
            print()

    if args.cli:
        client = CliClient(client_lib)
    else:
        client = GfxhatClient(client_lib)

    client.start()
    pianoteq.terminate()

    return 0


if __name__ == '__main__':
    sys.exit(main())
