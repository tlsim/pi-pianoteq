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
    def get_current_preset(self) -> str:
        raise NotImplemented

    @abstractmethod
    def get_current_preset_display_name(self) -> str:
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
    def get_instrument_names(self):
        raise NotImplemented

    @abstractmethod
    def get_current_instrument(self) -> str:
        raise NotImplemented

    @abstractmethod
    def get_current_background_primary(self) -> str:
        raise NotImplemented

    @abstractmethod
    def get_current_background_secondary(self) -> str:
        raise NotImplemented

    @abstractmethod
    def shutdown_device(self):
        raise NotImplemented

    @abstractmethod
    def set_on_exit(self, on_exit) -> None:
        raise NotImplemented
