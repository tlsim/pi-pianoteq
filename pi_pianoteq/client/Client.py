from abc import ABC, abstractmethod
from typing import Optional

from pi_pianoteq.client.ClientApi import ClientApi


class Client(ABC):
    """
    Base class for Pi-Pianoteq clients.

    Supports two-phase initialization for loading screen functionality:
    1. Instantiate with api=None to show loading messages during startup
    2. Call set_api() when ClientLib is ready
    3. Call start() to begin normal operation
    """

    @abstractmethod
    def __init__(self, api: Optional[ClientApi]):
        self.api = api

    @abstractmethod
    def set_api(self, api: ClientApi):
        """
        Provide the ClientApi after initialization.
        Called once instruments are discovered and ClientLib is created.
        """
        raise NotImplemented

    @abstractmethod
    def show_loading_message(self, message: str):
        """
        Display a loading message during startup.
        Called before api is available.
        """
        raise NotImplemented

    @abstractmethod
    def clear_loading_screen(self):
        """
        Clear the loading screen and prepare for normal operation.
        Called after api is provided and before transitioning to normal UI.
        """
        raise NotImplemented

    @abstractmethod
    def start(self):
        """
        Start normal client operation.
        Called after set_api() and clear_loading_screen().
        """
        raise NotImplemented
