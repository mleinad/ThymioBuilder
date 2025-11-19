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
        pass
    
    @abstractmethod
    def set_path(self, path):
        pass
    
    @abstractmethod
    def set_grid(self, grid):
        pass
