from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.midi.program_change import ProgramChange
from pi_pianoteq.config.config import Config

from typing import List, Optional, TYPE_CHECKING
from time import sleep
from os import system
import logging

if TYPE_CHECKING:
    from pi_pianoteq.rpc.jsonrpc_client import PianoteqJsonRpc

logger = logging.getLogger(__name__)

class ClientLib(ClientApi):

    def __init__(self, instrument_library: Library, selector: Selector, program_change: ProgramChange, jsonrpc: Optional['PianoteqJsonRpc'] = None):
        self.program_change = program_change
        self.instrument_library = instrument_library
        self.selector = selector
        self.on_exit = None
        self.sync_with_pianoteq(jsonrpc)

    def sync_with_pianoteq(self, jsonrpc: Optional['PianoteqJsonRpc']) -> None:
        """
        Sync selector state with Pianoteq's current preset.

        If the current preset in Pianoteq matches one in our library, set it as current.
        Otherwise, reset to the first preset (old behavior).
        """
        sleep(Config.MIDI_PIANOTEQ_STARTUP_DELAY)

        if jsonrpc is None:
            logger.warning("No JSON-RPC client provided, resetting to first preset")
            self.program_change.set_preset(self.selector.get_current_preset())
            return

        try:
            info = jsonrpc.get_info()
            current_preset_info = info.get('current_preset', {})
            preset_name = current_preset_info.get('name', '')

            if not preset_name:
                logger.warning("Could not get current preset name from Pianoteq, resetting to first preset")
                self.program_change.set_preset(self.selector.get_current_preset())
                return

            logger.info(f"Pianoteq current preset: {preset_name}")

            result = self.instrument_library.find_preset_by_name(preset_name)
            if result is not None:
                instrument, preset = result
                if self.selector.set_preset_by_name(instrument.name, preset.name):
                    logger.info(f"Synced to current preset: {instrument.name} - {preset.name}")
                else:
                    logger.warning(f"Found preset '{preset_name}' but failed to set position, resetting to first preset")
                    self.program_change.set_preset(self.selector.get_current_preset())
            else:
                logger.info(f"Current preset '{preset_name}' not in library, resetting to first preset")
                self.program_change.set_preset(self.selector.get_current_preset())

        except Exception as e:
            logger.warning(f"Error syncing with Pianoteq: {e}, resetting to first preset")
            self.program_change.set_preset(self.selector.get_current_preset())

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
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_next(self) -> None:
        self.selector.set_instrument_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_prev(self) -> None:
        self.selector.set_instrument_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

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
        Uses MIDI Program Change to trigger Pianoteq preset load.
        """
        if self.selector.set_preset_by_name(instrument_name, preset_name):
            self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_next(self) -> None:
        self.selector.set_preset_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_prev(self) -> None:
        self.selector.set_preset_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    # Utility methods
    def set_on_exit(self, on_exit) -> None:
        self.on_exit = on_exit

    def shutdown_device(self) -> None:
        logger.info("Client requested shutdown")
        if self.on_exit is not None:
            self.on_exit()
        system(Config.SHUTDOWN_COMMAND)
