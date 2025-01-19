from abc import ABC, abstractmethod


class ScreenInterface(ABC):

    @abstractmethod
    def __init__(self, manager):
        self.manager = manager

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_exit(self):
        pass
