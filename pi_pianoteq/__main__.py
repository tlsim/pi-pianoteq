import argparse
import logging
import sys
import time

from pi_pianoteq.config import (
    Config,
    ConfigLoader,
    USER_CONFIG_PATH,
    BUNDLED_CONFIG_PATH
)

from pi_pianoteq.logging_config import setup_logging

logger = logging.getLogger(__name__)


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
        '--cli',
        action='store_true',
        help='Use CLI client instead of GFX HAT client (for development/testing)'
    )
    parser.add_argument(
        '--include-demo',
        action='store_true',
        help='Include demo instruments (with limited functionality)'
    )

    args = parser.parse_args()

    # Handle special commands
    if args.show_config:
        show_config()
        return 0

    if args.init_config:
        return init_config()

    # Initialize logging for normal operation
    setup_logging()

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

    # Instantiate client early (in loading mode, api=None)
    if args.cli:
        client = CliClient(api=None)
    else:
        client = GfxhatClient(api=None)

    pianoteq = Pianoteq()

    logger.info("Pianoteq version: %s", pianoteq.get_version())

    # Start Pianoteq with loading feedback
    client.show_loading_message("Starting Pianoteq...")
    pianoteq.start()

    # Discover instruments via JSON-RPC API with retry logic
    from pi_pianoteq.jsonrpc_client import PianoteqJsonRpc, PianoteqJsonRpcError
    client.show_loading_message("Connecting to API...")

    jsonrpc = PianoteqJsonRpc()
    instruments = []
    last_count = 0
    stable_count = 0
    api_connected = False

    for attempt in range(8):
        try:
            instruments = Config.discover_instruments_from_api(jsonrpc, include_demo=args.include_demo, skip_fallback=True)
            current_count = len(instruments)

            # Show "Loading..." once API connects
            if not api_connected:
                api_connected = True
                client.show_loading_message("Loading...")

            if current_count > 0 and current_count == last_count:
                stable_count += 1
                if stable_count >= 2:
                    logger.info(f"Discovered {current_count} instruments from Pianoteq API")
                    break
            else:
                stable_count = 0

            last_count = current_count

            if attempt < 7:
                time.sleep(0.5)
        except Exception as e:
            if attempt < 7:
                time.sleep(0.5)
            else:
                logger.error(f"Failed to connect after 8 attempts: {e}")
    if not instruments:
        print("No licensed instruments found after retries, trying with demos...")
        instruments = Config.discover_instruments_from_api(jsonrpc, include_demo=True)

    # Check if we successfully discovered any instruments
    if not instruments:
        print("ERROR: No instruments discovered from Pianoteq API!")
        print()
        print("This usually means:")
        print("  1. Pianoteq failed to start or crashed during startup")
        print("  2. Pianoteq's --serve flag didn't enable the JSON-RPC server")
        print("  3. No instruments are licensed (all show as 'demo' status)")
        print()
        print("Please check the logs above for error messages.")
        pianoteq.terminate()
        return 1

    # Build library with discovered instruments (already grouped with presets)
    library = Library(instruments)
    selector = Selector(library.get_instruments())
    mapping = MappingBuilder(library).build()
    Writer(mapping).write()

    midiout = MidiOut()
    midiout.open_virtual_port(Config.MIDI_PORT_NAME)
    program_change = ProgramChange(midiout)

    client_lib = ClientLib(library, selector, program_change)

    # Give Pianoteq a bit more time to detect the virtual MIDI port and update its prefs
    time.sleep(2)

    # Check if PI-PTQ MIDI device is enabled in Pianoteq preferences
    if not is_midi_device_enabled(Config.PIANOTEQ_PREFS_FILE):
        logger.warning(
            "PI-PTQ MIDI port not enabled in Pianoteq. "
            "Please enable it in Pianoteq preferences: "
            "Edit → Preferences → Devices, then enable 'PI-PTQ' under Active MIDI Inputs. "
            "You may need to restart the service after enabling the port."
        )

        # Only wait for keypress in CLI mode (not in headless/systemd service)
        if args.cli:
            # Also print to console in CLI mode for immediate visibility
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
            input("Press Enter to continue...")
            print()

    # Transition from loading to normal operation
    client.clear_loading_screen()

    # Provide API and start normal operation
    client.set_api(client_lib)
    client.start()
    pianoteq.terminate()

    return 0


if __name__ == '__main__':
    sys.exit(main())
