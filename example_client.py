"""
Example minimal external client for Pi-Pianoteq.

This demonstrates the minimum required implementation for a custom client.
You can test it with: pi-pianoteq --client example_client:ExampleClient
"""
from typing import Optional
import logging

from pi_pianoteq.client.client import Client
from pi_pianoteq.client.client_api import ClientApi


class ExampleClient(Client):
    """
    Minimal example client that prints to console.

    Demonstrates the basic structure for a custom client.
    """

    def __init__(self, api: Optional[ClientApi]):
        """Initialize the client in loading mode (api=None)"""
        super().__init__(api)
        print("ExampleClient initialized")

    def set_api(self, api: ClientApi):
        """Called when the API becomes available"""
        self.api = api
        print(f"ExampleClient: API ready with {len(api.get_instruments())} instruments")

    def show_loading_message(self, message: str):
        """Display loading messages during startup"""
        print(f"[LOADING] {message}")

    def start(self):
        """Main client loop - called after set_api()"""
        print("\nExampleClient started!")
        print("=" * 60)

        # Show current state
        instrument = self.api.get_current_instrument()
        preset = self.api.get_current_preset()
        print(f"Current: {instrument.name} - {preset.name}")

        # List available instruments
        print(f"\nAvailable instruments ({len(self.api.get_instruments())}):")
        for i, instr in enumerate(self.api.get_instruments(), 1):
            print(f"  {i}. {instr.name}")

        print("\nPress Ctrl+C to exit")

        # Simple loop - just wait for interrupt
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExampleClient shutting down...")

    def get_logging_handler(self) -> Optional[logging.Handler]:
        """Return None to use default stdout/stderr logging"""
        return None
