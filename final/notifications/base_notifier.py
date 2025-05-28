from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, user_id: str, message: str):
        pass