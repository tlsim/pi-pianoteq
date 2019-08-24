from abc import ABC, abstractmethod
from client.ClientApi import ClientApi


class Client(ABC):

    @abstractmethod
    def __init__(self, api: ClientApi):
        self.api = api

    @abstractmethod
    def start(self):
        raise NotImplemented
