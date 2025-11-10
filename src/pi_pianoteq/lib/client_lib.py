from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.instrument.library import Library
from pi_pianoteq.instrument.selector import Selector
from pi_pianoteq.midi.program_change import ProgramChange
from pi_pianoteq.config.config import Config

from typing import List
from time import sleep
from os import system
import logging

logger = logging.getLogger(__name__)

class ClientLib(ClientApi):

    def __init__(self, instrument_library: Library, selector: Selector, program_change: ProgramChange):
        self.program_change = program_change
        self.instrument_library = instrument_library
        self.selector = selector
        self.reset_initial_preset()
        self.on_exit = None

    def reset_initial_preset(self) -> None:
        sleep(Config.MIDI_PIANOTEQ_STARTUP_DELAY)
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_next(self) -> None:
        self.selector.set_preset_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_preset_prev(self) -> None:
        self.selector.set_preset_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_next(self) -> None:
        self.selector.set_instrument_next()
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument(self, name) -> None:
        self.selector.set_instrument(name)
        self.program_change.set_preset(self.selector.get_current_preset())

    def set_instrument_prev(self) -> None:
        self.selector.set_instrument_prev()
        self.program_change.set_preset(self.selector.get_current_preset())

    def get_instrument_names(self) -> List[str]:
        return [i.name for i in self.instrument_library.get_instruments()]

    def get_current_preset(self) -> str:
        return self.selector.get_current_preset().name

    def get_current_preset_display_name(self) -> str:
        preset = self.selector.get_current_preset()
        instrument = self.selector.get_current_instrument()
        return preset.get_display_name(instrument.preset_prefix)

    def get_current_instrument(self) -> str:
        return self.selector.get_current_instrument().name

    def get_current_background_primary(self) -> str:
        return self.selector.get_current_instrument().background_primary

    def get_current_background_secondary(self) -> str:
        return self.selector.get_current_instrument().background_secondary

    def set_on_exit(self, on_exit) -> None:
        self.on_exit = on_exit

    def shutdown_device(self) -> None:
        logger.info("Client requested shutdown")
        if self.on_exit is not None:
            self.on_exit()
        system(Config.SHUTDOWN_COMMAND)

    def get_preset_names(self, instrument_name: str) -> List[str]:
        """Get list of preset names for a specific instrument."""
        instrument = self.selector.get_instrument_by_name(instrument_name)
        return [p.name for p in instrument.presets] if instrument else []

    def get_instrument_preset_prefix(self, instrument_name: str) -> str:
        """Get the preset prefix for a specific instrument."""
        instrument = self.selector.get_instrument_by_name(instrument_name)
        return instrument.preset_prefix if instrument else ""

    def set_preset(self, instrument_name: str, preset_name: str):
        """
        Set specific preset for a specific instrument.

        Switches to the instrument if not current, then loads the preset.
        Uses MIDI Program Change to trigger Pianoteq preset load.
        """
        if self.selector.set_preset_by_name(instrument_name, preset_name):
            self.program_change.set_preset(self.selector.get_current_preset())
