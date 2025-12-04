# robot_interface.py
from abc import ABC, abstractmethod


class RobotInterface(ABC):

    @abstractmethod
    def move_forward(self):
        """Moves the robot one grid cell forward."""
        pass

    @abstractmethod
    def move_backward(self):
        """Moves the robot one grid cell backward."""
        pass

    @abstractmethod
    def rotate_left(self):
        """Rotates the robot 90 degrees left."""
        pass

    @abstractmethod
    def rotate_right(self):
        """Rotates the robot 90 degrees right."""
        pass

    @abstractmethod
    def find_block(self):
        """Rotates the robot 180 degrees."""
        pass

    @abstractmethod
    def get_position(self):
        """Returns pixel position + orientation (x, y, theta_radians)."""
        pass

    @abstractmethod
    def update(self, dt):
        """Updates and renders the simulator each frame."""
        pass

    @abstractmethod
    def set_path(self, path):
        """Stores a grid path for visualization (optional)."""
        pass

    @abstractmethod
    def set_grid(self, grid):
        """Sets the reference grid map used for movement."""
        pass
