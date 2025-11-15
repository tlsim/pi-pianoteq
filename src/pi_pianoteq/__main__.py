import argparse
import atexit
import logging
import signal
import sys
import time

from pi_pianoteq.config.config import (
    Config,
    ConfigLoader,
    USER_CONFIG_PATH,
    BUNDLED_CONFIG_PATH
)

from pi_pianoteq.logging.logging_config import setup_logging

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
        ("PIANOTEQ_HEADLESS", Config.PIANOTEQ_HEADLESS),
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

    # Normal startup - import hardware dependencies only when needed
    from pi_pianoteq.instrument.library import Library
    from pi_pianoteq.instrument.selector import Selector
    from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpc, PianoteqJsonRpcError
    from pi_pianoteq.lib.client_lib import ClientLib
    from pi_pianoteq.process.pianoteq import Pianoteq

    # Import appropriate client based on mode
    if args.cli:
        from pi_pianoteq.client.cli.cli_client import CliClient
    else:
        from pi_pianoteq.client.gfxhat.gfxhat_client import GfxhatClient

    # Instantiate client early (in loading mode, api=None)
    if args.cli:
        client = CliClient(api=None)
    else:
        client = GfxhatClient(api=None)

    # Setup logging - use buffered handler for CLI mode
    log_buffer = client.log_buffer if args.cli else None
    setup_logging(cli_mode=args.cli, log_buffer=log_buffer)

    pianoteq = Pianoteq()

    logger.info("Pianoteq version: %s", pianoteq.get_version())

    # Start Pianoteq and wait for API
    client.show_loading_message("Starting Pianoteq...")
    pianoteq.start()

    jsonrpc = PianoteqJsonRpc()
    pianoteq.jsonrpc_client = jsonrpc

    # Register cleanup handlers
    def cleanup_handler(signum=None, frame=None):
        logger.info("Shutting down pi-pianoteq...")
        pianoteq.quit()
        sys.exit(0)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)

    # Register atexit handler for cleanup on normal exit
    atexit.register(lambda: pianoteq.quit())
    instruments = []
    last_count = 0
    stable_count = 0
    api_connected = False
    is_licensed = False

    # First, wait for API to be available and check license status
    for attempt in range(8):
        try:
            is_licensed = jsonrpc.is_licensed()
            api_connected = True
            logger.info(f"Pianoteq license status: {'Licensed' if is_licensed else 'Demo/Trial'}")
            break
        except Exception as e:
            if attempt < 7:
                time.sleep(0.5)
            else:
                logger.error(f"Failed to connect to API after 8 attempts: {e}")
                # If we can't connect at all, can't proceed
                print("ERROR: Could not connect to Pianoteq JSON-RPC API!")
                pianoteq.quit()
                return 1

    client.show_loading_message("Loading...")

    # Discover instruments based on license status
    if is_licensed:
        # Licensed version - get licensed instruments
        instruments = Config.discover_instruments_from_api(jsonrpc, include_demo=args.include_demo, skip_fallback=True)
        logger.info(f"Discovered {len(instruments)} licensed instruments from Pianoteq API")
    else:
        # Demo/trial version - use demo instruments
        logger.info("Demo/trial version detected, loading with demo instruments...")
        instruments = Config.discover_instruments_from_api(jsonrpc, include_demo=True)
        logger.info(f"Discovered {len(instruments)} demo instruments from Pianoteq API")

    # Check if we successfully discovered any instruments
    if not instruments:
        logger.error("No instruments discovered from Pianoteq API!")
        logger.error("This usually means:")
        logger.error("  1. Pianoteq failed to start or crashed during startup")
        logger.error("  2. Pianoteq's --serve flag didn't enable the JSON-RPC server")
        logger.error("  3. No instruments are licensed (all show as 'demo' status)")
        logger.error("Please check the logs for error messages.")
        pianoteq.quit()
        return 1

    # Build library with discovered instruments (already grouped with presets)
    library = Library(instruments)
    selector = Selector(library.get_instruments())

    client_lib = ClientLib(library, selector, jsonrpc)

    # Provide API and start normal operation
    client.set_api(client_lib)
    client.start()
    pianoteq.quit()

    return 0


if __name__ == '__main__':
    sys.exit(main())
