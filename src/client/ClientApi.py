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
