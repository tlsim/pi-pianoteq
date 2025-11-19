from abc import ABC, abstractmethod


class ClientApi(ABC):
    @classmethod
    def version(cls) -> str:
        return '1.0.0'

    @abstractmethod
    def set_preset_next(self):
        raise NotImplemented

    @abstractmethod
    def set_preset_prev(self):
        raise NotImplemented

    @abstractmethod
    def get_current_preset(self):
        """Get the current Preset object."""
        raise NotImplemented

    @abstractmethod
    def set_instrument_next(self):
        raise NotImplemented

    @abstractmethod
    def set_instrument_prev(self):
        raise NotImplemented

    @abstractmethod
    def set_instrument(self, name):
        raise NotImplemented

    @abstractmethod
    def get_instruments(self) -> list:
        """Get list of all Instrument objects."""
        raise NotImplemented

    @abstractmethod
    def get_current_instrument(self):
        """Get the current Instrument object."""
        raise NotImplemented

    @abstractmethod
    def shutdown_device(self):
        raise NotImplemented

    @abstractmethod
    def set_on_exit(self, on_exit) -> None:
        raise NotImplemented

    @abstractmethod
    def get_presets(self, instrument_name: str) -> list:
        """Get list of Preset objects for a specific instrument."""
        raise NotImplemented

    @abstractmethod
    def set_preset(self, instrument_name: str, preset_name: str):
        raise NotImplemented

    @abstractmethod
    def randomize_current_preset(self):
        """Randomize parameters of the current preset."""
        raise NotImplemented

    @abstractmethod
    def randomize_instrument_and_preset(self):
        """Randomly select an instrument and randomize its parameters."""
        raise NotImplemented
