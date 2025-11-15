from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.config.config import Config
from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpc

from typing import List
from os import system
import logging

logger = logging.getLogger(__name__)

class ClientLib(ClientApi):

    def __init__(self, instrument_library: Library, selector: Selector, jsonrpc: PianoteqJsonRpc):
        self.jsonrpc = jsonrpc
        self.instrument_library = instrument_library
        self.selector = selector
        self.on_exit = None
        self.sync_preset()

    def sync_preset(self) -> None:
        """
        Sync selector position with Pianoteq's current preset.

        If the current preset in Pianoteq matches one in our library, set it as current.
        Otherwise, reset to the first preset (old behavior).
        """

        try:
            info = self.jsonrpc.get_info()
            preset_name = info.current_preset.name

            if not preset_name:
                logger.warning("Could not get current preset name from Pianoteq, resetting to first preset")
                preset = self.selector.get_current_preset()
                self._apply_preset(preset)
                return

            logger.info(f"Pianoteq current preset: {preset_name}")

            result = self.instrument_library.find_preset_by_name(preset_name)
            if result is not None:
                instrument, preset = result
                if self.selector.set_preset_by_name(instrument.name, preset.name):
                    logger.info(f"Synced to current preset: {instrument.name} - {preset.name}")
                else:
                    logger.warning(f"Found preset '{preset_name}' but failed to set position, resetting to first preset")
                    preset = self.selector.get_current_preset()
                    self._apply_preset(preset)
            else:
                logger.info(f"Current preset '{preset_name}' not in library, resetting to first preset")
                preset = self.selector.get_current_preset()
                self._apply_preset(preset)

        except Exception as e:
            logger.warning(f"Error syncing with Pianoteq: {e}, resetting to first preset")
            preset = self.selector.get_current_preset()
            self._apply_preset(preset)

    # Instrument getters
    def get_instruments(self) -> list:
        """Get list of all Instrument objects."""
        return self.instrument_library.get_instruments()

    def get_current_instrument(self):
        """Get the current Instrument object."""
        return self.selector.get_current_instrument()

    # Instrument setters
    def set_instrument(self, name) -> None:
        self.selector.set_instrument(name)
        preset = self.selector.get_current_preset()
        self._apply_preset(preset)

    def set_instrument_next(self) -> None:
        self.selector.set_instrument_next()
        preset = self.selector.get_current_preset()
        self._apply_preset(preset)

    def set_instrument_prev(self) -> None:
        self.selector.set_instrument_prev()
        preset = self.selector.get_current_preset()
        self._apply_preset(preset)

    # Preset getters
    def get_presets(self, instrument_name: str) -> list:
        """Get list of Preset objects for a specific instrument."""
        instrument = self.selector.get_instrument_by_name(instrument_name)
        return instrument.presets if instrument else []

    def get_current_preset(self):
        """Get the current Preset object."""
        return self.selector.get_current_preset()

    # Preset setters
    def set_preset(self, instrument_name: str, preset_name: str):
        """
        Set specific preset for a specific instrument.

        Switches to the instrument if not current, then loads the preset.
        Uses JSON-RPC to load the preset in Pianoteq.
        """
        if self.selector.set_preset_by_name(instrument_name, preset_name):
            preset = self.selector.get_current_preset()
            self._apply_preset(preset)

    def set_preset_next(self) -> None:
        self.selector.set_preset_next()
        preset = self.selector.get_current_preset()
        self._apply_preset(preset)

    def set_preset_prev(self) -> None:
        self.selector.set_preset_prev()
        preset = self.selector.get_current_preset()
        self._apply_preset(preset)

    def _apply_preset(self, preset: 'Preset') -> None:
        """
        Apply a preset, handling both regular presets and special randomize preset.

        When applying the Randomise preset, ensures we switch to the correct
        instrument first (if needed) before randomizing parameters.

        Args:
            preset: The preset to apply
        """
        if preset.name == "__RANDOMISE__":
            logger.info("Randomizing parameters")

            # Get current instrument from selector
            current_instrument = self.selector.get_current_instrument()

            # Check if we need to switch instruments first
            try:
                info = self.jsonrpc.get_info()
                pianoteq_instrument = info.current_preset.instrument

                # If we're switching instruments, load a real preset first
                if pianoteq_instrument != current_instrument.name:
                    # Load the first non-randomise preset
                    first_preset = current_instrument.presets[0]
                    logger.info(f"Switching to {current_instrument.name} before randomizing")
                    self.jsonrpc.load_preset(first_preset.name)
            except Exception as e:
                logger.warning(f"Could not check current instrument, loading first preset: {e}")
                # Fallback: always load first preset to ensure we're on right instrument
                first_preset = current_instrument.presets[0]
                self.jsonrpc.load_preset(first_preset.name)

            # Now randomize the parameters
            self.jsonrpc.randomize_parameters()
        else:
            self.jsonrpc.load_preset(preset.name)

    # Utility methods
    def set_on_exit(self, on_exit) -> None:
        self.on_exit = on_exit

    def shutdown_device(self) -> None:
        logger.info("Client requested shutdown")
        if self.on_exit is not None:
            self.on_exit()
        system(Config.SHUTDOWN_COMMAND)
