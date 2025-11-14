# robot_interface.py
from abc import ABC, abstractmethod

class RobotInterface(ABC):

    @abstractmethod
    def move_forward(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def update(self, dt):
        """Called every frame or tick (sim only)."""
        pass
