from abc import ABC, abstractmethod


class ClientApi(ABC):
    """
    Abstract interface for controlling Pianoteq instruments and presets.

    This is the primary API that clients use to interact with the backend.
    All methods are thread-safe when called from a single thread. For
    multi-threaded clients, use external locking.
    """

    @classmethod
    def version(cls) -> str:
        """
        Get the ClientApi version.

        Returns:
            str: API version string (currently "1.0.0")
        """
        return '1.0.0'

    @abstractmethod
    def set_preset_next(self):
        """
        Switch to the next preset in the current instrument.

        Wraps around to the first preset when reaching the end.
        Sends MIDI Program Change to Pianoteq.
        """
        raise NotImplemented

    @abstractmethod
    def set_preset_prev(self):
        """
        Switch to the previous preset in the current instrument.

        Wraps around to the last preset when reaching the start.
        Sends MIDI Program Change to Pianoteq.
        """
        raise NotImplemented

    @abstractmethod
    def get_current_preset(self):
        """
        Get the currently loaded preset.

        Returns:
            Preset: The current preset object
        """
        raise NotImplemented

    @abstractmethod
    def set_instrument_next(self):
        """
        Switch to the next instrument.

        Wraps around to the first instrument when reaching the end.
        Also loads the first preset of the new instrument and sends
        MIDI Program Change to Pianoteq.
        """
        raise NotImplemented

    @abstractmethod
    def set_instrument_prev(self):
        """
        Switch to the previous instrument.

        Wraps around to the last instrument when reaching the start.
        Also loads the first preset of the new instrument and sends
        MIDI Program Change to Pianoteq.
        """
        raise NotImplemented

    @abstractmethod
    def set_instrument(self, name):
        """
        Switch to a specific instrument by name.

        Args:
            name (str): The full instrument name (e.g., "D4 Grand Piano")

        Also loads the first preset of the new instrument and sends
        MIDI Program Change to Pianoteq.
        """
        raise NotImplemented

    @abstractmethod
    def get_instruments(self) -> list:
        """
        Get list of all available instruments.

        Returns:
            list[Instrument]: All instruments discovered during startup
        """
        raise NotImplemented

    @abstractmethod
    def get_current_instrument(self):
        """
        Get the currently selected instrument.

        Returns:
            Instrument: The current instrument object
        """
        raise NotImplemented

    @abstractmethod
    def shutdown_device(self):
        """
        Trigger system shutdown.

        Calls registered exit callbacks, then executes the system shutdown
        command. This will shut down the entire device (e.g., Raspberry Pi).

        Warning:
            Only use this for hardware shutdown buttons. This will power
            off the system!
        """
        raise NotImplemented

    @abstractmethod
    def set_on_exit(self, on_exit) -> None:
        """
        Register a callback to run during shutdown.

        Args:
            on_exit (Callable[[], None]): Function to call before shutdown

        The callback will be invoked when shutdown_device() is called,
        before the actual system shutdown command executes.
        """
        raise NotImplemented

    @abstractmethod
    def get_presets(self, instrument_name: str) -> list:
        """
        Get list of presets for a specific instrument.

        Args:
            instrument_name (str): The full instrument name

        Returns:
            list[Preset]: List of preset objects, or empty list if
            instrument not found
        """
        raise NotImplemented

    @abstractmethod
    def set_preset(self, instrument_name: str, preset_name: str):
        """
        Load a specific preset for a specific instrument.

        If the instrument is not currently selected, switches to it first.
        Then loads the preset and sends MIDI Program Change to Pianoteq.

        Args:
            instrument_name (str): The full instrument name
            preset_name (str): The full preset name (use preset.name, not
                preset.display_name)
        """
        raise NotImplemented

    @abstractmethod
    def randomize_current_preset(self):
        """Randomize parameters of the current preset."""
        raise NotImplemented

    @abstractmethod
    def randomize_all(self):
        """Randomly select instrument and preset, then randomize parameters."""
        raise NotImplemented
